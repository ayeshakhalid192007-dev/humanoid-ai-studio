"""
Mock Qdrant client for development when qdrant-client cannot be installed.

This provides a simple in-memory mock for testing without the full Qdrant dependency.
Used when grpcio is not available (e.g., Python 3.14 on Windows).

Author: Physical AI Platform Team
Date: 2026-02-09
"""
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MockQdrantClient:
    """Mock Qdrant client that provides basic functionality without grpcio dependency."""

    def __init__(self, url: str = None, api_key: str = None, **kwargs):
        """Initialize mock client."""
        self.url = url
        self.api_key = api_key
        self.collections = {}
        self.mock_data = []
        logger.warning("Using MOCK Qdrant client - vector search will not work!")
        logger.info("To use real Qdrant, install Python 3.10-3.12 and reinstall requirements.txt")

    async def get_collection_info(self) -> Dict[str, Any]:
        """Return mock collection info."""
        return {
            "status": "mock",
            "points_count": len(self.mock_data),
            "vectors_count": len(self.mock_data),
        }

    def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: float = 0.7,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Return mock search results."""
        logger.warning("Mock Qdrant search - returning empty results")
        return []

    def upsert(
        self,
        collection_name: str,
        points: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """Mock upsert operation."""
        self.mock_data.extend(points)
        logger.info(f"Mock upsert: {len(points)} points (total: {len(self.mock_data)})")
        return {"status": "ok", "operation_id": "mock"}

    def create_collection(
        self,
        collection_name: str,
        vectors_config: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Mock collection creation."""
        self.collections[collection_name] = vectors_config
        logger.info(f"Mock collection created: {collection_name}")
        return {"status": "ok"}

    def collection_exists(self, collection_name: str) -> bool:
        """Check if mock collection exists."""
        return collection_name in self.collections

    def close(self):
        """Close mock client."""
        logger.info("Mock Qdrant client closed")
        pass


def get_mock_qdrant_client(url: str, api_key: str) -> MockQdrantClient:
    """Factory function to create mock Qdrant client."""
    return MockQdrantClient(url=url, api_key=api_key)
