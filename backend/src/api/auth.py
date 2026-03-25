"""
Better Auth Integration

Provides session-based authentication middleware and dependencies
for protecting chat endpoints.

Author: Physical AI Platform Team
Date: 2026-02-12
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import httpx

from fastapi import Depends, HTTPException, status, Request, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..config import get_settings
from ..utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

# HTTP Bearer scheme for optional token extraction
bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class AuthenticatedUser:
    """Represents an authenticated user from Better Auth."""
    user_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    session_id: Optional[str] = None
    session_expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BetterAuthClient:
    """
    Client for validating sessions / OAuth tokens with the Better Auth server.

    Supports two validation strategies:
    1. OAuth Bearer token  → /api/auth/oauth2/userinfo  (new OIDC flow)
    2. Cookie session token → /api/auth/get-session     (legacy cookie flow)

    Strategy 1 is tried first for Bearer tokens; if it fails the token is
    treated as a legacy opaque session token and re-tried via strategy 2.
    """

    def __init__(self, auth_url: Optional[str] = None):
        self.auth_url = auth_url or getattr(settings, 'BETTER_AUTH_URL', 'http://localhost:3002')
        self.userinfo_endpoint = f"{self.auth_url}/api/auth/oauth2/userinfo"
        self.session_endpoint = f"{self.auth_url}/api/auth/get-session"

    async def _user_from_userinfo(self, data: dict) -> AuthenticatedUser:
        """Map OIDC userinfo response to AuthenticatedUser."""
        return AuthenticatedUser(
            user_id=data.get("sub") or data.get("id"),
            email=data.get("email"),
            name=data.get("name"),
            session_id=None,
            session_expires_at=None,
            metadata={
                "emailVerified": data.get("email_verified"),
                "role": data.get("role"),
                "onboardingCompleted": data.get("onboardingCompleted"),
            }
        )

    async def _user_from_session(self, data: dict) -> Optional[AuthenticatedUser]:
        """Map Better Auth get-session response to AuthenticatedUser."""
        if not data.get("user"):
            return None
        user_data = data["user"]
        session_data = data.get("session", {})
        return AuthenticatedUser(
            user_id=user_data.get("id"),
            email=user_data.get("email"),
            name=user_data.get("name"),
            session_id=session_data.get("id"),
            session_expires_at=(
                datetime.fromisoformat(session_data["expiresAt"])
                if session_data.get("expiresAt") else None
            ),
            metadata={
                "emailVerified": user_data.get("emailVerified"),
                "createdAt": user_data.get("createdAt"),
                "updatedAt": user_data.get("updatedAt"),
            }
        )

    async def validate_bearer_token(self, token: str) -> Optional[AuthenticatedUser]:
        """
        Validate an OAuth access token via the OIDC userinfo endpoint.
        Falls back to legacy session-cookie validation if userinfo returns 401.
        """
        try:
            async with httpx.AsyncClient() as client:
                # Strategy 1: OIDC userinfo (OAuth access tokens)
                resp = await client.get(
                    self.userinfo_endpoint,
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=5.0,
                )
                if resp.status_code == 200:
                    return await self._user_from_userinfo(resp.json())

                # Strategy 2: legacy opaque session token sent as cookie
                if resp.status_code in (401, 400):
                    resp2 = await client.get(
                        self.session_endpoint,
                        cookies={"physical-ai.session_token": token},
                        timeout=5.0,
                    )
                    if resp2.status_code == 200:
                        return await self._user_from_session(resp2.json())

                logger.warning(f"Bearer token validation failed: {resp.status_code}")
                return None

        except httpx.TimeoutException:
            logger.error("Auth server token validation timed out")
            return None
        except Exception as e:
            logger.error(f"Auth token validation error: {e}")
            return None

    async def validate_session_cookie(self, request: Request) -> Optional[AuthenticatedUser]:
        """Validate session from request cookies (legacy cookie flow)."""
        session_token = request.cookies.get("physical-ai.session_token")
        if not session_token:
            return None
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    self.session_endpoint,
                    cookies={"physical-ai.session_token": session_token},
                    timeout=5.0,
                )
                if resp.status_code == 200:
                    return await self._user_from_session(resp.json())
                return None
        except Exception as e:
            logger.error(f"Cookie session validation error: {e}")
            return None


# Singleton client instance
_auth_client: Optional[BetterAuthClient] = None


def get_auth_client() -> BetterAuthClient:
    """Get or create Better Auth client singleton."""
    global _auth_client
    if _auth_client is None:
        _auth_client = BetterAuthClient()
    return _auth_client


# ===========================================================================
# FastAPI Dependencies
# ===========================================================================

async def get_optional_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)
) -> Optional[AuthenticatedUser]:
    """
    Dependency: Get authenticated user if available, None otherwise.

    Checks both:
    1. Authorization: Bearer <token>  (OAuth access token via OIDC userinfo,
                                       with legacy opaque-session fallback)
    2. physical-ai.session_token cookie (legacy cookie sessions)

    Use this for endpoints that work with or without auth.
    """
    auth_client = get_auth_client()

    # Try Bearer token first (OAuth access tokens + legacy tokens)
    if credentials and credentials.credentials:
        user = await auth_client.validate_bearer_token(credentials.credentials)
        if user:
            return user

    # Fall back to cookie session
    return await auth_client.validate_session_cookie(request)


async def require_authenticated_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)
) -> AuthenticatedUser:
    """
    Dependency: Require an authenticated user.

    Raises 401 if not authenticated.

    Use this for protected endpoints.
    """
    user = await get_optional_user(request, credentials)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user


async def get_user_id_from_session(
    request: Request,
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)
) -> Optional[str]:
    """
    Dependency: Get user ID from auth or session header.

    Priority:
    1. Authenticated user ID (from Better Auth)
    2. X-Session-ID header (for anonymous users)

    Returns None if neither available.
    """
    # Try authenticated user first
    user = await get_optional_user(request, credentials)
    if user:
        return user.user_id

    # Fall back to session header
    return x_session_id


# ===========================================================================
# Middleware (Optional)
# ===========================================================================

class AuthMiddleware:
    """
    Optional middleware for request-level auth context.

    Attaches user info to request.state for access in routes.
    """

    def __init__(self, app):
        self.app = app
        self.auth_client = get_auth_client()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Create request from scope
        request = Request(scope)

        # Try to get user
        user = await self.auth_client.validate_session_cookie(request)

        # Attach to scope for access in request.state
        scope["state"] = getattr(scope, "state", {})
        scope["state"]["user"] = user

        await self.app(scope, receive, send)
