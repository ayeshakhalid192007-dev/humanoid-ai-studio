"""
Chat API Endpoints - LEGACY (Routes through orchestrator)

Provides:
- POST /chat: Standard RAG query with tool-based retrieval (routes through orchestrator)
- POST /chat/stream: SSE streaming responses (routes through orchestrator)
- POST /chat/v2: ChatKit-based conversational endpoint (routes through orchestrator)

Supports mock mode for local testing and production mode with
full OpenAI + Qdrant + Neon integration.

This endpoint has been migrated to route through the AI Orchestrator.
New implementations should use /api/ai/chat instead.
Deprecation: This endpoint is deprecated and routes through the new architecture.

Author: Physical AI Platform Team
Date: 2026-02-12
"""

from typing import Optional
from enum import Enum

from fastapi import APIRouter, HTTPException, Request, status, Depends, Query
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field, UUID4

from ..config import get_settings
from ..models.query import ChatRequest, ChatResponse, Citation, RetrievedChunk
from .auth import get_optional_user, get_user_id_from_session, AuthenticatedUser
from .sessions import add_turn_to_session
from ..utils.logger import get_logger
from ..chatkit.agent import ChatKitAgent
from ..chatkit.context_injector import ContextInjector, ConversationContext

logger = get_logger(__name__)
router = APIRouter()
settings = get_settings()


async def get_orchestrator(request: Request):
    """
    Get the AI orchestrator instance from app.state.
    """
    if not hasattr(request.app.state, 'orchestrator'):
        raise HTTPException(status_code=500, detail="AI Orchestrator not initialized")

    return request.app.state.orchestrator


# ===========================================================================
# Request/Response Models for Enhanced Endpoints
# ===========================================================================

class AnsweringMode(str, Enum):
    """Available answering modes."""
    FULL_BOOK = "full_book"
    SELECTED_TEXT = "selected_text"


class ChatV2Request(BaseModel):
    """Enhanced chat request with mode selection."""
    query: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="User's question"
    )
    session_id: Optional[str] = Field(
        None,
        description="Session ID for conversation continuity"
    )
    mode: AnsweringMode = Field(
        default=AnsweringMode.FULL_BOOK,
        description="Answering mode: full_book (RAG) or selected_text"
    )
    selected_text: Optional[str] = Field(
        None,
        max_length=2000,
        description="Selected text for selected_text mode"
    )
    page_context: Optional[str] = Field(
        None,
        description="Current page URL for context"
    )


class ChatV2Response(BaseModel):
    """Enhanced chat response with tool metadata."""
    answer: str
    citations: list
    mode: str
    tool_calls: list = Field(default_factory=list)
    session_id: str
    retrieved_chunks: list = Field(default_factory=list)


class StreamChatRequest(BaseModel):
    """Request for streaming chat endpoint."""
    query: str = Field(..., min_length=1, max_length=500)
    session_id: Optional[str] = None
    mode: AnsweringMode = AnsweringMode.FULL_BOOK
    selected_text: Optional[str] = None


# ===========================================================================
# Original Chat Endpoint (Backward Compatible)
# ===========================================================================

@router.post("/chat", status_code=status.HTTP_200_OK)
async def chat_query(request: Request, chat_request: ChatRequest):
    """
    Process chatbot query using RAG pipeline via AI Orchestrator (legacy endpoint).

    In mock mode, returns demo responses without real API calls.
    In production mode, uses OpenAI + Qdrant + Neon via orchestrator.
    """
    deprecation_headers = {
        "Deprecation": "true",
        "Link": '</api/ai/chat>; rel="successor-version"',
    }

    try:
        # Check if mock mode is enabled
        mock_mode = getattr(request.app.state, 'mock_mode', False) or settings.MOCK_MODE

        if mock_mode:
            # Use mock services for backward compatibility
            from ..services.mock_services import (
                get_mock_retriever,
                get_mock_generator,
                get_mock_neon
            )

            retriever = get_mock_retriever()
            generator = get_mock_generator()
            neon = get_mock_neon()

            # Check rate limit
            rate_check = await neon.check_rate_limit(
                str(chat_request.session_id),
                settings.RATE_LIMIT_MAX_QUERIES
            )
            if not rate_check["allowed"]:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. {rate_check['remaining']} queries remaining.",
                    headers={"X-Rate-Limit-Remaining": str(rate_check["remaining"])}
                )

            # Search for relevant chunks
            chunks = await retriever.search(
                chat_request.query,
                limit=settings.QDRANT_SEARCH_LIMIT,
                score_threshold=settings.QDRANT_SCORE_THRESHOLD
            )

            # Generate response
            result = await generator.generate(
                chat_request.query,
                chunks,
                settings.OPENAI_MAX_TOKENS
            )

            # Log conversation
            await neon.log_conversation(
                session_id=str(chat_request.session_id),
                query=chat_request.query,
                response=result["answer"],
                citations=result["citations"]
            )
            await neon.record_query(str(chat_request.session_id))

            # Build citations with proper schema
            citations = []
            for c in chunks[:3]:
                citations.append(Citation(
                    module=c["payload"]["module"].replace("module", ""),
                    lesson=c["payload"]["lesson"],
                    section=c["payload"]["title"],
                    url=f"http://localhost:3000{c['payload']['source']}"
                ))

            # Build retrieved chunks with proper schema
            retrieved_chunks = []
            for c in chunks:
                retrieved_chunks.append(RetrievedChunk(
                    chunk_id=c["id"],
                    text_preview=c["payload"]["content"][:200],
                    score=c["score"],
                    module=c["payload"]["module"].replace("module", ""),
                    lesson=c["payload"]["lesson"],
                    section_title=c["payload"]["title"],
                    url=f"http://localhost:3000{c['payload']['source']}"
                ))

            return JSONResponse(
                content=ChatResponse(
                    answer=result["answer"],
                    citations=citations,
                    retrieved_chunks=retrieved_chunks
                ).model_dump(mode="json"),
                headers=deprecation_headers,
            )

        else:
            # Use orchestrator for real services
            from .rate_limit import check_rate_limit_for_session

            # Get orchestrator
            orchestrator = await get_orchestrator(request)

            # Reuse app-level Neon pool (initialized in main.py lifespan)
            neon_client = getattr(request.app.state, 'neon_pool', None)

            # Check rate limit
            await check_rate_limit_for_session(
                str(chat_request.session_id),
                neon_client=neon_client,
            )

            # Build payload for orchestrator based on request context
            payload = {
                "request_type": "rag_chat",
                "query": chat_request.query,
                "session_id": str(chat_request.session_id),
                "mode": "full_book",
                "selected_text": chat_request.selection_text,  # This would be used if mode is selected_text
                "user_id": None  # Legacy endpoint doesn't pass user_id but orchestrator might still work
            }

            # Use selected text mode if provided
            if chat_request.selection_text:
                payload["mode"] = "selected_text"

            # Execute through orchestrator
            result = await orchestrator.execute("rag_chat", payload)

            # Transform orchestrator response to legacy shape
            agent_data = result.data

            # Log conversation using app-level pool (no per-request connect/close)
            if neon_client and hasattr(neon_client, 'insert_conversation_turn'):
                from uuid import UUID
                try:
                    await neon_client.insert_conversation_turn(
                        session_id=UUID(str(chat_request.session_id)),
                        query=chat_request.query,
                        response=agent_data.get("content", ""),
                        retrieved_chunks=agent_data.get("retrieved_chunks", []),
                        page_context=chat_request.page_context,
                        metadata={
                            "selection_text": chat_request.selection_text,
                            "citation_count": len(agent_data.get("citations", []))
                        }
                    )
                except Exception:
                    logger.warning("Failed to log conversation turn")

            # Build citations with proper schema
            citations = []
            for citation_data in agent_data.get("citations", [])[:3]:
                # Extract module/lesson from the citation data
                # Example format: "Module X, Lesson Y: content"
                if isinstance(citation_data, str):
                    # Parse the citation string
                    parts = citation_data.split(": ", 1)
                    if len(parts) > 0:
                        module_lesson = parts[0]  # Module X, Lesson Y
                        module_lesson_parts = module_lesson.split(", ")
                        if len(module_lesson_parts) >= 2:
                            module_part = module_lesson_parts[0].replace("Module ", "")
                            lesson_part = module_lesson_parts[1].replace("Lesson ", "")

                            citations.append(Citation(
                                module=module_part,
                                lesson=lesson_part,
                                section="Referenced Section",
                                url="http://localhost:3000"
                            ))
                        else:
                            # Handle other formats
                            citations.append(Citation(
                                module="Unknown",
                                lesson="Unknown",
                                section="Referenced Content",
                                url="http://localhost:3000"
                            ))
                else:
                    # Handle dict format if needed
                    citations.append(Citation(
                        module=citation_data.get("module", "Unknown"),
                        lesson=citation_data.get("lesson", "Unknown"),
                        section=citation_data.get("section", "Referenced Content"),
                        url=citation_data.get("url", "http://localhost:3000")
                    ))

            # Build retrieved chunks with proper schema
            retrieved_chunks = []
            for chunk in agent_data.get("retrieved_chunks", []):
                if isinstance(chunk, dict):
                    retrieved_chunks.append(RetrievedChunk(
                        chunk_id=chunk.get("chunk_id", chunk.get("id", "")),
                        text_preview=chunk.get("text", chunk.get("content", ""))[:200],
                        score=chunk.get("score", 0.0),
                        module=chunk.get("module", ""),
                        lesson=chunk.get("lesson", ""),
                        section_title=chunk.get("section_title", chunk.get("title", "Unknown")),
                        url=chunk.get("url", chunk.get("source", "http://localhost:3000"))
                    ))
                else:
                    # Handle other formats
                    retrieved_chunks.append(RetrievedChunk(
                        chunk_id=getattr(chunk, 'chunk_id', getattr(chunk, 'id', "")),
                        text_preview=getattr(chunk, 'text', getattr(chunk, 'content', ""))[:200],
                        score=getattr(chunk, 'score', 0.0),
                        module=getattr(chunk, 'module', ""),
                        lesson=getattr(chunk, 'lesson', ""),
                        section_title=getattr(chunk, 'section_title', getattr(chunk, 'title', "Unknown")),
                        url=getattr(chunk, 'url', getattr(chunk, 'source', "http://localhost:3000"))
                    ))

            return JSONResponse(
                content=ChatResponse(
                    answer=agent_data.get("content", ""),
                    citations=citations,
                    retrieved_chunks=retrieved_chunks
                ).model_dump(mode="json"),
                headers=deprecation_headers,
            )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(e)}"
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unavailable: {str(e)}"
        )
    except Exception as e:
        logger.exception(f"Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


# ===========================================================================
# Alias Endpoints (/ask, /ask-from-selection)
# ===========================================================================

@router.post("/ask", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def ask(request: Request, chat_request: ChatRequest) -> ChatResponse:
    """Alias for /chat -- standard RAG query."""
    return await chat_query(request, chat_request)


@router.post("/ask-from-selection", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def ask_from_selection(request: Request, chat_request: ChatRequest) -> ChatResponse:
    """Alias for /chat with required selection_text."""
    if not chat_request.selection_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="selection_text is required for /ask-from-selection"
        )
    return await chat_query(request, chat_request)


# ===========================================================================
# ChatKit-Based Endpoint (v2)
# ===========================================================================

@router.post("/chat/v2", status_code=status.HTTP_200_OK)
async def chat_v2(
    http_request: Request,
    request: ChatV2Request,
    user_id: Optional[str] = Depends(get_user_id_from_session),
    use_chatkit: bool = Query(False, description="Whether to use the new ChatKit-based endpoint")
):
    """
    Enhanced chat endpoint with option to use ChatKit agent.

    Features:
    - By default: Standard RAG via AI Orchestrator
    - With use_chatkit=true: Uses ChatKit agent with tool-based RAG
    - Dual mode support (full_book / selected_text)
    - Session continuity
    - User attribution
    """

    try:
        if use_chatkit:
            # Use the new ChatKit implementation for enhanced conversation
            # Extract user profile if available
            user_profile = None
            if user_id:
                # This would typically fetch from DB or auth system
                user_profile = {"id": user_id, "preferred_language": "en", "expertise_level": "intermediate"}

            # Create conversation context
            additional_metadata = {"page_context": request.page_context} if request.page_context else {}

            # Create context with available data
            context_injector = ContextInjector()
            conv_context = context_injector.create_conversation_context(
                additional_metadata=additional_metadata
            )

            # If we have page context, build it
            if request.page_context:
                page_data = {
                    "title": "Default Title",
                    "url": request.page_context,
                    "module": "Module X",
                    "section": "Section X",
                    "contentPreview": "Content preview here..."
                }
                conv_context.page_context = context_injector.extract_page_context(page_data)

            # Create ChatKit agent
            agent = ChatKitAgent(
                session_id=request.session_id,
                user_id=user_id
            )

            # Inject context into agent
            await context_injector.inject_context_to_agent(agent, conv_context)

            # Process the message
            result = await agent.process_message(
                user_message=request.query,
                selected_text=request.selected_text
            )

            # Personalize response based on context if needed
            personalized_answer = await context_injector.personalize_context_response(
                conv_context,
                result["answer"]
            )

            return JSONResponse(content=ChatV2Response(
                answer=personalized_answer,
                citations=result["citations"],
                mode=result["mode"],
                tool_calls=result["tool_calls"],
                session_id=result["session_id"],
                retrieved_chunks=[]
            ).model_dump(mode="json"))

        else:
            # Use the standard orchestrator approach (original behavior)
            # Get orchestrator
            orchestrator = await get_orchestrator(http_request)

            # Validate mode/selected_text combination
            if request.mode == AnsweringMode.SELECTED_TEXT and not request.selected_text:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="selected_text is required when mode is 'selected_text'"
                )

            # Build payload for orchestrator
            payload = {
                "request_type": "rag_chat",
                "query": request.query,
                "session_id": request.session_id,
                "mode": request.mode.value,
                "selected_text": request.selected_text if request.mode == AnsweringMode.SELECTED_TEXT else None,
                "user_id": user_id
            }

            # Execute through orchestrator
            result = await orchestrator.execute("rag_chat", payload)

            # Transform orchestrator response to legacy shape
            agent_data = result.data

            # Log conversation turn
            await add_turn_to_session(
                session_id=agent_data.get("session_id", request.session_id or "unknown"),
                query=request.query,
                response=agent_data.get("content", ""),
                citations=agent_data.get("citations", [])
            )

            logger.info(
                f"Chat v2 (via orchestrator): session={agent_data.get('session_id', request.session_id)}, "
                f"mode={agent_data.get('mode', request.mode.value)}, agent_type={agent_data.get('agent_type', 'rag_chat')}"
            )

            return JSONResponse(content=ChatV2Response(
                answer=agent_data.get("content", ""),
                citations=agent_data.get("citations", []),
                mode=agent_data.get("mode", request.mode.value),
                tool_calls=agent_data.get("tool_calls", []),
                session_id=agent_data.get("session_id", request.session_id or ""),
                retrieved_chunks=agent_data.get("retrieved_chunks", [])
            ).model_dump(mode="json"))

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(e)}"
        )
    except Exception as e:
        logger.exception(f"Chat v2 error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


# ===========================================================================
# Streaming Endpoint
# ===========================================================================

@router.post("/chat/stream")
async def chat_stream(
    http_request: Request,
    request: StreamChatRequest,
    user_id: Optional[str] = Depends(get_user_id_from_session)
):
    """
    Streaming chat endpoint using Server-Sent Events (SSE) via AI Orchestrator.

    Returns real-time response chunks as they're generated via the AI Orchestrator.

    SSE Event Format:
        event: message
        data: {"type": "chunk", "content": "...", "metadata": {}}

        event: message
        data: {"type": "done", "content": "", "metadata": {...}}
    """
    try:
        # Get orchestrator
        orchestrator = await get_orchestrator(http_request)

        # Validate
        if request.mode == AnsweringMode.SELECTED_TEXT and not request.selected_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="selected_text is required when mode is 'selected_text'"
            )

        # Build payload for orchestrator
        payload = {
            "request_type": "rag_chat",
            "query": request.query,
            "session_id": request.session_id,
            "mode": request.mode.value,
            "selected_text": request.selected_text if request.mode == AnsweringMode.SELECTED_TEXT else None,
            "user_id": user_id,
            "stream": True
        }

        async def generate_and_log():
            """Generate streaming response via orchestrator and log when complete."""
            # Create a simple buffer to collect the full response for logging
            full_response = ""

            # Use orchestrator streaming
            async for token in orchestrator.execute_stream("rag_chat", payload):
                # Format as SSE chunk for compatibility
                if token.strip() and token != "[DONE]":
                    full_response += token
                    yield f"data: {token}\n\n"
                elif token == "[DONE]":
                    # When done, log the conversation
                    await add_turn_to_session(
                        session_id=request.session_id or "unknown",
                        query=request.query,
                        response=full_response,
                        citations=[]  # Might not have citations in streaming
                    )
                    yield f"data: [DONE]\n\n"

        # Return streaming response
        return StreamingResponse(generate_and_log(), media_type="text/event-stream")

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Stream error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Streaming error: {str(e)}"
        )


# ===========================================================================
# Mode Switch Helper
# ===========================================================================

@router.get("/chat/modes")
async def get_available_modes():
    """
    Get available answering modes.

    Returns mode descriptions for UI display.
    """
    return {
        "modes": [
            {
                "id": "full_book",
                "name": "Full Book Search",
                "description": "Search the entire curriculum for relevant content using semantic similarity",
                "requires_selected_text": False
            },
            {
                "id": "selected_text",
                "name": "Selected Text Only",
                "description": "Answer using ONLY the text you've highlighted - no broader search",
                "requires_selected_text": True
            }
        ],
        "default": "full_book"
    }
