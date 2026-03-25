"""Qdrant client wrapper with enhanced error handling, circuit breakers, and caching."""

import asyncio
import time
import random
from typing import List, Dict, Any, Optional
from uuid import UUID

try:
    from qdrant_client import QdrantClient as QdrantClientSDK
    from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue, ScoredPoint
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    QdrantClientSDK = None
    ScoredPoint = None

from .qdrant_client import QdrantClient
from ..utils.circuit_breaker import CircuitBreaker
from ..utils.cache import EmbeddingCache
from ..utils.logger import get_logger


class QdrantClientWrapper:
    """
    Enhanced Qdrant client wrapper with:
    - Circuit breaker pattern for resilience
    - Caching for frequently accessed data
    - Retry mechanisms with exponential backoff
    - Enhanced error handling
    """

    def __init__(self, qdrant_client: QdrantClient):
        self.qdrant_client = qdrant_client
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=30
        )
        self.cache = EmbeddingCache()
        self.logger = get_logger(__name__)

        # For similarity search cache
        self.search_cache_ttl = 300  # 5 minutes for search results
        self.search_cache_size = 1000  # max cache entries

    async def search_with_circuit_breaker(
        self,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: float = 0.7,
        module_filter: Optional[str] = None,
        lesson_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Perform vector search with circuit breaker protection and caching.
        """
        # Create cache key based on query parameters
        cache_key = self._create_search_cache_key(
            query_vector, limit, score_threshold, module_filter, lesson_filter
        )

        # Try to get from cache first
        cached_results = await self.cache.get("search", cache_key)
        if cached_results:
            self.logger.debug(f"Search cache hit for key: {cache_key[:16]}...")
            return cached_results

        async def _search_operation():
            start_time = time.time()
            try:
                results = await self.qdrant_client.search(
                    query_vector=query_vector,
                    limit=limit,
                    score_threshold=score_threshold,
                    module_filter=module_filter,
                    lesson_filter=lesson_filter
                )

                latency = (time.time() - start_time) * 1000
                self.logger.info(f"Qdrant search completed in {latency:.2f}ms")

                # Cache the successful results
                await self.cache.set("search", cache_key, results, ttl=self.search_cache_ttl)

                return results
            except Exception as e:
                latency = (time.time() - start_time) * 1000
                self.logger.error(f"Qdrant search failed in {latency:.2f}ms: {str(e)}")
                raise

        # Execute with circuit breaker
        return await self.circuit_breaker.execute(_search_operation)

    def _create_search_cache_key(
        self,
        query_vector: List[float],
        limit: int,
        score_threshold: float,
        module_filter: Optional[str],
        lesson_filter: Optional[str]
    ) -> str:
        """Create a cache key for search results."""
        import hashlib
        # Create a hash of the query vector and parameters
        query_str = f"{str(query_vector[:5])}_{limit}_{score_threshold}_{module_filter}_{lesson_filter}"
        return hashlib.md5(query_str.encode()).hexdigest()

    async def upsert_chunk_with_retry(
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
        max_retries: int = 3
    ) -> None:
        """
        Upsert a chunk with retry mechanism on failure.
        """
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                await self.qdrant_client.upsert_chunk(
                    chunk_id=chunk_id,
                    text=text,
                    embedding=embedding,
                    module=module,
                    lesson=lesson,
                    section_title=section_title,
                    url=url,
                    created_at=created_at,
                    content_version=content_version
                )
                # Success - clear any cached search results that might be affected
                await self._invalidate_search_cache(module, lesson)
                return
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    # Exponential backoff with jitter
                    delay = (2 ** attempt) + random.uniform(0, 1)
                    self.logger.warning(f"Qdrant upsert attempt {attempt + 1} failed: {str(e)}, retrying in {delay:.2f}s")
                    await asyncio.sleep(delay)
                else:
                    self.logger.error(f"Qdrant upsert failed after {max_retries} retries: {str(e)}")
                    raise last_exception

    async def upsert_chunks_batch_with_retry(
        self,
        chunks: List[Dict[str, Any]],
        max_retries: int = 3
    ) -> int:
        """
        Batch upsert chunks with retry mechanism.
        """
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                result = await self.qdrant_client.upsert_chunks_batch(chunks)

                # Clear related caches
                modules = set(chunk['module'] for chunk in chunks if 'module' in chunk)
                lessons = set(chunk['lesson'] for chunk in chunks if 'lesson' in chunk)

                for module in modules:
                    for lesson in lessons:
                        await self._invalidate_search_cache(module, lesson)

                return result
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    delay = (2 ** attempt) + random.uniform(0, 1)
                    self.logger.warning(f"Qdrant batch upsert attempt {attempt + 1} failed: {str(e)}, retrying in {delay:.2f}s")
                    await asyncio.sleep(delay)
                else:
                    self.logger.error(f"Qdrant batch upsert failed after {max_retries} retries: {str(e)}")
                    raise last_exception

    async def get_chunk_by_id_safe(
        self,
        chunk_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Get chunk by ID with circuit breaker and error handling.
        """
        async def _get_operation():
            try:
                return await self.qdrant_client.get_chunk_by_id(chunk_id)
            except Exception as e:
                self.logger.error(f"Failed to get chunk {chunk_id}: {str(e)}")
                raise

        try:
            return await self.circuit_breaker.execute(_get_operation)
        except Exception:
            # Circuit breaker may be open or operation failed
            self.logger.warning(f"Qdrant get_chunk_by_id failed after circuit breaker protection for chunk {chunk_id}")
            return None

    async def _invalidate_search_cache(self, module: str, lesson: str):
        """Invalidate search cache entries related to a module/lesson."""
        # In a real implementation, we'd have a more sophisticated invalidation strategy
        # For now, we'll just log that invalidation happened
        self.logger.info(f"Invalidating cache for module {module}, lesson {lesson}")

    async def health_check_with_circuit_breaker(self) -> bool:
        """
        Health check that respects circuit breaker state.
        """
        if self.circuit_breaker.is_open():
            return False

        async def _health_operation():
            return await self.qdrant_client.health_check()

        try:
            return await self.circuit_breaker.execute(_health_operation)
        except Exception:
            return False

    def get_circuit_breaker_state(self):
        """
        Get the current state of the circuit breaker.
        """
        return {
            "state": self.circuit_breaker.state,
            "failure_count": self.circuit_breaker.failure_count,
            "is_open": self.circuit_breaker.is_open(),
            "last_failure_time": self.circuit_breaker.last_failure_time
        }


# Global wrapper instance
_qdrant_wrapper: Optional[QdrantClientWrapper] = None


async def get_qdrant_wrapper() -> QdrantClientWrapper:
    """
    Get or create singleton Qdrant client wrapper instance.

    Returns:
        QdrantClientWrapper: Initialized wrapper with circuit breaker and caching
    """
    global _qdrant_wrapper

    if _qdrant_wrapper is None:
        qdrant_client = QdrantClient()
        _qdrant_wrapper = QdrantClientWrapper(qdrant_client)

    return _qdrant_wrapper