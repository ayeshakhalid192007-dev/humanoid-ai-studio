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
from ..db.qdrant_wrapper import get_qdrant_wrapper
from ..utils.logger import get_logger


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
        self.logger = get_logger(__name__)
        self.qdrant_wrapper = None  # Initialize lazily

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
        # Initialize wrapper if needed
        if self.qdrant_wrapper is None:
            self.qdrant_wrapper = await get_qdrant_wrapper()

        try:
            # Use the enhanced wrapper that includes circuit breaker and caching
            search_results = await self.qdrant_wrapper.search_with_circuit_breaker(
                query_vector=query_embedding,
                limit=limit,
                score_threshold=self.similarity_threshold,
                module_filter=module_filter,
                lesson_filter=content_type_filter  # Using content_type_filter as lesson_filter in this context
            )

            return search_results

        except Exception as e:
            self.logger.error(f"Vector search failed: {str(e)}", exc_info=True)
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
