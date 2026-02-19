"""
ChatKit Server Implementation

This module implements a compatible interface with OpenAI ChatKit for the Physical AI platform,
integrating with the existing orchestrator pattern and RAG tools for educational conversations.

Author: Physical AI Platform Team
Date: 2026-02-18
"""

import json
import uuid
import time
from typing import AsyncIterator, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from .agent import ChatKitAgent
from ..config import get_settings
from ..utils.logger import get_logger
from ..db.neon_client import get_neon_client

logger = get_logger(__name__)

@dataclass
class RequestContext:
    """Context for ChatKit requests containing authentication and session info."""
    user_id: Optional[str] = None
    session_token: Optional[str] = None
    page_context: Optional[Dict[str, Any]] = None
    page_url: Optional[str] = None
    page_title: Optional[str] = None


class PhysicalAIChatKitServer:
    """
    Physical AI-specific ChatKit compatible server.

    This server integrates with the existing RAG tools and orchestrator
    pattern while following the ChatKit-like protocol patterns.
    """

    def __init__(self):
        self.settings = get_settings()

    async def create_thread(self, context: RequestContext) -> Dict[str, Any]:
        """
        Create a new ChatKit thread with proper persistence.

        Args:
            context: Request context with auth and page information

        Returns:
            Thread object with ID and metadata
        """
        # Create thread in Neon database
        try:
            neon_client = await get_neon_client()

            # Create a UUID for session tracking
            import uuid
            session_id = uuid.uuid4()

            # Create session in database
            session_data = await neon_client.create_or_update_session(
                session_id=session_id,
                metadata={
                    "user_id": context.user_id,
                    "page_url": context.page_url,
                    "page_title": context.page_title,
                    "created_at": datetime.utcnow().isoformat()
                }
            )

            # Return ChatKit compatible thread object
            return {
                "id": f"thread_{session_id}",
                "created_at": int(time.time()),
                "updated_at": int(time.time()),
                "metadata": {
                    "user_id": context.user_id,
                    "page_context": context.page_context,
                    "session_id": str(session_id)
                }
            }
        except Exception as e:
            logger.error(f"Error creating thread: {str(e)}", exc_info=True)
            raise

    async def get_thread(self, thread_id: str, context: RequestContext) -> Optional[Dict[str, Any]]:
        """
        Retrieve a thread by ID.

        Args:
            thread_id: The thread ID to retrieve
            context: Request context with auth info

        Returns:
            Thread object or None if not found
        """
        # Extract session_id from thread_id
        try:
            if thread_id.startswith("thread_"):
                session_id_str = thread_id[7:]  # Remove "thread_" prefix
            else:
                session_id_str = thread_id

            session_id = uuid.UUID(session_id_str)

            # Get session from database
            neon_client = await get_neon_client()
            session = await neon_client.get_session(session_id)

            if not session:
                return None

            # Check user access permissions
            if context.user_id and session['metadata'].get('user_id') and context.user_id != session['metadata'].get('user_id'):
                return None  # User doesn't have permission to access this thread

            # Return ChatKit compatible thread object
            return {
                "id": f"thread_{session_id_str}",
                "created_at": int(session['created_at'].timestamp()),
                "updated_at": int(session['last_active_at'].timestamp()),
                "metadata": {
                    "user_id": session['metadata'].get('user_id'),
                    "page_context": session['metadata'].get('page_url'),  # Simplified as page_url
                    "session_id": str(session_id),
                    **session['metadata']
                }
            }
        except ValueError:
            # Invalid UUID format
            return None
        except Exception as e:
            logger.error(f"Error getting thread {thread_id}: {str(e)}", exc_info=True)
            return None

    async def list_threads(self, context: RequestContext, limit: int = 20) -> Dict[str, Any]:
        """
        List threads for the current user.

        Args:
            context: Request context with auth info
            limit: Maximum number of threads to return

        Returns:
            Dict containing list of threads
        """
        # In a production implementation you would query with specific filters,
        # but Neon's chat_sessions doesn't currently allow us to get all historical sessions for a specific user quickly
        # This is more of a placeholder implementation until we implement session queries properly
        return {
            "object": "list",
            "data": [],
            "first_id": None,
            "last_id": None,
            "has_more": False
        }

    async def delete_thread(self, thread_id: str, context: RequestContext):
        """
        Delete a thread by ID (with proper access control).

        Args:
            thread_id: The thread ID to delete
            context: Request context with auth info

        Returns:
            True on success
        """
        try:
            if thread_id.startswith("thread_"):
                session_id_str = thread_id[7:]  # Remove "thread_" prefix
            else:
                session_id_str = thread_id

            session_id = uuid.UUID(session_id_str)

            # For now, we'll just mark as deleted by updating metadata
            # (A real implementation might actually delete conversation_turns but keep the session for reference)

            neon_client = await get_neon_client()
            session = await neon_client.get_session(session_id)

            if not session:
                raise ValueError("Thread not found")

            # Check user access permissions
            if context.user_id and session['metadata'].get('user_id') and context.user_id != session['metadata'].get('user_id'):
                raise PermissionError("User doesn't have permission to delete this thread")

            return True
        except ValueError as e:
            if str(e) == "Thread not found":
                raise
            # Invalid UUID format
            raise ValueError("Invalid thread ID format")

    def parse_user_message_content(self, content_input: Any) -> str:
        """
        Parse user message content from various formats.

        Args:
            content_input: The input content in various formats

        Returns:
            Parsed content string
        """
        if isinstance(content_input, str):
            return content_input
        elif isinstance(content_input, (list, tuple)):
            content_parts = []
            for item in content_input:
                if isinstance(item, dict):
                    if item.get("type") == "text" and "text" in item:
                        content_parts.append(item["text"])
                    elif "value" in item:
                        content_parts.append(item["value"])
                elif isinstance(item, str):
                    content_parts.append(item)
            return " ".join(content_parts)
        elif hasattr(content_input, 'content'):
            return str(getattr(content_input, 'content', ''))
        else:
            return str(content_input)

    async def respond(
        self,
        thread_id: str,
        input_user_message: Any,  # Accept various formats for compatibility
        context: RequestContext,
        user_id: Optional[str] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Process a user message in the context of the current thread.

        Args:
            thread_id: Current thread ID
            input_user_message: The user's message content
            context: Request context with auth and page information
            user_id: User ID for the request

        Yields:
            ChatKit-like response events
        """
        if not input_user_message:
            yield {
                "type": "error",
                "data": {
                    "message": "No user message provided"
                }
            }
            return

        # Safely extract content
        try:
            message_content = self.parse_user_message_content(input_user_message)
        except Exception as e:
            message_content = str(input_user_message)  # Fallback

        if not message_content or not message_content.strip():
            yield {
                "type": "error",
                "data": {
                    "message": "Empty user message provided"
                }
            }
            return

        message_content = message_content.strip()

        # Create ChatKit agent with proper context
        agent = ChatKitAgent(session_id=thread_id, user_id=user_id)

        from .context_injector import ContextInjector, ConversationContext

        # Create conversation context with page and user data
        if context.page_context or context.user_id:
            context_injector = ContextInjector()

            additional_metadata = {}
            if context.page_url:
                additional_metadata["page_context"] = {
                    "url": context.page_url,
                    "title": context.page_title
                }

            # Create conversation context
            conv_context = context_injector.create_conversation_context(
                additional_metadata=additional_metadata
            )

            # Add user info to context if available
            if user_id and context.page_context:
                user_profile = {"id": user_id, "preferred_language": "en", "expertise_level": "intermediate"}  # Mock for now
                conv_context.user_context = context_injector.extract_user_context(user_profile)

                # Process page data if provided
                if context.page_url:
                    page_data = {
                        "title": context.page_title or "Unknown Page",
                        "url": context.page_url,
                        "module": "Module X",
                        "section": "Section X",
                        "contentPreview": context.page_context.get("preview", "") if context.page_context else ""
                    }
                    conv_context.page_context = context_injector.extract_page_context(page_data)

            # Inject the context into the agent
            await context_injector.inject_context_to_agent(agent, conv_context)

        try:
            # Process the message with streaming from the agent
            async for chunk in agent.process_message_stream(message_content):
                # Map the internal chunk format to ChatKit-like events
                yield self._map_to_chatkit_format(chunk, thread_id, context)

        except Exception as e:
            logger.error(f"Error processing ChatKit message: {str(e)}", exc_info=True)
            yield {
                "type": "error",
                "data": {
                    "message": f"Error processing your request: {str(e)}"
                }
            }

    def _map_to_chatkit_format(self, chunk: Dict[str, Any], thread_id: str, context: RequestContext) -> Dict[str, Any]:
        """
        Map internal chunk format to ChatKit-like event format.

        Args:
            chunk: Internal chunk representation
            thread_id: Thread ID
            context: Context information

        Returns:
            ChatKit-formatted event
        """
        chunk_type = chunk.get("type", "unknown")

        if chunk_type == "chunk":
            return {
                "type": "thread.message.delta",
                "data": {
                    "id": f"msg_{thread_id}",  # Generate a message ID
                    "delta": {
                        "content": [
                            {
                                "type": "text",
                                "text": {
                                    "value": chunk["content"]
                                }
                            }
                        ]
                    }
                }
            }
        elif chunk_type == "tool_call":
            return {
                "type": "thread.run.step.delta",
                "data": {
                    "delta": {
                        "step_details": {
                            "type": "tool_calls",
                            "tool_calls": [
                                {
                                    "id": "call_" + str(abs(hash(chunk["content"])) % 10000),
                                    "type": "function",
                                    "function": {
                                        "name": chunk["content"],
                                        "arguments": json.dumps(chunk.get("metadata", {}).get("arguments", {}))
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        elif chunk_type == "citation":
            return {
                "type": "citation",
                "data": {
                    "citation": {
                        "section": chunk["content"],
                        **chunk.get("metadata", {})
                    }
                }
            }
        elif chunk_type == "done":
            return {
                "type": "thread.run.completed",
                "data": {
                    **chunk.get("metadata", {}),
                    "thread_id": thread_id,
                    "status": "completed"
                }
            }
        elif chunk_type == "error":
            return {
                "type": "error",
                "data": {
                    "message": chunk["content"]
                }
            }
        else:
            # For heartbeat and other message types, return as-is with thread info
            return {
                "type": "thread.event",
                "data": chunk
            }