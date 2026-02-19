"""Database migration manager for PostgreSQL schema management.

This module provides a migration framework similar to Alembic but tailored for the Physical AI platform.
It creates standardized schema management with versioned migrations and rollback support.
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

import asyncpg


class Migration:
    """Represents a single database migration."""

    def __init__(self, version: str, name: str, up_sql: str, down_sql: Optional[str] = None, timestamp: Optional[datetime] = None):
        self.version = version
        self.name = name
        self.up_sql = up_sql
        self.down_sql = down_sql
        self.timestamp = timestamp or datetime.utcnow()
        self.applied_at = None

    def to_dict(self) -> dict:
        """Convert migration to dictionary format."""
        return {
            "version": self.version,
            "name": self.name,
            "timestamp": self.timestamp.isoformat(),
            "applied_at": self.applied_at.isoformat() if self.applied_at else None
        }


class MigrationManager:
    """Manages database migrations with version tracking and rollback capabilities."""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.pool: Optional[asyncpg.Pool] = None
        self.migrations_dir = Path(__file__).parent.parent / "migrations" / "versions"
        self.migrations_dir.mkdir(exist_ok=True)

    async def initialize_pool(self):
        """Initialize the connection pool."""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=1,
                max_size=5,
                command_timeout=30.0
            )

    async def close_pool(self):
        """Close the connection pool."""
        if self.pool:
            await self.pool.close()

    async def ensure_schema_table(self):
        """Ensure the schema_migrations table exists."""
        if not self.pool:
            await self.initialize_pool()

        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );

                -- Ensure we can track migration execution order
                CREATE INDEX IF NOT EXISTS idx_schema_migrations_applied_at
                ON schema_migrations(applied_at);
            """)

    async def get_applied_migrations(self) -> List[str]:
        """Get list of already applied migration versions."""
        if not self.pool:
            await self.initialize_pool()

        async with self.pool.acquire() as conn:
            rows = await conn.fetch("SELECT version FROM schema_migrations ORDER BY applied_at")
            return [row['version'] for row in rows]

    async def record_migration_applied(self, version: str, name: str):
        """Record that a migration has been applied."""
        if not self.pool:
            await self.initialize_pool()

        async with self.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO schema_migrations (version, name, applied_at) VALUES ($1, $2, NOW())",
                version, name
            )

    async def record_migration_rolled_back(self, version: str):
        """Remove migration record when rolled back."""
        if not self.pool:
            await self.initialize_pool()

        async with self.pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM schema_migrations WHERE version = $1",
                version
            )

    def load_migrations(self) -> List[Migration]:
        """Load all available migrations from migration files."""
        migrations = []
        migration_files = sorted(self.migrations_dir.glob("*.sql"))

        for migration_file in migration_files:
            # Extract version from filename: {version}_{name}.sql
            parts = migration_file.stem.split('_', 2)  # version_name_suffix (in case name includes underscore)
            if len(parts) >= 2:
                version = parts[0]
                name = parts[1] if len(parts) == 2 else '_'.join(parts[1:])

                content = migration_file.read_text()

                # Split content if down migration is included (separated by --DOWN--)
                parts = content.split('--DOWN--', 1)
                up_sql = parts[0].strip()
                down_sql = parts[1].strip() if len(parts) > 1 else None

                migrations.append(Migration(version, name, up_sql, down_sql))

        return sorted(migrations, key=lambda m: m.version)

    async def migrate(self, target_version: Optional[str] = None):
        """Run migrations up to the target version."""
        if not self.pool:
            await self.initialize_pool()

        await self.ensure_schema_table()

        all_migrations = self.load_migrations()
        applied_versions = await self.get_applied_migrations()

        # Filter migrations to run (only unapplied migrations or all if targeting a specific version)
        migrations_to_run = []

        for migration in all_migrations:
            if target_version and migration.version > target_version:
                continue

            if migration.version not in applied_versions:
                migrations_to_run.append(migration)

        print(f"Running {len(migrations_to_run)} migrations...")

        for migration in migrations_to_run:
            print(f"Applying migration {migration.version}: {migration.name}")

            try:
                if not self.pool:
                    await self.initialize_pool()

                async with self.pool.acquire() as conn:
                    async with conn.transaction():
                        # Execute the migration
                        await conn.execute(migration.up_sql)

                        # Record the migration as applied
                        await self.record_migration_applied(migration.version, migration.name)

                print(f"✓ Migration {migration.version} applied successfully")
            except Exception as e:
                print(f"✗ Failed to apply migration {migration.version}: {str(e)}")
                raise

    async def rollback(self, target_version: Optional[str] = None, steps: int = 1):
        """Roll back migrations to a specific version or number of steps."""
        if not self.pool:
            await self.initialize_pool()

        await self.ensure_schema_table()

        applied_versions = await self.get_applied_migrations()
        all_migrations = self.load_migrations()

        # Create map of version to migration object
        migration_map = {m.version: m for m in all_migrations}

        # Determine versions to rollback (from newest to oldest)
        versions_to_rollback = []

        if target_version:
            # Rollback to a specific version (find versions newer than target)
            versions_to_rollback = [v for v in applied_versions if v > target_version]
        else:
            # Rollback specified number of steps (oldest applied migrations)
            versions_to_rollback = applied_versions[-steps:] if applied_versions else []

        # Sort in reverse order (newest to oldest) so we rollback in correct order
        versions_to_rollback = sorted(versions_to_rollback, reverse=True)

        print(f"Rolling back {len(versions_to_rollback)} migrations...")

        for version in versions_to_rollback:
            migration = migration_map.get(version)
            if not migration or not migration.down_sql:
                print(f"⚠️ Cannot rollback migration {version}: no rollback script available")
                continue

            print(f"Rolling back migration {version}: {migration.name}")

            try:
                if not self.pool:
                    await self.initialize_pool()

                async with self.pool.acquire() as conn:
                    async with conn.transaction():
                        # Execute the rollback
                        await conn.execute(migration.down_sql)

                        # Remove migration record
                        await self.record_migration_rolled_back(migration.version)

                print(f"✓ Migration {version} rolled back successfully")
            except Exception as e:
                print(f"✗ Failed to rollback migration {version}: {str(e)}")
                raise

    async def show_status(self):
        """Show migration status."""
        await self.ensure_schema_table()
        all_migrations = self.load_migrations()
        applied_versions = set(await self.get_applied_migrations())

        print("\nMigration Status:")
        print("-" * 80)

        if not all_migrations:
            print("No migration files found.")
            return

        for migration in all_migrations:
            status = "✓ Applied" if migration.version in applied_versions else "⏳ Pending"
            print(f"{migration.version:15} {migration.name:35} {status}")


# Convenience functions
async def run_migrations(connection_string: str, target_version: Optional[str] = None):
    """Run all pending migrations."""
    migrator = MigrationManager(connection_string)
    try:
        await migrator.migrate(target_version)
    finally:
        await migrator.close_pool()


async def rollback_migrations(connection_string: str, target_version: Optional[str] = None, steps: int = 1):
    """Rollback applied migrations."""
    migrator = MigrationManager(connection_string)
    try:
        await migrator.rollback(target_version, steps)
    finally:
        await migrator.close_pool()


async def show_migration_status(connection_string: str):
    """Show migration status."""
    migrator = MigrationManager(connection_string)
    try:
        await migrator.show_status()
    finally:
        await migrator.close_pool()


# Migration file generation
def create_migration_file(version: str, name: str, up_sql: str, down_sql: Optional[str] = None):
    """Create a new migration file."""
    migrations_dir = Path(__file__).parent / "versions"
    migrations_dir.mkdir(exist_ok=True)

    filename = migrations_dir / f"{version}_{name.replace(' ', '_').replace('/', '_')}.sql"

    content = up_sql
    if down_sql:
        content += f"\n\n--DOWN--\n{down_sql}"

    with open(filename, 'w') as f:
        f.write(content)

    print(f"Created migration file: {filename}")
    return filename


# Default migrations for the Physical AI platform
def create_default_migrations():
    """Create default migration files based on current schema."""

    # Auth database migration
    auth_migration_sql = """
-- Schema creation for Better Auth with custom fields

-- Create Better Auth core tables (matching auth-server schema)
CREATE TABLE IF NOT EXISTS "user" (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    "emailVerified" BOOLEAN NOT NULL DEFAULT false,
    image TEXT,
    role TEXT DEFAULT 'student',
    "onboardingCompleted" BOOLEAN DEFAULT false,
    "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS "session" (
    id TEXT PRIMARY KEY,
    "expiresAt" TIMESTAMP NOT NULL,
    token TEXT NOT NULL UNIQUE,
    "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    "ipAddress" TEXT,
    "userAgent" TEXT,
    "userId" TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "account" (
    id TEXT PRIMARY KEY,
    "accountId" TEXT NOT NULL,
    "providerId" TEXT NOT NULL,
    "userId" TEXT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    "accessToken" TEXT,
    "refreshToken" TEXT,
    "idToken" TEXT,
    "accessTokenExpiresAt" TIMESTAMP,
    "refreshTokenExpiresAt" TIMESTAMP,
    scope TEXT,
    password TEXT,
    "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS "verification" (
    id TEXT PRIMARY KEY,
    identifier TEXT NOT NULL,
    value TEXT NOT NULL,
    "expiresAt" TIMESTAMP NOT NULL,
    "createdAt" TIMESTAMP DEFAULT NOW(),
    "updatedAt" TIMESTAMP DEFAULT NOW()
);

-- Custom user profiles table
CREATE TABLE IF NOT EXISTS user_profiles (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id TEXT UNIQUE NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    software_background TEXT NOT NULL DEFAULT 'none',
    hardware_background TEXT NOT NULL DEFAULT 'none',
    robotics_knowledge TEXT NOT NULL DEFAULT 'none'
      CHECK (robotics_knowledge IN ('none', 'beginner', 'intermediate', 'advanced')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Remove CHECK constraints on background fields to allow free-text
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name LIKE '%software_background%'
        AND table_name = 'user_profiles'
    ) THEN
        ALTER TABLE user_profiles DROP CONSTRAINT IF EXISTS
            (SELECT constraint_name FROM information_schema.table_constraints
             WHERE constraint_name LIKE '%software_background%'
             AND table_name = 'user_profiles' LIMIT 1);
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name LIKE '%hardware_background%'
        AND table_name = 'user_profiles'
    ) THEN
        ALTER TABLE user_profiles DROP CONSTRAINT IF EXISTS
            (SELECT constraint_name FROM information_schema.table_constraints
             WHERE constraint_name LIKE '%hardware_background%'
             AND table_name = 'user_profiles' LIMIT 1);
    END IF;
END $$;

-- Update user_profiles to allow free-text backgrounds
ALTER TABLE user_profiles ALTER COLUMN software_background SET DEFAULT 'none';
ALTER TABLE user_profiles ALTER COLUMN hardware_background SET DEFAULT 'none';
    """

    # Backend database migration
    backend_migration_sql = """
-- Backend schema for chatbot and AI services

CREATE TABLE IF NOT EXISTS chat_sessions (
    session_id UUID PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS conversation_turns (
    turn_id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    query VARCHAR(1000) NOT NULL
        CHECK (LENGTH(query) >= 1 AND LENGTH(query) <= 1000),
    response TEXT NOT NULL,
    retrieved_chunks JSONB DEFAULT '[]'::jsonb
        CHECK (jsonb_array_length(retrieved_chunks) <= 5),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    page_context VARCHAR(500),
    metadata JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS rate_limit_records (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    query_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Personalization tables
CREATE TABLE IF NOT EXISTS personalized_content (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    chapter_slug TEXT NOT NULL,
    personalized_markdown TEXT NOT NULL,
    user_profile_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    content_version TEXT NOT NULL,
    prompt_version TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, chapter_slug)
);

CREATE TABLE IF NOT EXISTS urdu_translations (
    id SERIAL PRIMARY KEY,
    chapter_slug TEXT NOT NULL UNIQUE,
    urdu_markdown TEXT NOT NULL,
    content_version TEXT NOT NULL,
    prompt_version TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- AI generation rate limiting
CREATE TABLE IF NOT EXISTS ai_generation_rate_limits (
    id SERIAL PRIMARY KEY,
    identifier TEXT NOT NULL,
    request_type TEXT NOT NULL,
    request_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Agent execution logging
CREATE TABLE IF NOT EXISTS agent_execution_logs (
    id SERIAL PRIMARY KEY,
    agent_type TEXT NOT NULL,
    grounding_policy TEXT NOT NULL,
    skills_used TEXT[] NOT NULL,
    skills_detail JSONB NOT NULL DEFAULT '[]'::jsonb,
    token_count INTEGER,
    model TEXT NOT NULL,
    latency_ms INTEGER NOT NULL,
    cached BOOLEAN NOT NULL DEFAULT FALSE,
    request_metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_agent_logs_created
    ON agent_execution_logs (created_at);
CREATE INDEX IF NOT EXISTS idx_agent_logs_type
    ON agent_execution_logs (agent_type);
CREATE INDEX IF NOT EXISTS idx_conversations_session
    ON conversation_turns (session_id);
CREATE INDEX IF NOT EXISTS idx_conversations_timestamp
    ON conversation_turns (timestamp);
CREATE INDEX IF NOT EXISTS idx_rate_limit_session_time
    ON rate_limit_records (session_id, query_timestamp);
CREATE INDEX IF NOT EXISTS idx_ai_rate_limits_id_type_time
    ON ai_generation_rate_limits (identifier, request_type, request_timestamp);

-- Auto-cleanup functions (can be called by background tasks)
CREATE OR REPLACE FUNCTION cleanup_old_conversations(p_days INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM conversation_turns
    WHERE timestamp < NOW() - (p_days || ' days')::INTERVAL;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION cleanup_old_rate_limit_records(p_hours INTEGER DEFAULT 24)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM rate_limit_records
    WHERE query_timestamp < NOW() - (p_hours || ' hours')::INTERVAL;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION cleanup_agent_execution_logs(p_days INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM agent_execution_logs
    WHERE created_at < NOW() - (p_days || ' days')::INTERVAL;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Grant basic permissions (if not already granted)
GRANT USAGE ON SCHEMA public TO postgres;
    """

    # Backend rollback
    backend_rollback_sql = """
-- This is a simplified rollback - in production you'd need to handle dependencies carefully
-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS agent_execution_logs;
DROP TABLE IF EXISTS ai_generation_rate_limits;
DROP TABLE IF EXISTS urdu_translations;
DROP TABLE IF EXISTS personalized_content;
DROP TABLE IF EXISTS rate_limit_records;
DROP TABLE IF EXISTS conversation_turns;
DROP TABLE IF EXISTS chat_sessions;

-- Drop functions
DROP FUNCTION IF EXISTS cleanup_old_conversations(INTEGER);
DROP FUNCTION IF EXISTS cleanup_old_rate_limit_records(INTEGER);
DROP FUNCTION IF EXISTS cleanup_agent_execution_logs(INTEGER);
    """

    # Auth rollback
    auth_rollback_sql = """
-- Rollback Auth tables (be careful in production - this deletes user data)
DROP TABLE IF EXISTS user_profiles;
DROP TABLE IF EXISTS verification;
DROP TABLE IF EXISTS account;
DROP TABLE IF EXISTS "session";
DROP TABLE IF EXISTS "user";
    """

    # Create the migration files
    create_migration_file("001", "auth_schema", auth_migration_sql, auth_rollback_sql)
    create_migration_file("002", "backend_schema", backend_migration_sql, backend_rollback_sql)


# Entry point for command line
if __name__ == "__main__":
    import sys
    import os

    if len(sys.argv) < 2:
        print("Usage: python migration_manager.py [migrate|rollback|status|init]")
        sys.exit(1)

    command = sys.argv[1].lower()

    # Load environment
    db_url = os.getenv("NEON_DATABASE_URL")
    if not db_url:
        print("ERROR: NEON_DATABASE_URL environment variable not set")
        sys.exit(1)

    async def main():
        if command == "migrate":
            await run_migrations(db_url)
        elif command == "rollback":
            steps = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            await rollback_migrations(db_url, steps=steps)
        elif command == "status":
            await show_migration_status(db_url)
        elif command == "init":
            create_default_migrations()
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    asyncio.run(main())