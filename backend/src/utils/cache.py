"""Distributed caching system using Redis for Physical AI platform.

Provides:
- Distributed caching with Redis
- Cache warming strategies for frequently accessed content
- Proper cache invalidation
- TTL management
- Fallback mechanisms
"""

import asyncio
import json
import hashlib
from typing import Optional, Any, Union, List, Dict
from datetime import timedelta
from functools import wraps
import logging

import redis.asyncio as redis
from ..config import get_settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CacheManager:
    """Redis-based cache manager with fallback capabilities."""

    def __init__(self):
        self.settings = get_settings()
        self.redis_client: Optional[redis.Redis] = None
        self._initialized = False

    async def initialize(self):
        """Initialize Redis connection."""
        if self._initialized:
            return

        try:
            redis_url = self.settings.REDIS_URL if hasattr(self.settings, 'REDIS_URL') else None

            if redis_url:
                self.redis_client = redis.from_url(
                    redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    max_connections=20,
                    retry_on_timeout=True
                )
            else:
                # Fall back to localhost with standard settings
                self.redis_client = redis.Redis(
                    host="localhost",
                    port=6379,
                    db=0,
                    encoding="utf-8",
                    decode_responses=True,
                    max_connections=20,
                    retry_on_timeout=True
                )

            # Test connection
            await self.redis_client.ping()
            logger.info("Redis cache connected successfully")
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to connect to Redis, falling back to in-memory cache: {e}")
            self.redis_client = None
            self._initialized = True

    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()

    def _get_cache_key(self, namespace: str, key: str) -> str:
        """Generate cache key with namespace."""
        return f"{namespace}:{key}"

    def _make_hash(self, obj: Any) -> str:
        """Create a hash of the provided object for use in cache keys."""
        obj_str = json.dumps(obj, sort_keys=True, default=str)
        return hashlib.md5(obj_str.encode()).hexdigest()

    async def get(self, namespace: str, key: str, json_decode: bool = True) -> Optional[Any]:
        """Get value from cache."""
        if not self._initialized:
            await self.initialize()

        cache_key = self._get_cache_key(namespace, key)

        try:
            if self.redis_client:
                value = await self.redis_client.get(cache_key)
                if value is not None:
                    if json_decode:
                        return json.loads(value)
                    return value
            return None
        except Exception as e:
            logger.error(f"Cache GET error for {cache_key}: {e}")
            return None

    async def set(self, namespace: str, key: str, value: Any, ttl: Union[int, timedelta] = None, json_encode: bool = True) -> bool:
        """Set value in cache."""
        if not self._initialized:
            await self.initialize()

        cache_key = self._get_cache_key(namespace, key)

        try:
            if self.redis_client:
                if json_encode:
                    value = json.dumps(value, default=str)

                if ttl:
                    if isinstance(ttl, timedelta):
                        ttl = int(ttl.total_seconds())
                    result = await self.redis_client.setex(cache_key, ttl, value)
                else:
                    result = await self.redis_client.set(cache_key, value)

                return bool(result)
            return False
        except Exception as e:
            logger.error(f"Cache SET error for {cache_key}: {e}")
            return False

    async def delete(self, namespace: str, key: str) -> bool:
        """Delete key from cache."""
        if not self._initialized:
            await self.initialize()

        cache_key = self._get_cache_key(namespace, key)

        try:
            if self.redis_client:
                result = await self.redis_client.delete(cache_key)
                return bool(result)
            return False
        except Exception as e:
            logger.error(f"Cache DELETE error for {cache_key}: {e}")
            return False

    async def clear_namespace(self, namespace: str) -> int:
        """Clear all keys in a namespace."""
        if not self._initialized:
            await self.initialize()

        try:
            if self.redis_client:
                # Use SCAN to avoid blocking with large datasets
                cursor = 0
                count = 0
                while True:
                    cursor, keys = await self.redis_client.scan(
                        cursor=cursor,
                        match=f"{namespace}:*",
                        count=100
                    )
                    if keys:
                        await self.redis_client.delete(*keys)
                        count += len(keys)
                    if cursor == 0:
                        break
                logger.info(f"Cache cleared {count} keys in namespace {namespace}")
                return count
            return 0
        except Exception as e:
            logger.error(f"Cache clear namespace error for {namespace}: {e}")
            return 0

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache keys matching a pattern."""
        if not self._initialized:
            await self.initialize()

        try:
            if self.redis_client:
                # Use SCAN to avoid blocking with large datasets
                cursor = 0
                count = 0
                while True:
                    cursor, keys = await self.redis_client.scan(
                        cursor=cursor,
                        match=pattern,
                        count=100
                    )
                    if keys:
                        await self.redis_client.delete(*keys)
                        count += len(keys)
                    if cursor == 0:
                        break
                logger.info(f"Cache invalidated {count} keys matching pattern {pattern}")
                return count
            return 0
        except Exception as e:
            logger.error(f"Cache invalidate pattern error for {pattern}: {e}")
            return 0

    async def get_with_fallback(self, namespace: str, key: str, fallback_func, ttl: Union[int, timedelta] = 3600):
        """Get value from cache with automatic fallback and cache population."""
        # Try to get from cache first
        cached_value = await self.get(namespace, key)
        if cached_value is not None:
            logger.debug(f"Cache HIT for {namespace}:{key}")
            return cached_value

        logger.debug(f"Cache MISS for {namespace}:{key}, populating from fallback")

        # Run fallback function to get value
        try:
            value = await fallback_func() if asyncio.iscoroutinefunction(fallback_func) else fallback_func()

            # Cache the value
            await self.set(namespace, key, value, ttl)

            return value
        except Exception as e:
            logger.error(f"Cache fallback error for {namespace}:{key}: {e}")
            return None


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


async def get_cache_manager() -> CacheManager:
    """Get or initialize the global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
        await _cache_manager.initialize()
    return _cache_manager


# Decorator for cache
def cached(
    namespace: str,
    ttl: Union[int, timedelta] = 3600,
    key_func: callable = None,
    include_args: bool = True,
    include_kwargs: bool = True
):
    """
    Decorator to cache function results.

    Args:
        namespace: Cache namespace
        ttl: Time-to-live in seconds
        key_func: Function to generate cache key (overrides defaults)
        include_args: Include function arguments in cache key
        include_kwargs: Include keyword arguments in cache key
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                func_name = func.__name__
                key_parts = [func_name]

                if include_args and args:
                    # Include args (skip first arg if it's self/cls for methods)
                    args_to_include = args[1:] if args and hasattr(args[0], func_name) else args
                    if args_to_include:
                        key_parts.append(str(args_to_include))

                if include_kwargs and kwargs:
                    # Sort kwargs for consistent key generation
                    sorted_kwargs = tuple(sorted(kwargs.items()))
                    key_parts.append(str(sorted_kwargs))

                cache_key = "|".join(key_parts)

            # Get or create cache manager
            cache_manager = await get_cache_manager()

            # Try to get from cache
            result = await cache_manager.get_with_fallback(
                namespace,
                cache_key,
                lambda: func(*args, **kwargs),
                ttl=ttl
            )

            return result
        return wrapper
    return decorator


# Specific cache operations for different use cases
class CurriculumCache:
    """Cache operations specific to curriculum content."""

    def __init__(self):
        self.cache = None

    async def get_cache(self):
        if self.cache is None:
            self.cache = await get_cache_manager()
        return self.cache

    async def get_chapter_content(self, chapter_slug: str) -> Optional[Dict[str, Any]]:
        """Get cached chapter content."""
        cache = await self.get_cache()
        return await cache.get("curriculum", f"chapter:{chapter_slug}")

    async def cache_chapter_content(self, chapter_slug: str, content: Dict[str, Any], ttl: int = 3600):
        """Cache chapter content."""
        cache = await self.get_cache()
        await cache.set("curriculum", f"chapter:{chapter_slug}", content, ttl)

    async def invalidate_chapter(self, chapter_slug: str):
        """Invalidate specific chapter cache."""
        cache = await self.get_cache()
        await cache.delete("curriculum", f"chapter:{chapter_slug}")

    async def invalidate_module(self, module: str):
        """Invalidate all chapters in a module."""
        cache = await self.get_cache()
        await cache.invalidate_pattern(f"curriculum:chapter:{module}_*")


class PersonalizationCache:
    """Cache operations specific to personalized content."""

    def __init__(self):
        self.cache = None

    async def get_cache(self):
        if self.cache is None:
            self.cache = await get_cache_manager()
        return self.cache

    async def get_personalized_content(self, user_id: str, chapter_slug: str) -> Optional[str]:
        """Get cached personalized content."""
        cache = await self.get_cache()
        return await cache.get("personalization", f"{user_id}:{chapter_slug}")

    async def cache_personalized_content(self, user_id: str, chapter_slug: str, content: str, ttl: int = 7200):
        """Cache personalized content."""
        cache = await self.get_cache()
        await cache.set("personalization", f"{user_id}:{chapter_slug}", content, ttl)

    async def invalidate_user_personalization(self, user_id: str):
        """Invalidate all personalized content for a user."""
        cache = await self.get_cache()
        await cache.invalidate_pattern(f"personalization:{user_id}:*")


class TranslationCache:
    """Cache operations specific to translated content."""

    def __init__(self):
        self.cache = None

    async def get_cache(self):
        if self.cache is None:
            self.cache = await get_cache_manager()
        return self.cache

    async def get_translation(self, chapter_slug: str, target_language: str) -> Optional[str]:
        """Get cached translation."""
        cache = await self.get_cache()
        return await cache.get("translation", f"{chapter_slug}:{target_language}")

    async def cache_translation(self, chapter_slug: str, target_language: str, content: str, ttl: int = 7200):
        """Cache translation."""
        cache = await self.get_cache()
        await cache.set("translation", f"{chapter_slug}:{target_language}", content, ttl)

    async def invalidate_translation(self, chapter_slug: str, target_language: str = None):
        """Invalidate translation cache."""
        cache = await self.get_cache()
        if target_language:
            await cache.delete("translation", f"{chapter_slug}:{target_language}")
        else:
            await cache.invalidate_pattern(f"translation:{chapter_slug}:*")


class EmbeddingCache:
    """Cache operations specific to embeddings."""

    def __init__(self):
        self.cache = None

    async def get_cache(self):
        if self.cache is None:
            self.cache = await get_cache_manager()
        return self.cache

    async def get_embedding(self, content_hash: str) -> Optional[List[float]]:
        """Get cached embedding."""
        cache = await self.get_cache()
        data = await cache.get("embedding", content_hash, json_decode=False)
        if data:
            return json.loads(data)  # Parse embedded data manually
        return None

    async def cache_embedding(self, content_hash: str, embedding: List[float], ttl: int = 86400):  # 24 hours
        """Cache embedding vector."""
        cache = await self.get_cache()
        await cache.set("embedding", content_hash, embedding, ttl, json_encode=False)

    async def get_chunk_embeddings(self, chunk_ids: List[str]) -> Dict[str, List[float]]:
        """Get multiple chunk embeddings efficiently."""
        cache = await self.get_cache()
        embeddings = {}
        for chunk_id in chunk_ids:
            emb = await self.get_embedding(chunk_id)
            if emb is not None:
                embeddings[chunk_id] = emb
        return embeddings


# Cache warming strategies
class CacheWarmingService:
    """Service to warm frequently accessed content into cache."""

    def __init__(self):
        self.chapters_cache = CurriculumCache()
        self.personalization_cache = PersonalizationCache()
        self.translation_cache = TranslationCache()
        self.logger = get_logger(__name__)

    async def warm_curriculum_cache(self, chapter_slugs: List[str]):
        """Warm curriculum chapter cache."""
        from ..services.chapter_retriever import ChapterRetriever
        retriever = ChapterRetriever()

        for slug in chapter_slugs:
            try:
                content = await retriever.get_chapter_content(slug)
                if content:
                    await self.chapters_cache.cache_chapter_content(slug, content)
                    self.logger.info(f"Warmed chapter cache: {slug}")
            except Exception as e:
                self.logger.error(f"Failed to warm chapter cache for {slug}: {e}")

    async def warm_popular_content(self):
        """Warm popular content based on usage analytics."""
        # This would normally integrate with analytics data
        popular_chapters = [
            "module1_introduction",
            "module2_ros_basics",
            "module3_simulation_fundamentals",
            "module4_perception_pipeline"
        ]
        await self.warm_curriculum_cache(popular_chapters)

    async def warm_user_content(self, user_id: str, chapter_slugs: List[str]):
        """Warm personalized content for a specific user."""
        from ..ai.agents.personalization import PersonalizationAgent
        from ..ai.prompts.registry import PromptRegistry
        from ..db.neon_client import get_neon_client

        # This would typically happen with an authenticated user context
        # In practice, this could be initiated on login or when needed
        pass