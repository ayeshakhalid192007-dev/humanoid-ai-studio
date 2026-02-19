"""
Translation API Router - LEGACY (Routes through orchestrator)

Endpoints for generating and retrieving Urdu translations of chapters.
Public access — no authentication required.

This endpoint has been migrated to route through the AI Orchestrator.
New implementations should use /api/ai/translate instead.
Deprecation: This endpoint is deprecated and routes through the new architecture.

Author: Physical AI Platform Team
Date: 2026-02-16
"""
from typing import Optional
from pydantic import BaseModel, Field

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse

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


def _get_client_identifier(request: Request) -> str:
    """Get client identifier for rate limiting (IP-based for public endpoint)."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class TranslateRequest(BaseModel):
    chapter_slug: str = Field(..., description="Docusaurus doc slug")
    content: Optional[str] = Field(
        default=None,
        description="Optional content override (for translating personalized content)"
    )


async def get_orchestrator(request: Request):
    """
    Get the AI orchestrator instance from app.state.
    """
    if not hasattr(request.app.state, 'orchestrator'):
        raise HTTPException(status_code=500, detail="AI Orchestrator not initialized")

    return request.app.state.orchestrator


@router.post("/translate", response_class=JSONResponse)
async def translate_chapter(
    body: TranslateRequest,
    request: Request,
):
    """Generate or retrieve Urdu translation of a chapter via AI Orchestrator. No auth required."""
    # Create a deprecation header for this endpoint
    response = JSONResponse(
        content={},
        headers={
            "Deprecation": "true",
            "Link": '</api/ai/translate>; rel="successor-version"',
        }
    )

    chapter_slug = validate_slug(body.chapter_slug)
    client_id = _get_client_identifier(request)

    # Get orchestrator
    orchestrator = await get_orchestrator(request)

    # Check rate limit (using the new system)
    neon = await get_neon_client()
    is_allowed = await neon.check_ai_rate_limit(
        identifier=client_id,
        request_type="translate",
        max_requests=settings.TRANSLATE_RATE_LIMIT_MAX,
        window_hours=settings.AI_RATE_LIMIT_WINDOW_HOURS,
    )
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: {settings.TRANSLATE_RATE_LIMIT_MAX} translations per hour.",
            headers={"Retry-After": "3600"},
        )

    # Fetch chapter content to get content version if translating a chapter (not custom content)
    content_version = ""
    if chapter_slug and not body.content:  # Only fetch if translating chapter, not custom content
        from ..services.chapter_retriever import ChapterRetriever
        retriever = ChapterRetriever()
        chapter_data = await retriever.get_chapter_content(chapter_slug)
        if chapter_data:
            content_version = chapter_data.get("version", "")

    # Build payload for orchestrator
    payload = {
        "request_type": "translation",
        "chapter_slug": chapter_slug,
        "content": body.content,  # May be None, the agent will fetch if needed
        "content_version": content_version,
    }

    if body.content:
        # For custom content translation, specify the content directly
        payload["content"] = body.content
        payload["content_version"] = "custom"  # Use "custom" for custom content

    try:
        # Execute through orchestrator
        result = await orchestrator.execute("translation", payload)

        # Transform orchestrator response to legacy shape
        agent_data = result.data

        # Record rate limit since orchestrator doesn't handle legacy rate limiting here
        await neon.record_ai_request(client_id, "translate")

        response.content = {
            "content": agent_data.get("translated_markdown", agent_data.get("content", "")),
            "cached": result.cached,
            "generated_at": None,  # Legacy endpoint doesn't return this
            "content_version": agent_data.get("content_version", "custom" if body.content else ""),
        }

        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@router.get("/translate/status/{chapter_slug:path}")
async def translate_status(chapter_slug: str):
    """Check if a cached Urdu translation exists for this chapter."""
    slug = validate_slug(chapter_slug)
    neon = await get_neon_client()
    cached = await neon.get_urdu_translation(slug)

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
