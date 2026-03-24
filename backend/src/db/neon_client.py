"""
Neon Postgres client with asyncpg connection pool.

Provides database operations for:
- Chat session management
- Conversation turn logging
- Rate limiting (sliding window)

Author: Physical AI Platform Team
Date: 2026-02-09
"""
import asyncpg
import os
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime, timedelta
from ..utils.cache import PersonalizationCache, TranslationCache, get_cache_manager
from ..utils.logger import get_logger


class NeonClient:
    """
    Async Postgres client for Neon database operations.

    Manages connection pool and provides query helpers for:
    - Session tracking (chat_sessions table)
    - Conversation logging (conversation_turns table)
    - Rate limiting (rate_limit_records table)
    """

    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize Neon client.

        Args:
            database_url: PostgreSQL connection string (defaults to NEON_DATABASE_URL env var)
        """
        self.database_url = database_url or os.getenv("NEON_DATABASE_URL")
        if not self.database_url:
            raise ValueError("NEON_DATABASE_URL environment variable not set")

        self.pool: Optional[asyncpg.Pool] = None

        # Add caching support
        self.personalization_cache = PersonalizationCache()
        self.translation_cache = TranslationCache()
        self.logger = get_logger(__name__)

    async def connect(self, min_size: int = 5, max_size: int = 20) -> None:
        """
        Create connection pool.

        Args:
            min_size: Minimum pool connections
            max_size: Maximum pool connections

        Raises:
            asyncpg.PostgresError: If connection fails
        """
        self.pool = await asyncpg.create_pool(
            self.database_url,
            min_size=min_size,
            max_size=max_size,
            command_timeout=10.0,  # 10 second timeout for queries
        )

    async def close(self) -> None:
        """Close connection pool."""
        if self.pool:
            await self.pool.close()

    # ========================================================================
    # Session Management
    # ========================================================================

    async def create_or_update_session(
        self, session_id: UUID, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create new session or update last_active_at for existing session.

        Args:
            session_id: UUID of browser session
            metadata: Optional JSONB metadata (user-agent, browser info, etc.)

        Returns:
            Dict with session_id, created_at, last_active_at, metadata

        Raises:
            asyncpg.PostgresError: If database operation fails
        """
        metadata = metadata or {}

        async with self.pool.acquire() as conn:
            result = await conn.fetchrow(
                """
                INSERT INTO chat_sessions (session_id, metadata)
                VALUES ($1, $2)
                ON CONFLICT (session_id)
                DO UPDATE SET last_active_at = NOW()
                RETURNING session_id, created_at, last_active_at, metadata
                """,
                session_id,
                metadata,
            )

            return dict(result)

    async def get_session(self, session_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get session by ID.

        Args:
            session_id: UUID of session

        Returns:
            Dict with session data or None if not found
        """
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow(
                """
                SELECT session_id, created_at, last_active_at, metadata
                FROM chat_sessions
                WHERE session_id = $1
                """,
                session_id,
            )

            return dict(result) if result else None

    # ========================================================================
    # Conversation Turn Logging
    # ========================================================================

    async def insert_conversation_turn(
        self,
        session_id: UUID,
        query: str,
        response: str,
        retrieved_chunks: List[Dict[str, Any]],
        page_context: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Log conversation turn to database.

        Args:
            session_id: UUID of session
            query: Student's question (1-500 chars)
            response: Chatbot's answer
            retrieved_chunks: List of chunks with {chunk_id, text_preview, score, module, lesson, section_title, url}
            page_context: Current book page URL (optional)
            metadata: Additional context (user-agent, selection_text, etc.)

        Returns:
            int: turn_id of inserted record

        Raises:
            asyncpg.CheckViolationError: If query length violates CHECK constraint
            asyncpg.ForeignKeyViolationError: If session_id doesn't exist
        """
        metadata = metadata or {}

        # Validate query length (1-500 chars)
        if not (1 <= len(query) <= 500):
            raise ValueError(f"Query length must be 1-500 chars, got {len(query)}")

        # Validate retrieved_chunks array (max 5 elements)
        if len(retrieved_chunks) > 5:
            raise ValueError(f"Max 5 retrieved chunks allowed, got {len(retrieved_chunks)}")

        async with self.pool.acquire() as conn:
            turn_id = await conn.fetchval(
                """
                INSERT INTO conversation_turns
                    (session_id, query, response, retrieved_chunks, page_context, metadata)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING turn_id
                """,
                session_id,
                query,
                response,
                retrieved_chunks,
                page_context,
                metadata,
            )

            return turn_id

    async def get_conversation_history(
        self, session_id: UUID, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history for session.

        Args:
            session_id: UUID of session
            limit: Max number of turns to retrieve (default 50)

        Returns:
            List of conversation turns (newest first)
        """
        async with self.pool.acquire() as conn:
            results = await conn.fetch(
                """
                SELECT turn_id, session_id, query, response, retrieved_chunks,
                       timestamp, page_context, metadata
                FROM conversation_turns
                WHERE session_id = $1
                ORDER BY timestamp DESC
                LIMIT $2
                """,
                session_id,
                limit,
            )

            return [dict(row) for row in results]

    async def get_conversation_turns(
        self, session_id: UUID, limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get conversation turns for session with pagination.

        Args:
            session_id: UUID of session
            limit: Max number of turns to retrieve (default 50)
            offset: Offset for pagination

        Returns:
            List of conversation turns (oldest first for display)
        """
        async with self.pool.acquire() as conn:
            results = await conn.fetch(
                """
                SELECT turn_id, session_id, query, response, retrieved_chunks,
                       timestamp as created_at, page_context, metadata
                FROM conversation_turns
                WHERE session_id = $1
                ORDER BY timestamp ASC
                LIMIT $2 OFFSET $3
                """,
                session_id,
                limit,
                offset,
            )

            return [dict(row) for row in results]

    # ========================================================================
    # Rate Limiting (Sliding Window)
    # ========================================================================

    async def check_rate_limit(
        self, session_id: UUID, max_queries: int = 20, window_hours: int = 1
    ) -> bool:
        """
        Check if session has exceeded rate limit.

        Args:
            session_id: UUID of session
            max_queries: Maximum queries allowed in window (default 20)
            window_hours: Time window in hours (default 1)

        Returns:
            bool: True if within limit, False if exceeded

        Note:
            Uses sliding window: counts queries in last N hours
        """
        async with self.pool.acquire() as conn:
            query_count = await conn.fetchval(
                """
                SELECT COUNT(*) as query_count
                FROM rate_limit_records
                WHERE session_id = $1
                AND query_timestamp > NOW() - INTERVAL '1 hour' * $2
                """,
                session_id,
                window_hours,
            )

            return query_count < max_queries

    async def record_query(self, session_id: UUID) -> None:
        """
        Record query timestamp for rate limiting.

        Args:
            session_id: UUID of session

        Raises:
            asyncpg.ForeignKeyViolationError: If session_id doesn't exist
        """
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO rate_limit_records (session_id)
                VALUES ($1)
                """,
                session_id,
            )

    async def get_rate_limit_info(
        self, session_id: UUID, window_hours: int = 1
    ) -> Dict[str, Any]:
        """
        Get rate limit status for session.

        Args:
            session_id: UUID of session
            window_hours: Time window in hours (default 1)

        Returns:
            Dict with query_count, max_queries, window_end, queries_remaining
        """
        async with self.pool.acquire() as conn:
            query_count = await conn.fetchval(
                """
                SELECT COUNT(*) as query_count
                FROM rate_limit_records
                WHERE session_id = $1
                AND query_timestamp > NOW() - INTERVAL '1 hour' * $2
                """,
                session_id,
                window_hours,
            )

            max_queries = 20  # FR-048
            queries_remaining = max(0, max_queries - query_count)
            window_end = datetime.utcnow() + timedelta(hours=window_hours)

            return {
                "query_count": query_count,
                "max_queries": max_queries,
                "queries_remaining": queries_remaining,
                "window_end": window_end.isoformat(),
            }

    # ========================================================================
    # Personalized Content Cache (Legacy - Kept for backward compatibility)
    # ========================================================================

    async def get_personalized_content_legacy(
        self, user_id: str, chapter_slug: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached personalized content for a user and chapter (legacy method)."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, user_id, chapter_slug, personalized_markdown,
                       user_profile_snapshot, content_version, prompt_version, created_at
                FROM personalized_content
                WHERE user_id = $1 AND chapter_slug = $2
                """,
                user_id,
                chapter_slug,
            )
            return dict(row) if row else None

    async def upsert_personalized_content_legacy(
        self,
        user_id: str,
        chapter_slug: str,
        personalized_markdown: str,
        user_profile_snapshot: dict,
        content_version: str,
    ) -> int:
        """Insert or update personalized content cache (legacy method)."""
        import json
        async with self.pool.acquire() as conn:
            row_id = await conn.fetchval(
                """
                INSERT INTO personalized_content
                    (user_id, chapter_slug, personalized_markdown, user_profile_snapshot, content_version, prompt_version, created_at)
                VALUES ($1, $2, $3, $4::jsonb, $5, '', NOW())
                ON CONFLICT (user_id, chapter_slug) DO UPDATE SET
                    personalized_markdown = $3,
                    user_profile_snapshot = $4::jsonb,
                    content_version = $5,
                    prompt_version = '',
                    created_at = NOW()
                RETURNING id
                """,
                user_id,
                chapter_slug,
                personalized_markdown,
                json.dumps(user_profile_snapshot),
                content_version,
            )
            return row_id

    # ========================================================================
    # Urdu Translation Cache (Legacy - Kept for backward compatibility)
    # ========================================================================

    async def get_urdu_translation_legacy(
        self, chapter_slug: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached Urdu translation for a chapter (legacy method)."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, chapter_slug, urdu_markdown, content_version, prompt_version, created_at
                FROM urdu_translations
                WHERE chapter_slug = $1
                """,
                chapter_slug,
            )
            return dict(row) if row else None

    async def upsert_urdu_translation_legacy(
        self,
        chapter_slug: str,
        urdu_markdown: str,
        content_version: str,
    ) -> int:
        """Insert or update Urdu translation cache (legacy method)."""
        async with self.pool.acquire() as conn:
            row_id = await conn.fetchval(
                """
                INSERT INTO urdu_translations
                    (chapter_slug, urdu_markdown, content_version, prompt_version, created_at)
                VALUES ($1, $2, $3, '', NOW())
                ON CONFLICT (chapter_slug) DO UPDATE SET
                    urdu_markdown = $2,
                    content_version = $3,
                    prompt_version = '',
                    created_at = NOW()
                RETURNING id
                """,
                chapter_slug,
                urdu_markdown,
                content_version,
            )
            return row_id

    # ========================================================================
    # AI Generation Rate Limiting
    # ========================================================================

    async def check_ai_rate_limit(
        self, identifier: str, request_type: str, max_requests: int, window_hours: int = 1
    ) -> bool:
        """
        Check if identifier has exceeded AI generation rate limit.

        Returns:
            bool: True if within limit, False if exceeded
        """
        async with self.pool.acquire() as conn:
            count = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM ai_generation_rate_limits
                WHERE identifier = $1
                AND request_type = $2
                AND request_timestamp > NOW() - INTERVAL '1 hour' * $3
                """,
                identifier,
                request_type,
                window_hours,
            )
            return count < max_requests

    async def record_ai_request(
        self, identifier: str, request_type: str
    ) -> None:
        """Record an AI generation request for rate limiting."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO ai_generation_rate_limits (identifier, request_type)
                VALUES ($1, $2)
                """,
                identifier,
                request_type,
            )

    # ========================================================================
    # Agent Execution Logging
    # ========================================================================

    async def insert_agent_execution_log(
        self,
        agent_type: str,
        grounding_policy: str,
        skills_used: List[str],
        skills_detail: List[Dict[str, Any]],
        token_count: Optional[int],
        model: str,
        latency_ms: int,
        cached: bool,
        request_metadata: Dict[str, Any],
    ) -> int:
        """
        Insert execution log for an agent request.

        Args:
            agent_type: Type of agent that executed
            grounding_policy: The grounding policy applied
            skills_used: List of skills applied
            skills_detail: Detailed data about each skill execution
            token_count: Number of tokens used (if applicable)
            model: The AI model used
            latency_ms: Execution latency in milliseconds
            cached: Whether result was from cache
            request_metadata: Additional request metadata

        Returns:
            int: log ID of inserted record
        """
        async with self.pool.acquire() as conn:
            log_id = await conn.fetchval(
                """
                INSERT INTO agent_execution_logs
                    (agent_type, grounding_policy, skills_used, skills_detail, token_count,
                     model, latency_ms, cached, request_metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING id
                """,
                agent_type,
                grounding_policy,
                skills_used,
                skills_detail,
                token_count,
                model,
                latency_ms,
                cached,
                request_metadata,
            )
            return log_id

    async def cleanup_agent_execution_logs(self, retention_days: int = 90) -> int:
        """
        Delete agent execution logs older than specified days.

        Args:
            retention_days: Number of days to retain logs (default: 90)

        Returns:
            int: Number of records deleted
        """
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                """
                DELETE FROM agent_execution_logs
                WHERE created_at < NOW() - INTERVAL '1 day' * $1
                """,
                retention_days,
            )

            deleted_count = int(result.split()[-1]) if result else 0
            return deleted_count

    # ========================================================================
    # Personalized Content Cache (Current Version with Prompt Version)
    # ========================================================================

    async def get_personalized_content(
        self, user_id: str, chapter_slug: str,
        content_version: str = None, prompt_version: str = None
    ) -> Optional[Dict[str, Any]]:
        """Get cached personalized content for a user and chapter.

        If content_version and prompt_version are provided, validate against both.
        Otherwise, just get the latest cached content.
        """
        # Try to get from cache first when we're just fetching the latest content
        if content_version is None and prompt_version is None:
            cached_content = await self.personalization_cache.get_personalized_content(user_id, chapter_slug)
            if cached_content:
                self.logger.debug(f"Cache hit for personalized content: {user_id}:{chapter_slug}")
                # If it's cached, we don't need to validate version in DB
                # In a real implementation we'd need to store versioning info with the cache
                return {
                    "personalized_markdown": cached_content,
                    "user_profile_snapshot": {},  # We'd need to cache this separately
                    "content_version": "cached_version",  # Placeholder
                    "prompt_version": "cached_prompt_version"  # Placeholder
                }

        async with self.pool.acquire() as conn:
            if content_version is not None and prompt_version is not None:
                # Validate against both content and prompt versions
                row = await conn.fetchrow(
                    """
                    SELECT id, user_id, chapter_slug, personalized_markdown,
                           user_profile_snapshot, content_version, prompt_version, created_at
                    FROM personalized_content
                    WHERE user_id = $1 AND chapter_slug = $2
                      AND content_version = $3 AND prompt_version = $4
                    """,
                    user_id,
                    chapter_slug,
                    content_version,
                    prompt_version,
                )
            else:
                # Get latest cached content
                row = await conn.fetchrow(
                    """
                    SELECT id, user_id, chapter_slug, personalized_markdown,
                           user_profile_snapshot, content_version, prompt_version, created_at
                    FROM personalized_content
                    WHERE user_id = $1 AND chapter_slug = $2
                    """,
                    user_id,
                    chapter_slug,
                )

            result = dict(row) if row else None

            # Cache the result if we got valid data, but only for latest content queries
            if result and content_version is None and prompt_version is None:
                await self.personalization_cache.cache_personalized_content(
                    user_id, chapter_slug, result.get('personalized_markdown'), ttl=7200  # 2 hours
                )

            return result

    async def upsert_personalized_content(
        self,
        user_id: str,
        chapter_slug: str,
        personalized_markdown: str,
        user_profile_snapshot: dict,
        content_version: str,
        prompt_version: str = ""
    ) -> int:
        """Insert or update personalized content cache with prompt version."""
        import json
        async with self.pool.acquire() as conn:
            row_id = await conn.fetchval(
                """
                INSERT INTO personalized_content
                    (user_id, chapter_slug, personalized_markdown, user_profile_snapshot, content_version, prompt_version, created_at)
                VALUES ($1, $2, $3, $4::jsonb, $5, $6, NOW())
                ON CONFLICT (user_id, chapter_slug) DO UPDATE SET
                    personalized_markdown = $3,
                    user_profile_snapshot = $4::jsonb,
                    content_version = $5,
                    prompt_version = $6,
                    created_at = NOW()
                RETURNING id
                """,
                user_id,
                chapter_slug,
                personalized_markdown,
                json.dumps(user_profile_snapshot),
                content_version,
                prompt_version,
            )

        # Invalidate cache after update
        await self.personalization_cache.invalidate_user_personalization(user_id)
        self.logger.info(f"Invalidated cache for personalized content: {user_id}:{chapter_slug}")

        # Cache the new version for immediate access
        await self.personalization_cache.cache_personalized_content(
            user_id, chapter_slug, personalized_markdown, ttl=7200  # 2 hours
        )

        return row_id

    # ========================================================================
    # Urdu Translation Cache (Current Version with Prompt Version)
    # ========================================================================

    async def get_urdu_translation(
        self, chapter_slug: str,
        content_version: str = None, prompt_version: str = None
    ) -> Optional[Dict[str, Any]]:
        """Get cached Urdu translation for a chapter.

        If content_version and prompt_version are provided, validate against both.
        Otherwise, just get the latest cached translation.
        """
        # Try to get from cache first when we're just fetching the latest content
        if content_version is None and prompt_version is None:
            cached_translation = await self.translation_cache.get_translation(chapter_slug, "urdu")
            if cached_translation:
                self.logger.debug(f"Cache hit for Urdu translation: {chapter_slug}")
                # If it's cached, we don't need to validate version in DB
                # In a real implementation we'd need to store versioning info with the cache
                return {
                    "urdu_markdown": cached_translation,
                    "content_version": "cached_version",  # Placeholder
                    "prompt_version": "cached_prompt_version"  # Placeholder
                }

        async with self.pool.acquire() as conn:
            if content_version is not None and prompt_version is not None:
                # Validate against both content and prompt versions
                row = await conn.fetchrow(
                    """
                    SELECT id, chapter_slug, urdu_markdown, content_version, prompt_version, created_at
                    FROM urdu_translations
                    WHERE chapter_slug = $1
                      AND content_version = $2 AND prompt_version = $3
                    """,
                    chapter_slug,
                    content_version,
                    prompt_version,
                )
            else:
                # Get latest cached translation
                row = await conn.fetchrow(
                    """
                    SELECT id, chapter_slug, urdu_markdown, content_version, prompt_version, created_at
                    FROM urdu_translations
                    WHERE chapter_slug = $1
                    """,
                    chapter_slug,
                )

            result = dict(row) if row else None

            # Cache the result if we got valid data, but only for latest content queries
            if result and content_version is None and prompt_version is None:
                await self.translation_cache.cache_translation(
                    chapter_slug, "urdu", result.get('urdu_markdown'), ttl=7200  # 2 hours
                )

            return result

    async def upsert_urdu_translation(
        self,
        chapter_slug: str,
        urdu_markdown: str,
        content_version: str,
        prompt_version: str = ""
    ) -> int:
        """Insert or update Urdu translation cache with prompt version."""
        async with self.pool.acquire() as conn:
            row_id = await conn.fetchval(
                """
                INSERT INTO urdu_translations
                    (chapter_slug, urdu_markdown, content_version, prompt_version, created_at)
                VALUES ($1, $2, $3, $4, NOW())
                ON CONFLICT (chapter_slug) DO UPDATE SET
                    urdu_markdown = $2,
                    content_version = $3,
                    prompt_version = $4,
                    created_at = NOW()
                RETURNING id
                """,
                chapter_slug,
                urdu_markdown,
                content_version,
                prompt_version,
            )

        # Invalidate cache after update
        await self.translation_cache.invalidate_translation(chapter_slug, "urdu")
        self.logger.info(f"Invalidated cache for Urdu translation: {chapter_slug}")

        # Cache the new version for immediate access
        await self.translation_cache.cache_translation(
            chapter_slug, "urdu", urdu_markdown, ttl=7200  # 2 hours
        )

        return row_id

    # ========================================================================
    # Cleanup & Maintenance
    # ========================================================================

    async def cleanup_old_rate_limit_records(self, hours: int = 1) -> int:
        """
        Delete rate limit records older than specified hours.

        Args:
            hours: Delete records older than this (default 1 hour)

        Returns:
            int: Number of records deleted
        """
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                """
                DELETE FROM rate_limit_records
                WHERE query_timestamp < NOW() - INTERVAL '1 hour' * $1
                """,
                hours,
            )

            # Extract count from "DELETE N" result
            deleted_count = int(result.split()[-1]) if result else 0
            return deleted_count

    async def cleanup_old_conversations(self, days: int = 30) -> int:
        """
        Delete conversation turns older than specified days.

        Args:
            days: Delete records older than this (default 30 days)

        Returns:
            int: Number of records deleted

        Note:
            Per FR-019, FR-047: Auto-delete 30 days after quarter end
        """
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                """
                DELETE FROM conversation_turns
                WHERE timestamp < NOW() - INTERVAL '1 day' * $1
                """,
                days,
            )

            deleted_count = int(result.split()[-1]) if result else 0
            return deleted_count

    async def health_check(self) -> bool:
        """
        Check if Neon Postgres is accessible.

        Uses a single direct connection (not a pool) for fast health checks
        that avoid cold-start delays on Neon serverless.

        Returns:
            True if healthy (SELECT 1 succeeds), False otherwise
        """
        try:
            if self.pool:
                # Reuse existing pool if already connected
                async with self.pool.acquire() as conn:
                    result = await conn.fetchval("SELECT 1")
                    return result == 1
            else:
                # Single connection — avoids creating a 5-connection pool
                conn = await asyncpg.connect(self.database_url)
                try:
                    result = await conn.fetchval("SELECT 1")
                    return result == 1
                finally:
                    await conn.close()
        except Exception:
            return False


# Singleton instance for import
_neon_client: Optional[NeonClient] = None


async def get_neon_client() -> NeonClient:
    """
    Get or create singleton Neon client instance.

    Returns:
        NeonClient: Initialized client with connection pool

    Usage:
        client = await get_neon_client()
        session = await client.create_or_update_session(session_id)
    """
    global _neon_client

    if _neon_client is None:
        _neon_client = NeonClient()
        await _neon_client.connect()

    return _neon_client
