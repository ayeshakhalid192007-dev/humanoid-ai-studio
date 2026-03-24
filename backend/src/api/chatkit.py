"""
ChatKit API Endpoints

This module implements the ChatKit protocol endpoints for the Physical AI platform,
including thread management, authentication, and integration with the existing RAG system.

Author: Physical AI Platform Team
Date: 2026-02-18
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
import json
import time
import uuid

from ..api.auth import require_authenticated_user, get_optional_user
from ..utils.logger import get_logger
from ..chatkit.server import PhysicalAIChatKitServer, RequestContext
from ..chatkit.agent import ChatKitAgent
from ..db.neon_client import get_neon_client
from ..chatkit.chat_service import ChatKitService, ChatKitThread

# Create router for ChatKit endpoints
router = APIRouter(prefix="/api/chatkit", tags=["chatkit"])
logger = get_logger(__name__)

# Initialize ChatKit server and service
chatkit_server = PhysicalAIChatKitServer()
chatkit_service = ChatKitService()


@router.post("/threads")
async def create_thread(
    request: Request,
    user=Depends(get_optional_user)
):
    """
    Create a new ChatKit thread.

    This endpoint creates a new conversation thread with proper authentication
    and context injection from the frontend.
    """
    try:
        # Extract request context
        body = await request.json()
        initial_messages = body.get("initial_messages", [])
        metadata = body.get("metadata", {})

        # Use the new service for thread creation
        thread = await chatkit_service.create_thread(
            messages=initial_messages,
            metadata=metadata,
            user_id=user.id if user else None
        )

        return {
            "id": thread.id,
            "object": thread.object,
            "created_at": thread.created_at,
            "updated_at": thread.updated_at,
            "metadata": thread.metadata
        }
    except Exception as e:
        logger.error(f"Error creating thread: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error creating thread: {str(e)}")


@router.get("/threads/{thread_id}")
async def get_thread(
    thread_id: str,
    user=Depends(get_optional_user)
):
    """
    Get a specific thread by ID.
    """
    # Use the new service for thread retrieval
    thread = await chatkit_service.get_thread(thread_id, user.id if user else None)

    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    return {
        "id": thread.id,
        "object": thread.object,
        "created_at": thread.created_at,
        "updated_at": thread.updated_at,
        "metadata": thread.metadata
    }


@router.delete("/threads/{thread_id}")
async def delete_thread(
    thread_id: str,
    user=Depends(require_authenticated_user)  # Require authentication for deletion
):
    """
    Delete a specific thread by ID.

    Note: This endpoint requires user authentication for security.
    """
    # Use the new service for thread deletion with access control
    success = await chatkit_service.delete_thread(thread_id, user.id)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete thread")

    return {
        "id": thread_id,
        "deleted": True
    }


@router.post("/threads/{thread_id}/messages")
async def create_message(
    request: Request,
    thread_id: str,
    user=Depends(get_optional_user)
):
    """
    Add a message to a thread and get the AI response.

    This endpoint processes the user's message using the ChatKit server
    and streams the response back to the client.
    """
    try:
        # Extract message request
        body = await request.json()
        message_text = body.get("content", "")
        page_context = body.get("page_context")
        page_url = body.get("page_url")
        page_title = body.get("page_title")
        selected_text = body.get("selected_text")

        # Validate input
        if not message_text.strip():
            raise HTTPException(status_code=400, detail="Message content cannot be empty")

        # Verify thread access using service
        thread = await chatkit_service.get_thread(thread_id, user.id if user else None)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        # Extract session ID from thread ID
        if thread_id.startswith("thread_"):
            session_id = thread_id[7:]
        else:
            session_id = thread_id

        # Add message using the service first (before processing)
        message = await chatkit_service.add_message(
            thread_id=thread_id,
            role="user",
            content=message_text,
            metadata={
                "selected_text": selected_text,
                "page_context": page_context,
                "page_url": page_url,
                "page_title": page_title
            },
            user_id=user.id if user else None
        )

        # Now process the message and stream the response
        async def response_generator():
            """Generate streaming responses for SSE."""
            full_response = ""
            try:
                # Use the chat service to run the thread with streaming
                async for chunk in chatkit_service.run_thread_streaming(
                    thread_id=thread_id,
                    user_message=message_text,
                    user_id=user.id if user else None,
                    page_context=page_context
                ):
                    if chunk.get("type") == "chunk":
                        full_response += chunk.get("content", "")

                    # Format chunks for frontend
                    yield f"data: {json.dumps(chunk)}\n\n"

            except Exception as e:
                logger.error(f"Error in response generator: {str(e)}", exc_info=True)
                yield f'data: {json.dumps({"type": "error", "content": f"Error generating response: {str(e)}", "metadata": {}})}\n\n'
            finally:
                # Log the full conversation turn to database after streaming is complete
                try:
                    from ..db.neon_client import get_neon_client
                    neon_client = await get_neon_client()

                    turn_data = {
                        "module": page_context.get("module") if page_context else "General",
                        "lesson": page_context.get("lesson") if page_context else "General",
                        "section_title": page_context.get("section_title") if page_context else "",
                        "url": page_url or ""
                    }
                    retrieved_chunks = [turn_data]

                    await neon_client.insert_conversation_turn(
                        session_id=uuid.UUID(session_id),
                        query=message_text,
                        response=full_response,
                        retrieved_chunks=retrieved_chunks,
                        page_context=page_url,
                        metadata={
                            "selected_text": selected_text,
                            "page_title": page_title
                        }
                    )
                except Exception as log_err:
                    logger.error(f"Failed to log conversation turn: {str(log_err)}", exc_info=True)

        return StreamingResponse(
            response_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing message for thread {thread_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@router.get("/threads/{thread_id}/messages")
async def list_messages(
    thread_id: str,
    user=Depends(get_optional_user),
    limit: int = 20,
    before: Optional[str] = None,
    after: Optional[str] = None
):
    """
    List messages from a thread (with appropriate access control).
    """
    try:
        # Import necessary modules
        import uuid
        from ..db.neon_client import get_neon_client

        # Build request context
        context = RequestContext(user_id=user.id if user else None)

        # Get thread from server
        thread = await chatkit_server.get_thread(thread_id, context)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        # Extract session ID from thread id
        if thread_id.startswith("thread_"):
            session_id_str = thread_id[7:]
        else:
            session_id_str = thread_id

        # Try to convert session_id to UUID for database lookup
        try:
            session_uuid = uuid.UUID(session_id_str)
        except ValueError:
            logger.error(f"Invalid session UUID: {session_id_str}")
            raise HTTPException(status_code=400, detail="Invalid thread ID")

        # Get conversation history from DB
        neon_client = await get_neon_client()
        conversation_turns = await neon_client.get_conversation_turns(session_uuid, limit=limit)

        # Format as ChatKit message responses
        messages = []

        for i, turn in enumerate(conversation_turns):
            # Add user message
            user_message = {
                "id": f"msg_user_{i}_{session_id_str}",
                "thread_id": thread_id,
                "role": "user",
                "content": [{"type": "text", "text": {"value": turn['query']}}],
                "created_at": int(turn['created_at'].timestamp()) if turn.get('created_at') else int(time.time()),
                "type": "message",
                "status": "read"  # All historical messages are considered read
            }
            messages.append(user_message)

            # Add assistant response if it exists
            if turn.get('response'):
                assistant_message = {
                    "id": f"msg_assistant_{i}_{session_id_str}",
                    "thread_id": thread_id,
                    "role": "assistant",
                    "content": [{"type": "text", "text": {"value": turn['response']}}],
                    "created_at": int(turn['created_at'].timestamp()) if turn.get('created_at') else int(time.time()) + 1,
                    "type": "message",
                    "status": "read"  # All historical messages are considered read
                }
                messages.append(assistant_message)

        # Sort messages by timestamp to maintain chronological order
        messages.sort(key=lambda x: x['created_at'])

        return {
            "object": "list",
            "data": messages,
            "first_id": messages[0]["id"] if messages else None,
            "last_id": messages[-1]["id"] if messages else None,
            "has_more": len(conversation_turns) >= limit  # Indicate if more messages available
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing messages for thread {thread_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error listing messages: {str(e)}")


@router.post("/context-inject")
async def inject_context(
    request: Request,
    user=Depends(get_optional_user)
):
    """
    Accept context from the frontend and inject it into the conversation.

    This endpoint allows the frontend to send page context, user information,
    and other relevant data to enrich the chat experience.
    """
    try:
        body = await request.json()
        page_title = body.get('page_title', '')
        page_url = body.get('page_url', '')
        page_content = body.get('page_content', '')
        selected_text = body.get('selected_text', '')

        # Create enriched context
        context = {
            "page_title": page_title,
            "page_url": page_url,
            "page_content_snippet": page_content[:500] if page_content else "",  # Limit size
            "selected_text": selected_text,
            "user_id": user.id if user else None
        }

        # This would be used when creating agent instances
        # In a real implementation, this might save to a cache/database
        # or add to request context for the conversation

        return {
            "status": "success",
            "message": "Context received and processed",
            "context_id": f"ctx_{hash(str(context)) % 10000}"  # Simple context ID
        }
    except Exception as e:
        logger.error(f"Error injecting context: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error injecting context: {str(e)}")


# Add the router to be included in the main app
__all__ = ["router"]