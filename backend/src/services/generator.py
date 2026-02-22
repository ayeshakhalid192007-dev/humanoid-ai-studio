"""
Generator Service - OpenAI Agents SDK Integration

Generates curriculum-grounded answers with citations using OpenAI API.
Implements context window management and citation formatting.

Author: Physical AI Platform Team
Date: 2026-02-09
"""
from typing import List, Dict, Any
import openai
from openai import AsyncOpenAI

from ..config import get_settings


class Generator:
    """
    Handles answer generation using OpenAI LLM with RAG context.

    Features:
    - Curriculum-scoped system prompt
    - Context window management (<8k tokens)
    - Citation formatting
    - Streaming support for typing indicators
    """

    def __init__(self):
        self.settings = get_settings()
        self.client = AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"
        self.max_context_tokens = 8000  # FR-040

        self.system_prompt = """You are a helpful AI assistant for the Physical AI & Humanoid Robotics curriculum.

Your role is to answer student questions based ONLY on the provided curriculum content. Follow these rules:

1. Answer using ONLY information from the retrieved curriculum chunks
2. Cite specific modules and lessons when referencing content
3. If the question is off-topic (not about robotics/AI), politely decline and suggest curriculum topics
4. If you don't have enough context, ask clarifying questions referencing specific modules
5. For code debugging questions, provide step-by-step diagnostic procedures from the curriculum
6. For prediction-phase exercises, give hints without revealing full solutions

Citation format: "According to Module X, Lesson Y: [content]"

CRITICAL: If the answer is not found in the provided context, you MUST respond:
"The answer is not available in this textbook." Do NOT attempt to answer from your general knowledge.

Be concise, accurate, and educational."""

    async def generate(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Generate answer based on query and retrieved context.

        Args:
            query: User's question
            retrieved_chunks: List of relevant curriculum chunks from retriever
            conversation_history: Optional previous turns for context

        Returns:
            Dict with 'answer' and 'citations' fields
        """
        # Build context and messages using shared helper
        context, citations = self._build_context(retrieved_chunks)
        messages = self._build_messages(query, context, conversation_history)

        try:
            # Generate answer
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            answer = response.choices[0].message.content

            return {
                "answer": answer,
                "citations": citations[:3]  # Return top 3 citations
            }

        except Exception as e:
            raise RuntimeError(f"Answer generation failed: {str(e)}")

    def _build_context(self, retrieved_chunks: List[Dict[str, Any]]) -> tuple:
        """
        Build context from retrieved chunks and extract citations.

        Args:
            retrieved_chunks: List of relevant curriculum chunks from retriever

        Returns:
            Tuple of (context string, citations list)
        """
        context_parts = []
        citations = []

        for i, chunk in enumerate(retrieved_chunks, 1):
            context_parts.append(
                f"[Source {i}] Module {chunk['module']}, {chunk['section_title']}:\n{chunk['text']}\n"
            )
            citations.append({
                "module": chunk["module"],
                "lesson": chunk["lesson"],
                "section": chunk["section_title"],
                "url": chunk["url"]
            })

        context = "\n".join(context_parts)
        return context, citations

    def _build_messages(self, query: str, context: str, conversation_history: List[Dict[str, str]] = None) -> List[Dict[str, str]]:
        """
        Build the message history for the OpenAI API call.

        Args:
            query: User's question
            context: Retrieved curriculum context
            conversation_history: Optional previous turns for context

        Returns:
            List of message dictionaries for the OpenAI API
        """
        # Truncate if exceeds token limit (rough estimate: 1 token ≈ 4 chars)
        max_context_chars = self.max_context_tokens * 4 - len(query) * 4 - 1000
        if len(context) > max_context_chars:
            context = context[:max_context_chars] + "\n[Context truncated...]"

        # Build messages
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]

        # Add conversation history if provided (last 3 turns)
        if conversation_history:
            for turn in conversation_history[-3:]:
                messages.append({"role": "user", "content": turn.get("query", "")})
                messages.append({"role": "assistant", "content": turn.get("response", "")})

        # Add current query with context
        user_message = f"Context from curriculum:\n{context}\n\nStudent question: {query}"
        messages.append({"role": "user", "content": user_message})

        return messages

    async def generate_stream(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        conversation_history: List[Dict[str, str]] = None
    ):
        """
        Generate answer with streaming for typing indicators (FR-053).

        Yields answer chunks as they're generated via OpenAI streaming API.

        Args:
            query: User's question
            retrieved_chunks: Relevant curriculum chunks from retriever
            conversation_history: Optional previous turns for context

        Yields:
            str: Answer text chunks as they arrive
        """
        # Build context and messages using shared helper
        context, _ = self._build_context(retrieved_chunks)
        messages = self._build_messages(query, context, conversation_history)

        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500,
                stream=True
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise RuntimeError(f"Streaming generation failed: {str(e)}")
