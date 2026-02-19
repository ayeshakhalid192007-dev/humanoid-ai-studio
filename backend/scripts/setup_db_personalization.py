#!/usr/bin/env python3
"""
Database Migration: Personalized Chapters + Urdu Translation

Creates tables for caching personalized content, Urdu translations,
and AI generation rate limiting.

Usage: python backend/scripts/setup_db_personalization.py

Tables created:
- personalized_content (per user per chapter cached content)
- urdu_translations (per chapter cached translation)
- ai_generation_rate_limits (sliding window rate limiting)
"""
import asyncio
import asyncpg
import os
import sys
from typing import Optional

# Load backend/.env
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from dotenv import load_dotenv
_backend_env = Path(__file__).parent.parent / ".env"
if _backend_env.exists():
    load_dotenv(_backend_env, override=True)


async def setup_personalization_tables() -> bool:
    """
    Create personalized_content, urdu_translations, and ai_generation_rate_limits tables.

    Returns:
        bool: True if successful, False otherwise
    """
    database_url = os.getenv("NEON_DATABASE_URL")

    if not database_url:
        print("Error: NEON_DATABASE_URL environment variable not set")
        return False

    conn: Optional[asyncpg.Connection] = None

    try:
        print("Connecting to Neon Postgres...")
        conn = await asyncpg.connect(database_url)
        print("Connected successfully")

        # Create personalized_content table
        print("\nCreating personalized_content table...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS personalized_content (
                id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                chapter_slug TEXT NOT NULL,
                personalized_markdown TEXT NOT NULL,
                user_profile_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
                content_version TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                UNIQUE (user_id, chapter_slug)
            )
        """)
        print("personalized_content table created")

        # Create urdu_translations table
        print("\nCreating urdu_translations table...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS urdu_translations (
                id SERIAL PRIMARY KEY,
                chapter_slug TEXT NOT NULL UNIQUE,
                urdu_markdown TEXT NOT NULL,
                content_version TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)
        print("urdu_translations table created")

        # Create ai_generation_rate_limits table
        print("\nCreating ai_generation_rate_limits table...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS ai_generation_rate_limits (
                id SERIAL PRIMARY KEY,
                identifier TEXT NOT NULL,
                request_type TEXT NOT NULL,
                request_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)
        print("ai_generation_rate_limits table created")

        # Create indexes
        print("\nCreating indexes...")
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_personalized_user_chapter "
            "ON personalized_content(user_id, chapter_slug)"
        )
        print("  idx_personalized_user_chapter")

        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_personalized_chapter_version "
            "ON personalized_content(chapter_slug, content_version)"
        )
        print("  idx_personalized_chapter_version")

        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_urdu_chapter_version "
            "ON urdu_translations(chapter_slug, content_version)"
        )
        print("  idx_urdu_chapter_version")

        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_ai_rate_identifier_type_time "
            "ON ai_generation_rate_limits(identifier, request_type, request_timestamp DESC)"
        )
        print("  idx_ai_rate_identifier_type_time")

        print("\nDatabase migration completed successfully")
        print("\nTables created:")
        print("  - personalized_content (user-specific cached content)")
        print("  - urdu_translations (chapter-level cached translations)")
        print("  - ai_generation_rate_limits (AI endpoint rate limiting)")

        return True

    except asyncpg.PostgresError as e:
        print(f"\nPostgreSQL Error: {e}")
        return False

    except Exception as e:
        print(f"\nUnexpected error: {e}")
        return False

    finally:
        if conn:
            await conn.close()
            print("\nDatabase connection closed")


def main():
    print("=" * 70)
    print("Personalization & Translation Schema Migration")
    print("Physical AI & Humanoid Robotics Platform")
    print("=" * 70)

    success = asyncio.run(setup_personalization_tables())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
