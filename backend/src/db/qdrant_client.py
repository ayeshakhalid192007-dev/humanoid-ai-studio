"""
Qdrant Cloud client for curriculum vector search.

Provides vector database operations for:
- Curriculum chunk storage
- Semantic search with cosine similarity
- RAG retrieval with score thresholds

Author: Physical AI Platform Team
Date: 2026-02-09
"""
import os
from typing import Optional, List, Dict, Any
from uuid import UUID

try:
    from qdrant_client import QdrantClient as QdrantClientSDK
    from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue, ScoredPoint
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    from src.db.qdrant_mock import MockQdrantClient


class QdrantClient:
    """
    Async Qdrant client for vector search operations.

    Manages connection to Qdrant Cloud and provides:
    - Vector search with cosine similarity
    - Filtering by module/lesson
    - Batch upsert for curriculum embeddings
    """

    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        collection_name: str = "curriculum",
    ):
        """
        Initialize Qdrant client.

        Args:
            url: Qdrant Cloud URL (defaults to QDRANT_URL env var)
            api_key: Qdrant API key (defaults to QDRANT_API_KEY env var)
            collection_name: Collection name (default: curriculum)
        """
        self.url = url or os.getenv("QDRANT_URL")
        self.api_key = api_key or os.getenv("QDRANT_API_KEY")
        self.collection_name = collection_name

        if not self.url or not self.api_key:
            raise ValueError("QDRANT_URL and QDRANT_API_KEY environment variables must be set")

        if QDRANT_AVAILABLE:
            self.client = QdrantClientSDK(url=self.url, api_key=self.api_key)
        else:
            import logging
            logging.warning("qdrant-client not available, using mock client")
            self.client = MockQdrantClient(url=self.url, api_key=self.api_key)

    def close(self) -> None:
        """Close Qdrant client connection."""
        if self.client:
            self.client.close()

    # ========================================================================
    # Vector Search
    # ========================================================================

    async def search(
        self,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: float = 0.7,
        module_filter: Optional[str] = None,
        lesson_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar curriculum chunks using vector similarity.

        Args:
            query_vector: Query embedding vector (1536 dimensions from OpenAI)
            limit: Maximum number of results (default 5)
            score_threshold: Minimum cosine similarity score (default 0.7 per FR-039)
            module_filter: Optional filter by module (e.g., "1", "2", "3", "4")
            lesson_filter: Optional filter by lesson (e.g., "lesson-3")

        Returns:
            List of dicts with:
                - chunk_id (str): UUID of chunk
                - text (str): Chunk text content
                - module (str): Module number
                - lesson (str): Lesson identifier
                - section_title (str): Section heading
                - url (str): Book page URL
                - score (float): Cosine similarity score (0.0-1.0)
                - created_at (str): Chunk creation timestamp
                - content_version (str): Book version

        Example:
            results = await client.search(
                query_vector=[0.023, -0.15, ...],
                limit=5,
                score_threshold=0.7,
                module_filter="1"
            )
        """
        # Build filter conditions
        must_conditions = []

        if module_filter:
            must_conditions.append(
                FieldCondition(key="module", match=MatchValue(value=module_filter))
            )

        if lesson_filter:
            must_conditions.append(
                FieldCondition(key="lesson", match=MatchValue(value=lesson_filter))
            )

        query_filter = Filter(must=must_conditions) if must_conditions else None

        # Perform vector search
        search_results: List[ScoredPoint] = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
            query_filter=query_filter,
        )

        # Convert to dict format
        results = []
        for hit in search_results:
            payload = hit.payload or {}
            results.append(
                {
                    "chunk_id": str(hit.id),
                    "text": payload.get("text", ""),
                    "module": payload.get("module", ""),
                    "lesson": payload.get("lesson", ""),
                    "section_title": payload.get("section_title", ""),
                    "url": payload.get("url", ""),
                    "score": hit.score,
                    "created_at": payload.get("created_at", ""),
                    "content_version": payload.get("content_version", ""),
                }
            )

        return results

    async def search_by_text(
        self,
        query_text: str,
        embedding_function,
        limit: int = 5,
        score_threshold: float = 0.7,
        module_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search using text query (embeds text first, then searches).

        Args:
            query_text: Natural language query
            embedding_function: Async function that takes text and returns embedding vector
            limit: Maximum results
            score_threshold: Minimum similarity
            module_filter: Optional module filter

        Returns:
            List of search results (same format as search())

        Example:
            from backend.src.services.embedder import generate_embedding

            results = await client.search_by_text(
                query_text="What are URDF joint limits?",
                embedding_function=generate_embedding,
                limit=5
            )
        """
        # Generate embedding for query text
        query_vector = await embedding_function(query_text)

        # Perform vector search
        return await self.search(
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
            module_filter=module_filter,
        )

    # ========================================================================
    # Curriculum Chunk Management
    # ========================================================================

    async def upsert_chunk(
        self,
        chunk_id: UUID,
        text: str,
        embedding: List[float],
        module: str,
        lesson: str,
        section_title: str,
        url: str,
        created_at: str,
        content_version: str,
    ) -> None:
        """
        Insert or update single curriculum chunk.

        Args:
            chunk_id: UUID of chunk
            text: Chunk text content (50-1000 words)
            embedding: Vector embedding (1536 dimensions)
            module: Module number ("1", "2", "3", "4")
            lesson: Lesson identifier (e.g., "lesson-3")
            section_title: Section heading (max 200 chars)
            url: Book page URL
            created_at: ISO timestamp
            content_version: Semantic version (e.g., "1.2.0")

        Raises:
            ValueError: If validation fails (text length, module format, etc.)
        """
        # Validate inputs
        word_count = len(text.split())
        if not (50 <= word_count <= 1000):
            raise ValueError(f"Text must be 50-1000 words, got {word_count}")

        if module not in ["1", "2", "3", "4"]:
            raise ValueError(f"Module must be 1-4, got {module}")

        if len(embedding) != 1536:
            raise ValueError(f"Embedding must be 1536 dimensions, got {len(embedding)}")

        # Create point
        point = PointStruct(
            id=str(chunk_id),
            vector=embedding,
            payload={
                "chunk_id": str(chunk_id),
                "text": text,
                "module": module,
                "lesson": lesson,
                "section_title": section_title,
                "url": url,
                "created_at": created_at,
                "content_version": content_version,
            },
        )

        # Upsert to Qdrant
        self.client.upsert(collection_name=self.collection_name, points=[point])

    async def upsert_chunks_batch(self, chunks: List[Dict[str, Any]]) -> int:
        """
        Batch upsert multiple curriculum chunks.

        Args:
            chunks: List of chunk dicts with keys:
                - chunk_id (UUID)
                - text (str)
                - embedding (List[float])
                - module (str)
                - lesson (str)
                - section_title (str)
                - url (str)
                - created_at (str)
                - content_version (str)

        Returns:
            int: Number of chunks upserted

        Example:
            chunks = [
                {
                    "chunk_id": uuid4(),
                    "text": "URDF joints define...",
                    "embedding": [0.023, ...],
                    "module": "1",
                    "lesson": "lesson-3",
                    "section_title": "Joint Constraints",
                    "url": "https://example.com/module1/lesson3#joints",
                    "created_at": "2026-02-09T10:30:00Z",
                    "content_version": "1.0.0"
                }
            ]
            count = await client.upsert_chunks_batch(chunks)
        """
        points = []

        for chunk in chunks:
            point = PointStruct(
                id=str(chunk["chunk_id"]),
                vector=chunk["embedding"],
                payload={
                    "chunk_id": str(chunk["chunk_id"]),
                    "text": chunk["text"],
                    "module": chunk["module"],
                    "lesson": chunk["lesson"],
                    "section_title": chunk["section_title"],
                    "url": chunk["url"],
                    "created_at": chunk["created_at"],
                    "content_version": chunk["content_version"],
                },
            )
            points.append(point)

        # Batch upsert
        self.client.upsert(collection_name=self.collection_name, points=points)

        return len(points)

    async def get_chunk_by_id(self, chunk_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Retrieve chunk by ID.

        Args:
            chunk_id: UUID of chunk

        Returns:
            Dict with chunk data or None if not found
        """
        results = self.client.retrieve(
            collection_name=self.collection_name, ids=[str(chunk_id)]
        )

        if not results:
            return None

        point = results[0]
        payload = point.payload or {}

        return {
            "chunk_id": str(point.id),
            "text": payload.get("text", ""),
            "module": payload.get("module", ""),
            "lesson": payload.get("lesson", ""),
            "section_title": payload.get("section_title", ""),
            "url": payload.get("url", ""),
            "created_at": payload.get("created_at", ""),
            "content_version": payload.get("content_version", ""),
        }

    # ========================================================================
    # Collection Info
    # ========================================================================

    async def get_collection_info(self) -> Dict[str, Any]:
        """
        Get collection statistics.

        Returns:
            Dict with:
                - points_count (int): Number of chunks
                - vector_size (int): Embedding dimension
                - status (str): Collection status
        """
        info = self.client.get_collection(collection_name=self.collection_name)

        return {
            "collection_name": self.collection_name,
            "points_count": info.points_count,
            "vector_size": info.config.params.vectors.size,
            "distance": info.config.params.vectors.distance.name,
            "status": info.status.name,
        }


# Singleton instance for import
_qdrant_client: Optional[QdrantClient] = None


def get_qdrant_client() -> QdrantClient:
    """
    Get or create singleton Qdrant client instance.

    Returns:
        QdrantClient: Initialized client

    Usage:
        client = get_qdrant_client()
        results = await client.search(query_vector, limit=5)
    """
    global _qdrant_client

    if _qdrant_client is None:
        _qdrant_client = QdrantClient()

    return _qdrant_client
