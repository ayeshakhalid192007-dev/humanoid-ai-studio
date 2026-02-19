"""
Pydantic models for chat API requests and responses.

Defines data schemas for:
- ChatRequest: Student query with session context
- ChatResponse: RAG answer with citations and metadata
- Citation: Book reference for answer sources

Author: Physical AI Platform Team
Date: 2026-02-09
"""
from pydantic import BaseModel, Field, field_validator, UUID4
from typing import Optional, List
from datetime import datetime


# ============================================================================
# Request Models
# ============================================================================

class ChatRequest(BaseModel):
    """
    Student chat query with context.

    Example:
        {
            "query": "What are URDF joint limits?",
            "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "page_context": "https://example.com/docs/module1/lesson3",
            "selection_text": "joint limits"
        }
    """

    query: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Student's question (1-500 characters)",
        examples=["What are URDF joint limits?"],
    )

    session_id: UUID4 = Field(
        ...,
        description="Browser session ID (UUID v4 from sessionStorage)",
        examples=["a1b2c3d4-e5f6-7890-abcd-ef1234567890"],
    )

    page_context: Optional[str] = Field(
        None,
        max_length=500,
        description="Current book page URL when query submitted",
        examples=["https://example.com/docs/module1/lesson3"],
    )

    selection_text: Optional[str] = Field(
        None,
        max_length=500,
        description="Highlighted text from book page (optional)",
        examples=["joint limits"],
    )

    @field_validator("query")
    @classmethod
    def sanitize_query(cls, v: str) -> str:
        """
        Sanitize query input by removing special tokens.

        Removes:
        - <|endoftext|>
        - <|im_sep|>
        - <|im_start|>
        - <|im_end|>
        - Other LLM control tokens

        Per FR-046: Input sanitization requirement
        """
        special_tokens = [
            "<|endoftext|>",
            "<|im_sep|>",
            "<|im_start|>",
            "<|im_end|>",
            "<|system|>",
            "<|user|>",
            "<|assistant|>",
        ]

        sanitized = v
        for token in special_tokens:
            sanitized = sanitized.replace(token, "")

        # Remove any remaining angle bracket sequences
        import re
        sanitized = re.sub(r"<\|[^|]*\|>", "", sanitized)

        # Strip leading/trailing whitespace
        sanitized = sanitized.strip()

        return sanitized


# ============================================================================
# Response Models
# ============================================================================

class Citation(BaseModel):
    """
    Book reference citing source of answer.

    Example:
        {
            "module": "1",
            "lesson": "lesson-3",
            "section": "Joint Constraints and Workspace",
            "url": "https://example.com/docs/module1/lesson3#joints"
        }
    """

    module: str = Field(
        ...,
        description="Module number (1-4)",
        examples=["1"],
    )

    lesson: str = Field(
        ...,
        description="Lesson identifier (e.g., lesson-3)",
        examples=["lesson-3"],
    )

    section: str = Field(
        ...,
        max_length=200,
        description="Section heading from curriculum",
        examples=["Joint Constraints and Workspace"],
    )

    url: str = Field(
        ...,
        description="Clickable link to book section",
        examples=["https://example.com/docs/module1/lesson3#joints"],
    )


class RetrievedChunk(BaseModel):
    """
    Curriculum chunk retrieved during RAG search.

    Example:
        {
            "chunk_id": "550e8400-e29b-41d4-a716-446655440000",
            "text_preview": "URDF joints define the kinematic relationships...",
            "score": 0.89,
            "module": "1",
            "lesson": "lesson-3",
            "section_title": "Joint Constraints",
            "url": "https://example.com/docs/module1/lesson3#joints"
        }
    """

    chunk_id: str = Field(
        ...,
        description="UUID of curriculum chunk",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )

    text_preview: str = Field(
        ...,
        max_length=200,
        description="Preview of chunk text (max 200 chars)",
        examples=["URDF joints define the kinematic relationships between rigid bodies..."],
    )

    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Cosine similarity score (0.0-1.0)",
        examples=[0.89],
    )

    module: str = Field(
        ...,
        description="Module number",
        examples=["1"],
    )

    lesson: str = Field(
        ...,
        description="Lesson identifier",
        examples=["lesson-3"],
    )

    section_title: str = Field(
        ...,
        max_length=200,
        description="Section heading",
        examples=["Joint Constraints"],
    )

    url: str = Field(
        ...,
        description="Book page URL",
        examples=["https://example.com/docs/module1/lesson3#joints"],
    )


class ChatResponse(BaseModel):
    """
    RAG chatbot response with answer and citations.

    Example:
        {
            "answer": "According to Module 1, Lesson 3, URDF joint limits...",
            "citations": [
                {
                    "module": "1",
                    "lesson": "lesson-3",
                    "section": "Joint Constraints",
                    "url": "https://example.com/docs/module1/lesson3#joints"
                }
            ],
            "retrieved_chunks": [
                {
                    "chunk_id": "550e...",
                    "text_preview": "URDF joints define...",
                    "score": 0.89,
                    "module": "1",
                    "lesson": "lesson-3",
                    "section_title": "Joint Constraints",
                    "url": "https://example.com/docs/module1/lesson3#joints"
                }
            ],
            "timestamp": "2026-02-09T14:30:45.123Z"
        }
    """

    answer: str = Field(
        ...,
        max_length=2000,
        description="Chatbot's answer based on curriculum context",
        examples=["According to Module 1, Lesson 3, URDF joint limits define..."],
    )

    citations: List[Citation] = Field(
        default_factory=list,
        max_length=5,
        description="Book references for answer sources (max 5)",
    )

    retrieved_chunks: List[RetrievedChunk] = Field(
        default_factory=list,
        max_length=5,
        description="Top-5 chunks retrieved during RAG search",
    )

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response generation timestamp (UTC)",
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "answer": "According to Module 1, Lesson 3, URDF joint limits define the maximum and minimum positions a joint can reach. These limits are specified in the <limit> tag within the joint definition.",
                "citations": [
                    {
                        "module": "1",
                        "lesson": "lesson-3",
                        "section": "Joint Constraints and Workspace",
                        "url": "https://example.com/docs/module1/lesson3#joints",
                    }
                ],
                "retrieved_chunks": [
                    {
                        "chunk_id": "550e8400-e29b-41d4-a716-446655440000",
                        "text_preview": "URDF joints define the kinematic relationships between rigid bodies...",
                        "score": 0.89,
                        "module": "1",
                        "lesson": "lesson-3",
                        "section_title": "Joint Constraints",
                        "url": "https://example.com/docs/module1/lesson3#joints",
                    }
                ],
                "timestamp": "2026-02-09T14:30:45.123Z",
            }
        }


# ============================================================================
# Error Response Models
# ============================================================================

class ErrorResponse(BaseModel):
    """
    Standard error response format.

    Example:
        {
            "detail": "Rate limit: 20 queries/hour. Try again later.",
            "error_code": "RATE_LIMIT_EXCEEDED"
        }
    """

    detail: str = Field(
        ...,
        description="Human-readable error message",
        examples=["Rate limit: 20 queries/hour. Try again later."],
    )

    error_code: Optional[str] = Field(
        None,
        description="Machine-readable error code",
        examples=["RATE_LIMIT_EXCEEDED", "INVALID_INPUT", "SERVICE_UNAVAILABLE"],
    )

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Error timestamp (UTC)",
    )


class RateLimitInfo(BaseModel):
    """
    Rate limit status information.

    Example:
        {
            "query_count": 15,
            "max_queries": 20,
            "queries_remaining": 5,
            "window_end": "2026-02-09T15:30:00Z"
        }
    """

    query_count: int = Field(
        ...,
        ge=0,
        description="Number of queries in current window",
        examples=[15],
    )

    max_queries: int = Field(
        ...,
        ge=1,
        description="Maximum queries allowed per window",
        examples=[20],
    )

    queries_remaining: int = Field(
        ...,
        ge=0,
        description="Queries remaining in current window",
        examples=[5],
    )

    window_end: str = Field(
        ...,
        description="ISO timestamp when current window ends",
        examples=["2026-02-09T15:30:00Z"],
    )
