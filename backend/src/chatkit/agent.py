"""
ChatKit Agent - Conversational RAG Orchestration

Manages conversation state, tool calling, and response generation
using OpenAI's chat completions API with function calling.

Author: Physical AI Platform Team
Date: 2026-02-12
"""

from typing import List, Dict, Any, Optional, AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime
import json
import uuid

from .tools import RAGTools, RetrievalResult
from ..config import get_settings
from ..ai.gemini_client import get_gemini_client
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ConversationMessage:
    """A single message in the conversation."""
    role: str  # "system", "user", "assistant", "tool"
    content: str
    name: Optional[str] = None  # For tool messages
    tool_call_id: Optional[str] = None  # For tool responses
    tool_calls: Optional[List[Dict]] = None  # For assistant tool requests
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ConversationState:
    """Tracks the state of a conversation session."""
    session_id: str
    user_id: Optional[str] = None
    messages: List[ConversationMessage] = field(default_factory=list)
    retrieval_history: List[RetrievalResult] = field(default_factory=list)
    mode: str = "full_book"  # "full_book" or "selected_text"
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)


class ChatKitAgent:
    """
    ChatKit-style agent for RAG-based conversation.

    Features:
    - Tool-based retrieval (full-book search, selected-text answering)
    - Multi-turn conversation with context
    - Streaming response support
    - Automatic tool execution
    """

    def __init__(self, session_id: Optional[str] = None, user_id: Optional[str] = None):
        """
        Initialize ChatKit agent.

        Args:
            session_id: Existing session ID or None to create new
            user_id: Optional user ID from auth session
        """
        self.settings = get_settings()
        self.client = get_gemini_client()
        self.tools = RAGTools()

        self.state = ConversationState(
            session_id=session_id or str(uuid.uuid4()),
            user_id=user_id
        )

        # Initialize with system prompt
        self._init_system_prompt()

    def _init_system_prompt(self) -> None:
        """Set up the system prompt for the agent."""
        system_prompt = """You are an expert AI assistant for the Physical AI & Humanoid Robotics curriculum book.

Your role is to help readers understand concepts from the book by:
1. Answering questions using retrieved book content
2. Explaining complex robotics concepts clearly
3. Providing code examples and debugging guidance
4. Giving hints for exercises without revealing full solutions

IMPORTANT RULES:
- ALWAYS use the available tools to retrieve relevant content before answering
- For general questions, use retrieve_full_book to search the curriculum
- When the user provides selected/highlighted text, use answer_from_selected_text
- Base your answers ONLY on the retrieved content - do not make up information
- If content is insufficient, say so and suggest related topics from the curriculum
- Cite sources using format: "According to Module X, Lesson Y: [content]"

Available curriculum modules:
- Module 1: ROS 2 Foundations (URDF, launch files, transforms)
- Module 2: Gazebo Simulation (worlds, sensors, physics)
- Module 3: VSLAM & Navigation (mapping, localization, path planning)
- Module 4: Voice-Language-Action Systems (LLM integration, embodied AI)

Be helpful, accurate, and educational. If a question is off-topic, politely redirect to curriculum topics."""

        self.state.messages.append(ConversationMessage(
            role="system",
            content=system_prompt
        ))

    def set_mode(self, mode: str) -> None:
        """
        Set the answering mode.

        Args:
            mode: "full_book" for RAG search, "selected_text" for selected text only
        """
        if mode not in ("full_book", "selected_text"):
            raise ValueError(f"Invalid mode: {mode}. Must be 'full_book' or 'selected_text'")
        self.state.mode = mode
        logger.info(f"Session {self.state.session_id}: Mode set to {mode}")

    def _format_messages_for_api(self) -> List[Dict[str, Any]]:
        """Convert conversation messages to OpenAI API format."""
        api_messages = []

        for msg in self.state.messages:
            api_msg = {"role": msg.role, "content": msg.content}

            if msg.name:
                api_msg["name"] = msg.name
            if msg.tool_call_id:
                api_msg["tool_call_id"] = msg.tool_call_id
            if msg.tool_calls:
                api_msg["tool_calls"] = msg.tool_calls
                # When there are tool_calls, content might be None
                if not msg.content:
                    api_msg["content"] = None

            api_messages.append(api_msg)

        return api_messages

    async def process_message(
        self,
        user_message: str,
        selected_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and generate a response.

        This is the main entry point for non-streaming interactions.

        Args:
            user_message: The user's question/message
            selected_text: Optional selected text for selected_text mode

        Returns:
            Dict with:
                - answer: The generated response
                - citations: List of citations used
                - mode: The answering mode used
                - tool_calls: List of tools that were called
        """
        # Add user message to conversation
        self.state.messages.append(ConversationMessage(
            role="user",
            content=user_message
        ))
        self.state.last_active = datetime.utcnow()

        # If selected text provided, switch to selected_text mode
        if selected_text:
            self.set_mode("selected_text")
            # Pre-execute the selected text tool to inject context
            retrieval = await self.tools.answer_from_selected_text(
                selected_text=selected_text,
                question=user_message
            )
            self.state.retrieval_history.append(retrieval)

            # Add context as a system message
            context_msg = ConversationMessage(
                role="system",
                content=f"User has selected the following text:\n{retrieval.context_text}"
            )
            self.state.messages.append(context_msg)

        # Get tool definitions
        tool_defs = RAGTools.get_tool_definitions()

        # Call OpenAI API with tools
        messages = self._format_messages_for_api()

        response = await self.client.chat.completions.create(
            model=self.settings.OPENAI_CHAT_MODEL,
            messages=messages,
            tools=tool_defs,
            tool_choice="auto",
            temperature=self.settings.OPENAI_TEMPERATURE,
            max_tokens=self.settings.OPENAI_MAX_TOKENS
        )

        assistant_message = response.choices[0].message
        tool_calls_made = []

        # Handle tool calls if present
        if assistant_message.tool_calls:
            # Add assistant message with tool calls
            self.state.messages.append(ConversationMessage(
                role="assistant",
                content=assistant_message.content or "",
                tool_calls=[tc.model_dump() for tc in assistant_message.tool_calls]
            ))

            # Execute each tool call
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                tool_calls_made.append({"name": tool_name, "arguments": tool_args})

                # Execute the tool
                retrieval = await self.tools.execute_tool(tool_name, tool_args)
                self.state.retrieval_history.append(retrieval)

                # Add tool result to conversation
                self.state.messages.append(ConversationMessage(
                    role="tool",
                    content=retrieval.context_text,
                    name=tool_name,
                    tool_call_id=tool_call.id
                ))

            # Get final response after tool execution
            messages = self._format_messages_for_api()
            final_response = await self.client.chat.completions.create(
                model=self.settings.OPENAI_CHAT_MODEL,
                messages=messages,
                temperature=self.settings.OPENAI_TEMPERATURE,
                max_tokens=self.settings.OPENAI_MAX_TOKENS
            )
            final_content = final_response.choices[0].message.content
        else:
            final_content = assistant_message.content

        # Add final assistant response
        self.state.messages.append(ConversationMessage(
            role="assistant",
            content=final_content
        ))

        # Build citations from retrieval history
        citations = []
        if self.state.retrieval_history:
            latest_retrieval = self.state.retrieval_history[-1]
            for chunk in latest_retrieval.chunks:
                if chunk.get("module") != "user_selection":
                    citations.append({
                        "module": chunk.get("module", ""),
                        "lesson": chunk.get("lesson", ""),
                        "section": chunk.get("section_title", ""),
                        "url": chunk.get("url", "")
                    })

        return {
            "answer": final_content,
            "citations": citations[:3],  # Top 3 citations
            "mode": self.state.mode,
            "tool_calls": tool_calls_made,
            "session_id": self.state.session_id
        }

    async def process_message_stream(
        self,
        user_message: str,
        selected_text: Optional[str] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Process a user message with streaming response.

        Yields chunks as they're generated.

        Args:
            user_message: The user's question
            selected_text: Optional selected text

        Yields:
            Dict chunks with:
                - type: "chunk" | "tool_call" | "citation" | "done"
                - content: The chunk content
                - metadata: Additional info
        """
        # Add user message
        self.state.messages.append(ConversationMessage(
            role="user",
            content=user_message
        ))
        self.state.last_active = datetime.utcnow()

        # Handle selected text mode
        if selected_text:
            self.set_mode("selected_text")
            retrieval = await self.tools.answer_from_selected_text(
                selected_text=selected_text,
                question=user_message
            )
            self.state.retrieval_history.append(retrieval)

            self.state.messages.append(ConversationMessage(
                role="system",
                content=f"User has selected the following text:\n{retrieval.context_text}"
            ))

        tool_defs = RAGTools.get_tool_definitions()
        messages = self._format_messages_for_api()

        # First API call to check for tool usage
        response = await self.client.chat.completions.create(
            model=self.settings.OPENAI_CHAT_MODEL,
            messages=messages,
            tools=tool_defs,
            tool_choice="auto",
            temperature=self.settings.OPENAI_TEMPERATURE,
            max_tokens=self.settings.OPENAI_MAX_TOKENS
        )

        assistant_message = response.choices[0].message

        # Handle tool calls
        if assistant_message.tool_calls:
            self.state.messages.append(ConversationMessage(
                role="assistant",
                content=assistant_message.content or "",
                tool_calls=[tc.model_dump() for tc in assistant_message.tool_calls]
            ))

            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                yield {
                    "type": "tool_call",
                    "content": tool_name,
                    "metadata": {"arguments": tool_args}
                }

                retrieval = await self.tools.execute_tool(tool_name, tool_args)
                self.state.retrieval_history.append(retrieval)

                self.state.messages.append(ConversationMessage(
                    role="tool",
                    content=retrieval.context_text,
                    name=tool_name,
                    tool_call_id=tool_call.id
                ))

            messages = self._format_messages_for_api()

        # Stream the final response
        stream = await self.client.chat.completions.create(
            model=self.settings.OPENAI_CHAT_MODEL,
            messages=messages,
            temperature=self.settings.OPENAI_TEMPERATURE,
            max_tokens=self.settings.OPENAI_MAX_TOKENS,
            stream=True
        )

        full_content = ""
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_content += content
                yield {
                    "type": "chunk",
                    "content": content,
                    "metadata": {}
                }

        # Add complete response to conversation
        self.state.messages.append(ConversationMessage(
            role="assistant",
            content=full_content
        ))

        # Yield citations
        if self.state.retrieval_history:
            latest_retrieval = self.state.retrieval_history[-1]
            for chunk in latest_retrieval.chunks[:3]:
                if chunk.get("module") != "user_selection":
                    yield {
                        "type": "citation",
                        "content": chunk.get("section_title", ""),
                        "metadata": {
                            "module": chunk.get("module", ""),
                            "lesson": chunk.get("lesson", ""),
                            "url": chunk.get("url", "")
                        }
                    }

        yield {
            "type": "done",
            "content": "",
            "metadata": {
                "session_id": self.state.session_id,
                "mode": self.state.mode,
                "total_length": len(full_content)
            }
        }

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        Get the conversation history for persistence.

        Returns:
            List of message dicts suitable for storage
        """
        history = []
        for msg in self.state.messages:
            if msg.role in ("user", "assistant"):
                history.append({
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                })
        return history

    def restore_conversation(self, history: List[Dict[str, Any]]) -> None:
        """
        Restore conversation from stored history.

        Args:
            history: List of message dicts from get_conversation_history
        """
        for msg in history:
            self.state.messages.append(ConversationMessage(
                role=msg["role"],
                content=msg["content"],
                timestamp=datetime.fromisoformat(msg["timestamp"])
            ))
