"""
RAG Pipeline - Orchestration Service

Orchestrates the complete Retrieve → Augment → Generate flow.
Includes input sanitization and validation.

Author: Physical AI Platform Team
Date: 2026-02-09
"""
import re
from typing import Dict, Any, List, Optional

from .embedder import Embedder
from .retriever import Retriever
from .generator import Generator


class RAGPipeline:
    """
    Orchestrates the RAG (Retrieval-Augmented Generation) pipeline.

    Flow:
    1. Sanitize and validate input query
    2. Generate query embedding
    3. Retrieve relevant curriculum chunks
    4. Generate answer with citations
    """

    def __init__(self):
        self.embedder = Embedder()
        self.retriever = Retriever()
        self.generator = Generator()

        # Dangerous tokens to strip (FR-046)
        self.dangerous_tokens = [
            "<|endoftext|>",
            "<|im_sep|>",
            "<|im_start|>",
            "<|im_end|>"
        ]

    def sanitize_query(self, query: str) -> str:
        """
        Sanitize user input query (FR-046).

        - Strip dangerous tokens
        - Remove excessive whitespace
        - Validate length (1-500 chars)

        Raises:
            ValueError: If query is invalid
        """
        # Strip dangerous tokens
        for token in self.dangerous_tokens:
            query = query.replace(token, "")

        # Remove excessive whitespace
        query = " ".join(query.split())

        # Validate length
        if len(query) < 1:
            raise ValueError("Query is too short (minimum 1 character)")
        if len(query) > 500:
            raise ValueError("Query is too long (maximum 500 characters)")

        return query

    async def process_query(
        self,
        query: str,
        session_id: str,
        page_context: Optional[str] = None,
        selection_text: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Process a complete RAG query.

        Args:
            query: User's question
            session_id: Session ID for rate limiting/logging
            page_context: Current page URL (optional)
            selection_text: Highlighted text (optional, FR-052)
            conversation_history: Previous turns for context

        Returns:
            Dict with answer, citations, and retrieved_chunks

        Raises:
            ValueError: Invalid input
            RuntimeError: Pipeline execution error
        """
        # Step 1: Sanitize input
        sanitized_query = self.sanitize_query(query)

        # Augment query with selection text if provided
        if selection_text:
            augmented_query = f"{sanitized_query}\n\nContext (selected text): {selection_text}"
        else:
            augmented_query = sanitized_query

        # Step 2: Generate query embedding
        query_embedding = await self.embedder.embed_text(augmented_query)

        # Step 3: Retrieve relevant chunks
        retrieved_chunks = await self.retriever.search(
            query_embedding=query_embedding,
            limit=5
        )

        # Check if retrieval found relevant content
        if not retrieved_chunks:
            return {
                "answer": "I don't have specific curriculum content to answer that question. Could you rephrase or ask about topics like ROS 2, Gazebo simulation, VSLAM, or voice-language-action systems?",
                "citations": [],
                "retrieved_chunks": []
            }

        # Step 4: Generate answer
        generation_result = await self.generator.generate(
            query=sanitized_query,
            retrieved_chunks=retrieved_chunks,
            conversation_history=conversation_history
        )

        # Format retrieved chunks for response (preview only)
        formatted_chunks = [
            {
                "text": chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"],
                "score": round(chunk["score"], 3),
                "module": chunk["module"],
                "section": chunk["section_title"]
            }
            for chunk in retrieved_chunks
        ]

        return {
            "answer": generation_result["answer"],
            "citations": generation_result["citations"],
            "retrieved_chunks": formatted_chunks
        }
