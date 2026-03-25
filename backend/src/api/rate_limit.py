"""
Rate Limiting Middleware

Enforces 20 queries/hour per session using sliding window.

Author: Physical AI Platform Team
Date: 2026-02-09
"""
from typing import Optional
from uuid import UUID
from fastapi import HTTPException, Request, status

from ..config import get_settings
from ..db.neon_client import get_neon_client

settings = get_settings()


async def check_rate_limit(request: Request):
    """
    Dependency function to check rate limit before processing request.

    Enforces 20 queries/hour per session_id (FR-048).

    Raises:
        HTTPException 429: Rate limit exceeded
    """
    # Skip in mock mode
    if settings.MOCK_MODE:
        return

    # Get request body to extract session_id
    body = await request.json()
    session_id = body.get("session_id")

    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="session_id is required"
        )

    neon_client = await get_neon_client()

    # Check rate limit (1-hour sliding window)
    session_uuid = UUID(session_id)

    # Ensure the session exists before recording (prevents FK violation)
    try:
        await neon_client.create_or_update_session(session_uuid)
    except Exception:
        pass

    is_allowed = await neon_client.check_rate_limit(session_uuid, max_queries=20)

    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded: 20 queries per hour. Try again later.",
            headers={"Retry-After": "3600"}  # 1 hour
        )

    # Record this query for rate limiting
    await neon_client.record_query(session_uuid)


async def check_rate_limit_for_session(session_id: str, neon_client=None):
    """
    Check rate limit for a specific session ID.

    Used by chat endpoint directly when session_id is already extracted.

    Args:
        session_id: The session UUID string
        neon_client: Optional pre-connected NeonClient (e.g. from app.state.neon_pool).
                     If None, creates and manages its own connection.

    Raises:
        HTTPException 429: Rate limit exceeded
    """
    # Skip in mock mode
    if settings.MOCK_MODE:
        return

    if neon_client is None:
        neon_client = await get_neon_client()

    session_uuid = UUID(session_id)

    # Ensure the session exists before checking rate limits (prevents FK violation)
    try:
        await neon_client.create_or_update_session(session_uuid)
    except Exception:
        pass  # Best-effort; if DB is down, let rate-limit check handle it

    is_allowed = await neon_client.check_rate_limit(session_uuid, max_queries=settings.RATE_LIMIT_MAX_QUERIES)

    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: {settings.RATE_LIMIT_MAX_QUERIES} queries per hour. Try again later.",
            headers={"Retry-After": "3600"}
        )

    await neon_client.record_query(session_uuid)
