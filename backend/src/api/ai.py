"""
AI API Router
Provides new endpoints that route through the AI Orchestrator:
- /api/ai/personalize
- /api/ai/translate
- /api/ai/chat
- /api/ai/chat/stream
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any, Optional
from pydantic import BaseModel

from ..api.auth import require_authenticated_user, get_optional_user
from ..api.rate_limit import check_rate_limit_for_session
from ..services.chapter_retriever import ChapterRetriever
from ..db.neon_client import get_neon_client
from ..config import get_settings
from ..ai.orchestrator import AIOrchestrator
from ..ai.envelope import AIEnvelope, ErrorResponse


# Pydantic models for request/response validation
class PersonalizeRequest(BaseModel):
    chapter_slug: str


class TranslateRequest(BaseModel):
    chapter_slug: Optional[str] = None
    content: Optional[str] = None
    target_language: str = "urdu"


class ChatRequest(BaseModel):
    query: str
    mode: str = "full_book"
    selected_text: Optional[str] = None
    session_id: Optional[str] = None


class ChatStreamRequest(BaseModel):
    query: str
    mode: str = "full_book"
    selected_text: Optional[str] = None
    session_id: Optional[str] = None


class ChatKitRequest(BaseModel):
    """Request model for ChatKit-compatible endpoint."""
    query: str
    mode: str = "full_book"
    selected_text: Optional[str] = None
    session_id: Optional[str] = None
    thread_id: Optional[str] = None
    page_context: Optional[Dict[str, Any]] = None


# Create router
router = APIRouter(prefix="/api/ai", tags=["AI Agent"])


async def get_orchestrator(request: Request):
    """
    Get the AI orchestrator instance from app.state.
    """
    if not hasattr(request.app.state, 'orchestrator'):
        raise HTTPException(status_code=500, detail="AI Orchestrator not initialized")

    return request.app.state.orchestrator


@router.post("/personalize", response_model=AIEnvelope)
async def ai_personalize(
    request: PersonalizeRequest,
    user = Depends(require_authenticated_user),
    orchestrator: AIOrchestrator = Depends(get_orchestrator),
):
    """Personalize chapter content for authenticated user through orchestrator."""
    # Apply rate limiting
    # Note: For personalized content generation, we'll track this separately
    # using the neon_client directly since rate limiting is typically set up per query

    # Fetch chapter content
    retriever = ChapterRetriever()
    chapter_data = await retriever.get_chapter_content(request.chapter_slug)
    if not chapter_data:
        raise HTTPException(status_code=404, detail="Chapter not found")

    # Build payload for orchestrator
    payload = {
        "request_type": "personalization",
        "chapter_slug": request.chapter_slug,
        "content": chapter_data["markdown"],
        "user_id": user.get("id"),
        "user_profile": user.get("profile", {}),
        "content_version": chapter_data.get("version", ""),
    }

    try:
        # Execute through orchestrator
        result = await orchestrator.execute("personalization", payload)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Personalization failed: {str(e)}")


@router.post("/translate", response_model=AIEnvelope)
async def ai_translate(
    request: TranslateRequest,
    orchestrator: AIOrchestrator = Depends(get_orchestrator),
):
    """Translate chapter content to Urdu through orchestrator."""
    # Apply rate limiting (by IP if unauthenticated)
    # Note: We'll need to adapt this to work with the current IP-based rate limiting system
    neon_client = await get_neon_client()

    # If content is provided directly, we just translate it
    if request.content:
        # Fetch content and translate directly using orchestrator
        if not request.chapter_slug:
            # If no chapter slug provided, use a placeholder
            request.chapter_slug = "custom_content"

        payload = {
            "request_type": "translation",
            "chapter_slug": request.chapter_slug,
            "content": request.content,
            "target_language": request.target_language,
        }
    else:
        # Fetch chapter content by slug if not provided directly
        if not request.chapter_slug:
            raise HTTPException(status_code=400, detail="Either chapter_slug or content must be provided")

        # Apply rate limiting
        # In real implementation, we'd get client IP for rate limiting
        # This is a placeholder - actual rate limiting would use different approach

        # Fetch chapter content
        retriever = ChapterRetriever()
        chapter_data = await retriever.get_chapter_content(request.chapter_slug)
        if not chapter_data:
            raise HTTPException(status_code=404, detail="Chapter not found")

        payload = {
            "request_type": "translation",
            "chapter_slug": request.chapter_slug,
            "content": chapter_data["markdown"],
            "target_language": request.target_language,
            "content_version": chapter_data.get("version", ""),
        }

    try:
        # Execute through orchestrator
        result = await orchestrator.execute("translation", payload)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@router.post("/chat", response_model=AIEnvelope)
async def ai_chat(
    request: ChatRequest,
    user = Depends(get_optional_user),
    orchestrator: AIOrchestrator = Depends(get_orchestrator),
):
    """RAG chat query through orchestrator."""
    # Note: Rate limiting is handled by the AI orchistrator through the neon_client

    payload = {
        "request_type": "rag_chat",
        "query": request.query,
        "mode": request.mode,
        "selected_text": request.selected_text,
        "session_id": request.session_id,
        "user_id": user.get("id") if user else None,
    }

    try:
        # Execute through orchestrator
        result = await orchestrator.execute("rag_chat", payload)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


from fastapi.responses import StreamingResponse


@router.post("/chat/stream")
async def ai_chat_stream(
    request: ChatStreamRequest,
    user = Depends(get_optional_user),
    orchestrator: AIOrchestrator = Depends(get_orchestrator),
):
    """RAG chat query with streaming through orchestrator."""
    # Note: Rate limiting is handled by the AI orchestrator through the neon_client

    payload = {
        "request_type": "rag_chat",
        "query": request.query,
        "mode": request.mode,
        "selected_text": request.selected_text,
        "session_id": request.session_id,
        "user_id": user.get("id") if user else None,
        "stream": True,
    }

    async def generate_stream():
        # Use orchestrator streaming method
        try:
            async for token in orchestrator.execute_stream("rag_chat", payload):
                yield f"data: {token}\n\n"
            # Send final message to complete the stream
            yield f"data: [DONE]\n\n"
        except Exception as e:
            yield f"event: error\ndata: {str(e)}\n\n"
            return

    return StreamingResponse(generate_stream(), media_type="text/event-stream")


@router.post("/chatkit", response_model=AIEnvelope)
async def ai_chatkit(
    request: ChatKitRequest,
    user=Depends(get_optional_user),
    orchestrator: AIOrchestrator = Depends(get_orchestrator),
):
    """
    ChatKit-compatible endpoint through AI Orchestrator.

    Provides ChatKit-like functionality while leveraging the orchestrator
    for advanced RAG capabilities and tool-based reasoning.
    """
    # Apply rate limiting via neon client through orchestrator

    payload = {
        "request_type": "rag_chat",
        "query": request.query,
        "mode": request.mode,
        "selected_text": request.selected_text,
        "session_id": request.session_id,
        "thread_id": request.thread_id,
        "user_id": user.get("id") if user else None,
        "page_context": request.page_context,  # Include page context information
    }

    try:
        # Execute through orchestrator
        result = await orchestrator.execute("rag_chat", payload)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ChatKit processing failed: {str(e)}")


@router.post("/chatkit/stream")
async def ai_chatkit_stream(
    request: ChatKitRequest,
    user=Depends(get_optional_user),
    orchestrator: AIOrchestrator = Depends(get_orchestrator),
):
    """ChatKit-compatible streaming endpoint through AI Orchestrator."""
    # Apply rate limiting via neon client through orchestrator

    payload = {
        "request_type": "rag_chat",
        "query": request.query,
        "mode": request.mode,
        "selected_text": request.selected_text,
        "session_id": request.session_id,
        "thread_id": request.thread_id,
        "user_id": user.get("id") if user else None,
        "page_context": request.page_context,
        "stream": True,
    }

    async def generate_chatkit_stream():
        # Use orchestrator streaming method with ChatKit formatting
        try:
            async for token in orchestrator.execute_stream("rag_chat", payload):
                # Format as ChatKit-like SSE event
                if token.strip() and token != "[DONE]":
                    yield f"data: {token}\n\n"
                elif token == "[DONE]":
                    yield f"data: [DONE]\n\n"
        except Exception as e:
            # Send error event in ChatKit format
            yield f'event: error\ndata: {str(e)}\n\n'
            return

    return StreamingResponse(
        generate_chatkit_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true"
        }
    )


# Status endpoint to check availability
@router.get("/status")
def ai_status():
    """Check if AI services are available."""
    return {
        "status": "available",
        "features": ["personalization", "translation", "chat"],
        "grounding_policies": ["strict_grounding", "structural_fidelity", "semantic_fidelity"]
    }