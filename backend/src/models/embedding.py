"""
Pydantic models for curriculum embeddings and vector search.

Defines data schemas for:
- EmbeddingChunk: Curriculum text chunk with metadata
- VectorSearchResult: Qdrant search result
- ChunkMetadata: Curriculum chunk metadata

Author: Physical AI Platform Team
Date: 2026-02-09
"""
from pydantic import BaseModel, Field, field_validator, UUID4
from typing import List, Optional
from datetime import datetime


# ============================================================================
# Embedding Models
# ============================================================================

class ChunkMetadata(BaseModel):
    """
    Metadata for curriculum chunk.

    Example:
        {
            "module": "1",
            "lesson": "lesson-3",
            "section_title": "Joint Constraints and Workspace",
            "url": "https://example.com/docs/module1/lesson3#joints",
            "content_version": "1.2.0"
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

    section_title: str = Field(
        ...,
        max_length=200,
        description="Section heading from curriculum",
        examples=["Joint Constraints and Workspace"],
    )

    url: str = Field(
        ...,
        description="Absolute URL to source content in book",
        examples=["https://example.com/docs/module1/lesson3#joints"],
    )

    content_version: str = Field(
        default="1.0.0",
        description="Book version when chunk was created (semantic versioning)",
        examples=["1.2.0"],
    )

    @field_validator("module")
    @classmethod
    def validate_module(cls, v: str) -> str:
        """Validate module number is 1-4."""
        if v not in ["1", "2", "3", "4"]:
            raise ValueError(f"Module must be 1-4, got {v}")
        return v

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format."""
        if not v.startswith("http"):
            raise ValueError(f"URL must start with http, got {v}")
        return v


class EmbeddingChunk(BaseModel):
    """
    Curriculum chunk with text, embedding, and metadata.

    Used for:
    - Storing chunks in Qdrant vector database
    - Batch embedding generation
    - Chunk validation before upload

    Example:
        {
            "chunk_id": "550e8400-e29b-41d4-a716-446655440000",
            "text": "URDF joints define the kinematic relationships...",
            "embedding": [0.023, -0.15, 0.87, ...],
            "metadata": {
                "module": "1",
                "lesson": "lesson-3",
                "section_title": "Joint Constraints",
                "url": "https://example.com/docs/module1/lesson3#joints",
                "content_version": "1.0.0"
            },
            "created_at": "2026-02-09T10:30:00Z"
        }
    """

    chunk_id: UUID4 = Field(
        ...,
        description="Unique identifier for chunk",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )

    text: str = Field(
        ...,
        min_length=50,
        description="Raw curriculum text content (50-10000 chars)",
        examples=["URDF joints define the kinematic relationships between rigid bodies..."],
    )

    embedding: List[float] = Field(
        ...,
        description="OpenAI text-embedding-3-small vector (1536 dimensions)",
    )

    metadata: ChunkMetadata = Field(
        ...,
        description="Curriculum metadata (module, lesson, section, URL, version)",
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Chunk creation timestamp (UTC)",
    )

    @field_validator("text")
    @classmethod
    def validate_text_length(cls, v: str) -> str:
        """
        Validate text length is within range.

        Per data-model.md: 50-1000 words
        We use character count for simplicity (50-10000 chars ~= 10-2000 words)
        """
        word_count = len(v.split())
        if not (50 <= word_count <= 1000):
            raise ValueError(f"Text must be 50-1000 words, got {word_count} words")
        return v

    @field_validator("embedding")
    @classmethod
    def validate_embedding_dimension(cls, v: List[float]) -> List[float]:
        """Validate embedding is 1536 dimensions (OpenAI text-embedding-3-small)."""
        if len(v) != 1536:
            raise ValueError(f"Embedding must be 1536 dimensions, got {len(v)}")
        return v


# ============================================================================
# Vector Search Models
# ============================================================================

class VectorSearchResult(BaseModel):
    """
    Result from Qdrant vector search.

    Contains:
    - Chunk ID and text
    - Cosine similarity score
    - Curriculum metadata
    - Timestamp

    Example:
        {
            "chunk_id": "550e8400-e29b-41d4-a716-446655440000",
            "text": "URDF joints define the kinematic relationships...",
            "score": 0.89,
            "module": "1",
            "lesson": "lesson-3",
            "section_title": "Joint Constraints",
            "url": "https://example.com/docs/module1/lesson3#joints",
            "created_at": "2026-02-09T10:30:00Z",
            "content_version": "1.0.0"
        }
    """

    chunk_id: str = Field(
        ...,
        description="UUID of curriculum chunk",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )

    text: str = Field(
        ...,
        description="Full chunk text content",
        examples=["URDF joints define the kinematic relationships between rigid bodies..."],
    )

    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Cosine similarity score (0.0-1.0, higher is more relevant)",
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
        description="Section heading",
        examples=["Joint Constraints"],
    )

    url: str = Field(
        ...,
        description="Book page URL",
        examples=["https://example.com/docs/module1/lesson3#joints"],
    )

    created_at: str = Field(
        ...,
        description="Chunk creation timestamp (ISO 8601)",
        examples=["2026-02-09T10:30:00Z"],
    )

    content_version: str = Field(
        default="1.0.0",
        description="Book version",
        examples=["1.0.0"],
    )

    def to_preview(self, max_length: int = 200) -> str:
        """
        Get truncated text preview.

        Args:
            max_length: Maximum preview length (default 200)

        Returns:
            str: Truncated text with ellipsis if needed
        """
        if len(self.text) <= max_length:
            return self.text

        return self.text[:max_length].rsplit(" ", 1)[0] + "..."


# ============================================================================
# Batch Processing Models
# ============================================================================

class EmbeddingBatchRequest(BaseModel):
    """
    Request for batch embedding generation.

    Example:
        {
            "texts": [
                "URDF joints define...",
                "Gazebo simulation provides...",
                "Nav2 navigation stack..."
            ],
            "model": "text-embedding-3-small"
        }
    """

    texts: List[str] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="List of texts to embed (max 50 per batch)",
    )

    model: str = Field(
        default="text-embedding-3-small",
        description="OpenAI embedding model",
        examples=["text-embedding-3-small"],
    )

    @field_validator("texts")
    @classmethod
    def validate_batch_size(cls, v: List[str]) -> List[str]:
        """Validate batch size is reasonable (max 50 texts)."""
        if len(v) > 50:
            raise ValueError(f"Max 50 texts per batch, got {len(v)}")
        return v


class EmbeddingBatchResponse(BaseModel):
    """
    Response from batch embedding generation.

    Example:
        {
            "embeddings": [
                [0.023, -0.15, ...],
                [0.045, 0.23, ...],
                [0.012, -0.34, ...]
            ],
            "model": "text-embedding-3-small",
            "tokens_used": 1500
        }
    """

    embeddings: List[List[float]] = Field(
        ...,
        description="List of embedding vectors (1536 dimensions each)",
    )

    model: str = Field(
        ...,
        description="OpenAI embedding model used",
        examples=["text-embedding-3-small"],
    )

    tokens_used: int = Field(
        ...,
        ge=0,
        description="Total tokens processed",
        examples=[1500],
    )


# ============================================================================
# Collection Info Models
# ============================================================================

class CollectionInfo(BaseModel):
    """
    Qdrant collection statistics.

    Example:
        {
            "collection_name": "curriculum",
            "points_count": 523,
            "vector_size": 1536,
            "distance": "COSINE",
            "status": "GREEN"
        }
    """

    collection_name: str = Field(
        ...,
        description="Collection name",
        examples=["curriculum"],
    )

    points_count: int = Field(
        ...,
        ge=0,
        description="Number of chunks stored",
        examples=[523],
    )

    vector_size: int = Field(
        ...,
        description="Embedding dimension",
        examples=[1536],
    )

    distance: str = Field(
        ...,
        description="Distance metric (COSINE, EUCLIDEAN, DOT)",
        examples=["COSINE"],
    )

    status: str = Field(
        ...,
        description="Collection status (GREEN, YELLOW, RED)",
        examples=["GREEN"],
    )
