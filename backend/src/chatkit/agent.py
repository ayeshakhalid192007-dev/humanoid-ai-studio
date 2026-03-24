"""
ChatKit Agent - Conversational RAG Orchestration

Uses native google-genai SDK for Gemini chat, streaming, and function calling.

Author: Physical AI Platform Team
Date: 2026-03-24
"""

from typing import List, Dict, Any, Optional, AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime
import json
import uuid

from google.genai import types as genai_types

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
    tool_call_id: Optional[str] = None  # For tool responses (kept for compat)
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
        self.settings = get_settings()
        self.client = get_gemini_client()
        self.tools = RAGTools()

        self.state = ConversationState(
            session_id=session_id or str(uuid.uuid4()),
            user_id=user_id
        )

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
        """Set the answering mode."""
        if mode not in ("full_book", "selected_text"):
            raise ValueError(f"Invalid mode: {mode}. Must be 'full_book' or 'selected_text'")
        self.state.mode = mode
        logger.info(f"Session {self.state.session_id}: Mode set to {mode}")

    def _format_contents_for_api(self) -> tuple:
        """
        Convert conversation messages to google-genai Contents format.

        Returns:
            (contents, system_instruction) tuple.
            System messages are extracted as system_instruction.
            Tool messages are represented as function_response Parts.
        """
        system_instruction = ""
        contents = []

        i = 0
        msgs = self.state.messages
        while i < len(msgs):
            msg = msgs[i]

            if msg.role == "system":
                if system_instruction:
                    system_instruction += "\n\n" + msg.content
                else:
                    system_instruction = msg.content
                i += 1
                continue

            if msg.role == "user":
                contents.append(genai_types.Content(
                    role="user",
                    parts=[genai_types.Part(text=msg.content)]
                ))
                i += 1
                continue

            if msg.role == "assistant":
                if msg.tool_calls:
                    parts = []
                    for tc in msg.tool_calls:
                        fn = tc.get("function", {})
                        args = fn.get("arguments", "{}")
                        if isinstance(args, str):
                            try:
                                args = json.loads(args)
                            except json.JSONDecodeError:
                                args = {}
                        parts.append(genai_types.Part(
                            function_call=genai_types.FunctionCall(
                                name=fn.get("name", ""),
                                args=args
                            )
                        ))
                    contents.append(genai_types.Content(role="model", parts=parts))
                else:
                    contents.append(genai_types.Content(
                        role="model",
                        parts=[genai_types.Part(text=msg.content or "")]
                    ))
                i += 1
                continue

            if msg.role == "tool":
                result_value = msg.content
                try:
                    result_value = json.loads(msg.content)
                except (json.JSONDecodeError, TypeError):
                    result_value = {"result": msg.content}

                contents.append(genai_types.Content(
                    role="user",
                    parts=[genai_types.Part(
                        function_response=genai_types.FunctionResponse(
                            name=msg.name or "tool",
                            response={"output": result_value}
                        )
                    )]
                ))
                i += 1
                continue

            i += 1

        return contents, system_instruction

    def _build_genai_tools(self) -> list:
        """Convert RAG tool definitions to google-genai Tool format."""
        tool_defs = RAGTools.get_tool_definitions()
        fn_declarations = []
        for t in tool_defs:
            fn = t["function"]
            fn_declarations.append(genai_types.FunctionDeclaration(
                name=fn["name"],
                description=fn.get("description", ""),
                parameters=fn.get("parameters", {})
            ))
        return [genai_types.Tool(function_declarations=fn_declarations)]

    async def process_message(
        self,
        user_message: str,
        selected_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and generate a response.

        Returns:
            Dict with answer, citations, mode, tool_calls, session_id.
        """
        self.state.messages.append(ConversationMessage(
            role="user",
            content=user_message
        ))
        self.state.last_active = datetime.utcnow()

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

        genai_tools = self._build_genai_tools()
        contents, system_instruction = self._format_contents_for_api()

        config = genai_types.GenerateContentConfig(
            temperature=self.settings.OPENAI_TEMPERATURE,
            max_output_tokens=self.settings.OPENAI_MAX_TOKENS,
            system_instruction=system_instruction or None,
            tools=genai_tools,
        )

        response = await self.client.aio.models.generate_content(
            model=self.settings.OPENAI_CHAT_MODEL,
            contents=contents,
            config=config,
        )

        tool_calls_made = []

        fn_call_parts = []
        if response.candidates:
            fn_call_parts = [
                p for p in (response.candidates[0].content.parts or [])
                if p.function_call is not None
            ]

        if fn_call_parts:
            self.state.messages.append(ConversationMessage(
                role="assistant",
                content="",
                tool_calls=[
                    {
                        "function": {
                            "name": p.function_call.name,
                            "arguments": json.dumps(dict(p.function_call.args))
                        }
                    }
                    for p in fn_call_parts
                ]
            ))

            for part in fn_call_parts:
                fn_name = part.function_call.name
                fn_args = dict(part.function_call.args)
                logger.info(f"Executing tool: {fn_name} with args: {fn_args}")
                tool_calls_made.append({"name": fn_name, "arguments": fn_args})

                retrieval = await self.tools.execute_tool(fn_name, fn_args)
                self.state.retrieval_history.append(retrieval)

                self.state.messages.append(ConversationMessage(
                    role="tool",
                    content=retrieval.context_text,
                    name=fn_name,
                ))

            contents, _ = self._format_contents_for_api()
            final_config = genai_types.GenerateContentConfig(
                temperature=self.settings.OPENAI_TEMPERATURE,
                max_output_tokens=self.settings.OPENAI_MAX_TOKENS,
                system_instruction=system_instruction or None,
            )
            final_response = await self.client.aio.models.generate_content(
                model=self.settings.OPENAI_CHAT_MODEL,
                contents=contents,
                config=final_config,
            )
            final_content = final_response.text or ""
        else:
            final_content = response.text or ""

        self.state.messages.append(ConversationMessage(
            role="assistant",
            content=final_content
        ))

        citations = []
        if self.state.retrieval_history:
            latest = self.state.retrieval_history[-1]
            for chunk in latest.chunks:
                if chunk.get("module") != "user_selection":
                    citations.append({
                        "module": chunk.get("module", ""),
                        "lesson": chunk.get("lesson", ""),
                        "section": chunk.get("section_title", ""),
                        "url": chunk.get("url", "")
                    })

        return {
            "answer": final_content,
            "citations": citations[:3],
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
        Process a user message with streaming response via google-genai.

        Yields chunks as they're generated.
        """
        self.state.messages.append(ConversationMessage(
            role="user",
            content=user_message
        ))
        self.state.last_active = datetime.utcnow()

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

        genai_tools = self._build_genai_tools()
        contents, system_instruction = self._format_contents_for_api()

        config = genai_types.GenerateContentConfig(
            temperature=self.settings.OPENAI_TEMPERATURE,
            max_output_tokens=self.settings.OPENAI_MAX_TOKENS,
            system_instruction=system_instruction or None,
            tools=genai_tools,
        )

        # Non-streaming first call to detect tool use
        response = await self.client.aio.models.generate_content(
            model=self.settings.OPENAI_CHAT_MODEL,
            contents=contents,
            config=config,
        )

        fn_call_parts = []
        if response.candidates:
            fn_call_parts = [
                p for p in (response.candidates[0].content.parts or [])
                if p.function_call is not None
            ]

        if fn_call_parts:
            self.state.messages.append(ConversationMessage(
                role="assistant",
                content="",
                tool_calls=[
                    {
                        "function": {
                            "name": p.function_call.name,
                            "arguments": json.dumps(dict(p.function_call.args))
                        }
                    }
                    for p in fn_call_parts
                ]
            ))

            for part in fn_call_parts:
                fn_name = part.function_call.name
                fn_args = dict(part.function_call.args)

                yield {
                    "type": "tool_call",
                    "content": fn_name,
                    "metadata": {"arguments": fn_args}
                }

                retrieval = await self.tools.execute_tool(fn_name, fn_args)
                self.state.retrieval_history.append(retrieval)

                self.state.messages.append(ConversationMessage(
                    role="tool",
                    content=retrieval.context_text,
                    name=fn_name,
                ))

            contents, _ = self._format_contents_for_api()

        # Streaming final response
        stream_config = genai_types.GenerateContentConfig(
            temperature=self.settings.OPENAI_TEMPERATURE,
            max_output_tokens=self.settings.OPENAI_MAX_TOKENS,
            system_instruction=system_instruction or None,
        )

        full_content = ""
        async for chunk in await self.client.aio.models.generate_content_stream(
            model=self.settings.OPENAI_CHAT_MODEL,
            contents=contents,
            config=stream_config,
        ):
            text = chunk.text or ""
            if text:
                full_content += text
                yield {
                    "type": "chunk",
                    "content": text,
                    "metadata": {}
                }

        self.state.messages.append(ConversationMessage(
            role="assistant",
            content=full_content
        ))

        if self.state.retrieval_history:
            latest = self.state.retrieval_history[-1]
            for chunk in latest.chunks[:3]:
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
        """Get the conversation history for persistence."""
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
        """Restore conversation from stored history."""
        for msg in history:
            self.state.messages.append(ConversationMessage(
                role=msg["role"],
                content=msg["content"],
                timestamp=datetime.fromisoformat(msg["timestamp"])
            ))
