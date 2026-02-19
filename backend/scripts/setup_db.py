"""
Initialize Neon Postgres schema for RAG chatbot.

Run once during deployment setup with:
    python backend/scripts/setup_db.py

Requirements:
- NEON_DATABASE_URL environment variable must be set
- asyncpg package installed (pip install asyncpg)

Schema created:
- chat_sessions table with session_id, created_at, last_active_at, metadata
- conversation_turns table with turn_id, session_id, query, response, retrieved_chunks, timestamp, page_context, metadata
- rate_limit_records table with record_id, session_id, query_timestamp
- All indexes per data-model.md

Author: Physical AI Platform Team
Date: 2026-02-09
"""
import asyncio
import asyncpg
import os
import sys
from typing import Optional


async def setup_database() -> bool:
    """
    Initialize Neon Postgres schema with tables and indexes.

    Returns:
        bool: True if successful, False otherwise
    """
    database_url = os.getenv("NEON_DATABASE_URL")

    if not database_url:
        print("❌ Error: NEON_DATABASE_URL environment variable not set")
        print("   Please set it in .env file or environment")
        return False

    conn: Optional[asyncpg.Connection] = None

    try:
        print("🔌 Connecting to Neon Postgres...")
        conn = await asyncpg.connect(database_url)
        print("✅ Connected successfully")

        # Create chat_sessions table
        print("\n📋 Creating chat_sessions table...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                last_active_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                metadata JSONB DEFAULT '{}'::jsonb
            )
        """)
        print("✅ chat_sessions table created")

        # Create conversation_turns table
        print("\n📋 Creating conversation_turns table...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS conversation_turns (
                turn_id SERIAL PRIMARY KEY,
                session_id UUID NOT NULL REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
                query TEXT NOT NULL CHECK (char_length(query) BETWEEN 1 AND 500),
                response TEXT NOT NULL,
                retrieved_chunks JSONB NOT NULL DEFAULT '[]'::jsonb,
                timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                page_context TEXT,
                metadata JSONB DEFAULT '{}'::jsonb
            )
        """)
        print("✅ conversation_turns table created")

        # Create rate_limit_records table
        print("\n📋 Creating rate_limit_records table...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS rate_limit_records (
                record_id SERIAL PRIMARY KEY,
                session_id UUID NOT NULL REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
                query_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)
        print("✅ rate_limit_records table created")

        # Create indexes
        print("\n🔍 Creating indexes...")
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_sessions_last_active "
            "ON chat_sessions(last_active_at DESC)"
        )
        print("  ✅ idx_sessions_last_active")

        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_turns_session_time "
            "ON conversation_turns(session_id, timestamp DESC)"
        )
        print("  ✅ idx_turns_session_time")

        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_turns_timestamp "
            "ON conversation_turns(timestamp DESC)"
        )
        print("  ✅ idx_turns_timestamp")

        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_rate_limit_session_time "
            "ON rate_limit_records(session_id, query_timestamp DESC)"
        )
        print("  ✅ idx_rate_limit_session_time")

        print("\n✅ Database schema initialized successfully")
        print("\nTables created:")
        print("  - chat_sessions (session tracking)")
        print("  - conversation_turns (Q&A logging)")
        print("  - rate_limit_records (20 queries/hour enforcement)")
        print("\nIndexes created:")
        print("  - idx_sessions_last_active (session activity queries)")
        print("  - idx_turns_session_time (conversation history retrieval)")
        print("  - idx_turns_timestamp (analytics queries)")
        print("  - idx_rate_limit_session_time (sliding window rate limit)")

        return True

    except asyncpg.PostgresError as e:
        print(f"\n❌ PostgreSQL Error: {e}")
        print(f"   Error code: {e.sqlstate if hasattr(e, 'sqlstate') else 'N/A'}")
        return False

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

    finally:
        if conn:
            await conn.close()
            print("\n🔌 Database connection closed")


def main():
    """Main entry point for script execution."""
    print("=" * 70)
    print("Neon Postgres Schema Initialization")
    print("Physical AI & Humanoid Robotics Platform - RAG Chatbot")
    print("=" * 70)

    success = asyncio.run(setup_database())

    if success:
        print("\n🎉 Setup complete! Database ready for RAG chatbot.")
        sys.exit(0)
    else:
        print("\n❌ Setup failed. Please check error messages above.")
        print("\nTroubleshooting:")
        print("  1. Verify NEON_DATABASE_URL is set correctly")
        print("  2. Check network connectivity to Neon Postgres")
        print("  3. Ensure database exists and credentials are valid")
        sys.exit(1)


if __name__ == "__main__":
    main()
