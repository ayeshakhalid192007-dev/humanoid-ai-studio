"""
RAG Tools for ChatKit Agent

Defines tool functions for retrieval operations:
- retrieve_full_book: Semantic search across entire book
- answer_from_selected_text: Answer using only selected text

Author: Physical AI Platform Team
Date: 2026-02-12
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json

from ..services.embedder import Embedder
from ..services.retriever import Retriever
from ..config import get_settings


@dataclass
class RetrievalResult:
    """Result from a retrieval operation."""
    chunks: List[Dict[str, Any]]
    mode: str  # "full_book" or "selected_text"
    query: str
    context_text: str


class RAGTools:
    """
    RAG tool implementations for ChatKit agent.

    Provides two retrieval strategies:
    1. Full-book semantic search via Qdrant
    2. Selected-text-only answering (no retrieval)
    """

    def __init__(self):
        self.settings = get_settings()
        self.embedder = Embedder()
        self.retriever = Retriever()

    # =========================================================================
    # Tool Definitions (OpenAI Function Calling Format)
    # =========================================================================

    @staticmethod
    def get_tool_definitions() -> List[Dict[str, Any]]:
        """
        Return OpenAI-compatible tool definitions.

        These are passed to the ChatKit agent for function calling.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "retrieve_full_book",
                    "description": (
                        "Search the entire book for relevant content to answer the user's question. "
                        "Use this when the user asks a general question about robotics, ROS 2, "
                        "Gazebo, SLAM, or any topic covered in the curriculum. Returns the most "
                        "relevant passages from the book."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to find relevant book content"
                            },
                            "module_filter": {
                                "type": "string",
                                "description": "Optional: Filter results to a specific module (1, 2, 3, or 4)",
                                "enum": ["1", "2", "3", "4"]
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Number of results to return (default: 5, max: 10)",
                                "default": 5,
                                "minimum": 1,
                                "maximum": 10
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "answer_from_selected_text",
                    "description": (
                        "Answer a question using ONLY the text that the user has selected/highlighted. "
                        "Use this when the user provides specific text and asks a question about it. "
                        "Do NOT search the broader book - only use the provided text. If the answer "
                        "cannot be found in the selected text, indicate that clearly."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "selected_text": {
                                "type": "string",
                                "description": "The exact text the user has selected/highlighted"
                            },
                            "question": {
                                "type": "string",
                                "description": "The user's question about the selected text"
                            }
                        },
                        "required": ["selected_text", "question"]
                    }
                }
            }
        ]

    # =========================================================================
    # Tool Implementations
    # =========================================================================

    async def retrieve_full_book(
        self,
        query: str,
        module_filter: Optional[str] = None,
        top_k: int = 5
    ) -> RetrievalResult:
        """
        Perform semantic search across the entire book.

        Args:
            query: Search query
            module_filter: Optional module filter (1-4)
            top_k: Number of results to return

        Returns:
            RetrievalResult with chunks and formatted context
        """
        # Generate query embedding
        query_embedding = await self.embedder.embed_text(query)

        # Search Qdrant
        chunks = await self.retriever.search(
            query_embedding=query_embedding,
            limit=min(top_k, 10),  # Cap at 10
            module_filter=module_filter
        )

        # Format context for LLM
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Source {i}] Module {chunk['module']}, {chunk['section_title']}:\n"
                f"{chunk['text']}\n"
            )

        context_text = "\n".join(context_parts) if context_parts else ""

        return RetrievalResult(
            chunks=chunks,
            mode="full_book",
            query=query,
            context_text=context_text
        )

    async def answer_from_selected_text(
        self,
        selected_text: str,
        question: str
    ) -> RetrievalResult:
        """
        Prepare context from user-selected text only.

        This does NOT perform any retrieval - it simply formats
        the selected text as the sole context for answering.

        Args:
            selected_text: User's highlighted text
            question: User's question about the text

        Returns:
            RetrievalResult with selected text as context
        """
        # Create a pseudo-chunk for consistency
        chunk = {
            "chunk_id": "selected_text",
            "text": selected_text,
            "module": "user_selection",
            "lesson": "N/A",
            "section_title": "Selected Text",
            "url": "",
            "score": 1.0
        }

        context_text = (
            "[SELECTED TEXT - Answer ONLY from this content]\n"
            f"{selected_text}\n\n"
            "IMPORTANT: If the answer to the question cannot be found in the "
            "selected text above, respond with: 'The selected text does not "
            "contain information to answer this question.'"
        )

        return RetrievalResult(
            chunks=[chunk],
            mode="selected_text",
            query=question,
            context_text=context_text
        )

    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> RetrievalResult:
        """
        Execute a tool by name with given arguments.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments as dict

        Returns:
            RetrievalResult from tool execution

        Raises:
            ValueError: If tool name is unknown
        """
        if tool_name == "retrieve_full_book":
            return await self.retrieve_full_book(
                query=arguments["query"],
                module_filter=arguments.get("module_filter"),
                top_k=arguments.get("top_k", 5)
            )
        elif tool_name == "answer_from_selected_text":
            return await self.answer_from_selected_text(
                selected_text=arguments["selected_text"],
                question=arguments["question"]
            )
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
