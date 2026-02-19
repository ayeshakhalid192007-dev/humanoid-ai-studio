"""
Personalization API Router - LEGACY (Routes through orchestrator)

Endpoints for generating and retrieving personalized chapter content.
Requires authentication via Better Auth session.

This endpoint has been migrated to route through the AI Orchestrator.
New implementations should use /api/ai/personalize instead.
Deprecation: This endpoint is deprecated and routes through the new architecture.

Author: Physical AI Platform Team
Date: 2026-02-16
"""
import httpx
from typing import Optional
from pydantic import BaseModel, Field

from fastapi import APIRouter, HTTPException, Request, Depends, status
from fastapi.responses import JSONResponse

from ..api.auth import require_authenticated_user, AuthenticatedUser
from ..api.validators import validate_slug
from ..config import get_settings
from ..db.neon_client import get_neon_client
from ..services.chapter_retriever import ChapterRetriever
from ..utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()
router = APIRouter(prefix="/api")

# Lazy-loaded service instances
_chapter_retriever: Optional[ChapterRetriever] = None


def _get_chapter_retriever() -> ChapterRetriever:
    global _chapter_retriever
    if _chapter_retriever is None:
        _chapter_retriever = ChapterRetriever()
    return _chapter_retriever


class PersonalizeRequest(BaseModel):
    chapter_slug: str = Field(..., description="Docusaurus doc slug")
    regenerate: bool = Field(default=False, description="Force regeneration")


async def get_orchestrator(request: Request):
    """
    Get the AI orchestrator instance from app.state.
    """
    if not hasattr(request.app.state, 'orchestrator'):
        raise HTTPException(status_code=500, detail="AI Orchestrator not initialized")

    return request.app.state.orchestrator


@router.post("/personalize", response_class=JSONResponse)
async def personalize_chapter(
    body: PersonalizeRequest,
    request: Request,
    user: AuthenticatedUser = Depends(require_authenticated_user),
):
    """Generate or retrieve personalized chapter content via AI Orchestrator."""
    # Create a deprecation header for this endpoint
    response = JSONResponse(
        content={},
        headers={
            "Deprecation": "true",
            "Link": '</api/ai/personalize>; rel="successor-version"',
        }
    )

    chapter_slug = validate_slug(body.chapter_slug)

    # Get orchestrator
    orchestrator = await get_orchestrator(request)

    # Check rate limit (using the new system)
    neon = await get_neon_client()
    is_allowed = await neon.check_ai_rate_limit(
        identifier=user.user_id,
        request_type="personalize",
        max_requests=settings.PERSONALIZE_RATE_LIMIT_MAX,
        window_hours=settings.AI_RATE_LIMIT_WINDOW_HOURS,
    )
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: {settings.PERSONALIZE_RATE_LIMIT_MAX} personalizations per hour.",
            headers={"Retry-After": "3600"},
        )

    # Fetch user profile from auth-server
    user_profile = await _fetch_user_profile(request)

    # Fetch chapter content to get content version
    content_version = ""
    if chapter_slug:
        from ..services.chapter_retriever import ChapterRetriever
        retriever = ChapterRetriever()
        chapter_data = await retriever.get_chapter_content(chapter_slug)
        if chapter_data:
            content_version = chapter_data.get("version", "")

    # Build payload for orchestrator
    payload = {
        "request_type": "personalization",
        "chapter_slug": chapter_slug,
        "user_id": user.user_id,
        "user_profile": user_profile,
        "content_version": content_version,
    }

    try:
        # Execute through orchestrator
        result = await orchestrator.execute("personalization", payload)

        # Transform orchestrator response to legacy shape
        agent_data = result.data

        # Record rate limit since orchestrator doesn't handle legacy rate limiting here
        await neon.record_ai_request(user.user_id, "personalize")

        response.content = {
            "content": agent_data.get("personalized_markdown", ""),
            "cached": result.cached,
            "generated_at": None,  # Legacy endpoint doesn't return this
            "content_version": agent_data.get("content_version", ""),
            "profile_used": agent_data.get("profile_used", agent_data.get("user_profile_snapshot", {})),
        }

        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Personalization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Personalization failed: {str(e)}")


@router.get("/personalize/status/{chapter_slug:path}")
async def personalize_status(
    chapter_slug: str,
    user: AuthenticatedUser = Depends(require_authenticated_user),
):
    """Check if a cached personalized version exists for this user and chapter."""
    slug = validate_slug(chapter_slug)
    neon = await get_neon_client()
    cached = await neon.get_personalized_content(user.user_id, slug)

    if not cached:
        return {
            "has_cached": False,
            "content_version": None,
            "is_stale": False,
            "generated_at": None,
        }

    # Check staleness
    is_stale = False
    try:
        retriever = _get_chapter_retriever()
        chapter_data = await retriever.get_chapter_content(slug)
        if chapter_data and cached["content_version"] != chapter_data["content_version"]:
            is_stale = True
    except Exception:
        pass

    return {
        "has_cached": True,
        "content_version": cached["content_version"],
        "is_stale": is_stale,
        "generated_at": cached["created_at"].isoformat() if cached.get("created_at") else None,
    }


async def _fetch_user_profile(request: Request) -> dict:
    """Fetch user profile from auth-server using the session cookie."""
    cookie_header = request.headers.get("cookie", "")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.BETTER_AUTH_URL}/api/profile",
                headers={"cookie": cookie_header},
                timeout=5.0,
            )
            if response.status_code == 200:
                data = response.json()
                profile = data.get("profile", {})
                return {
                    "software_background": profile.get("software_background", ""),
                    "hardware_background": profile.get("hardware_background", ""),
                    "robotics_knowledge": profile.get("robotics_knowledge", "beginner"),
                }
    except Exception as e:
        logger.warning(f"Failed to fetch user profile: {e}")

    return {
        "software_background": "",
        "hardware_background": "",
        "robotics_knowledge": "beginner",
    }
