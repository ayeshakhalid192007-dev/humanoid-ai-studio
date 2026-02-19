"""
Retriever Service - Qdrant Vector Search

Retrieves relevant curriculum chunks from Qdrant vector database
using semantic similarity search.

Author: Physical AI Platform Team
Date: 2026-02-09
"""
from typing import List, Dict, Any, Optional

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, Filter, FieldCondition, MatchValue
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

from ..config import get_settings


class Retriever:
    """
    Handles semantic search over curriculum content in Qdrant.

    Features:
    - Top-K retrieval with configurable limit
    - Cosine similarity threshold filtering (>0.7)
    - Metadata filtering (module, lesson)
    """

    def __init__(self):
        self.settings = get_settings()
        if not QDRANT_AVAILABLE:
            raise ImportError(
                "qdrant-client package is required for Retriever. "
                "Install it with: pip install qdrant-client"
            )
        self.client = QdrantClient(
            url=self.settings.QDRANT_URL,
            api_key=self.settings.QDRANT_API_KEY
        )
        self.collection_name = "curriculum"
        self.similarity_threshold = 0.7  # FR-039

    async def search(
        self,
        query_embedding: List[float],
        limit: int = 5,
        module_filter: Optional[str] = None,
        content_type_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant curriculum chunks.

        Args:
            query_embedding: Query vector (1536 dimensions)
            limit: Max number of results to return (default 5)
            module_filter: Optional filter by module (e.g., "1", "2")
            content_type_filter: Optional filter by content type ("prose", "code", "exercise")

        Returns:
            List of dicts with chunk data and similarity scores
        """
        try:
            # Build filter conditions
            filter_conditions = []
            if module_filter:
                filter_conditions.append(
                    FieldCondition(
                        key="module",
                        match=MatchValue(value=module_filter)
                    )
                )
            if content_type_filter:
                filter_conditions.append(
                    FieldCondition(
                        key="content_type",
                        match=MatchValue(value=content_type_filter)
                    )
                )

            search_filter = None
            if filter_conditions:
                search_filter = Filter(must=filter_conditions)

            # Perform vector search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=self.similarity_threshold,
                query_filter=search_filter
            )

            # Format results
            chunks = []
            for result in search_results:
                chunk = {
                    "chunk_id": result.id,
                    "text": result.payload.get("text", ""),
                    "module": result.payload.get("module", ""),
                    "lesson": result.payload.get("lesson", ""),
                    "section_title": result.payload.get("section_title", ""),
                    "url": result.payload.get("url", ""),
                    "content_type": result.payload.get("content_type", "prose"),
                    "code_language": result.payload.get("code_language"),
                    "file_type": result.payload.get("file_type", "lesson"),
                    "score": result.score
                }
                chunks.append(chunk)

            return chunks

        except Exception as e:
            raise RuntimeError(f"Vector search failed: {str(e)}")

    async def health_check(self) -> bool:
        """
        Check if Qdrant is accessible and collection exists.

        Returns:
            True if healthy, False otherwise
        """
        try:
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]
            return self.collection_name in collection_names
        except Exception:
            return False
