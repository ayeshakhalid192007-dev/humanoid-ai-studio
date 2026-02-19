"""
Cleanup Logs - Scheduled Database Maintenance

Deletes expired conversation logs and rate limit records from Neon Postgres.

Usage:
    python backend/scripts/cleanup_logs.py --retention-days 90
    python backend/scripts/cleanup_logs.py --dry-run
"""
import asyncio
import argparse
import logging
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import asyncpg
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def cleanup_conversation_turns(
    conn: asyncpg.Connection,
    retention_days: int,
    dry_run: bool = False
) -> int:
    """Delete conversation turns older than retention period."""
    if dry_run:
        count = await conn.fetchval(
            "SELECT COUNT(*) FROM conversation_turns "
            "WHERE timestamp < NOW() - $1::interval",
            f"{retention_days} days"
        )
        logger.info(f"[DRY RUN] Would delete {count} conversation turns "
                     f"older than {retention_days} days")
        return count

    result = await conn.execute(
        "DELETE FROM conversation_turns "
        "WHERE timestamp < NOW() - $1::interval",
        f"{retention_days} days"
    )
    count = int(result.split()[-1])
    logger.info(f"Deleted {count} conversation turns "
                f"older than {retention_days} days")
    return count


async def cleanup_rate_limit_records(
    conn: asyncpg.Connection,
    dry_run: bool = False
) -> int:
    """Delete rate limit records older than 1 hour."""
    if dry_run:
        count = await conn.fetchval(
            "SELECT COUNT(*) FROM rate_limit_records "
            "WHERE query_timestamp < NOW() - INTERVAL '1 hour'"
        )
        logger.info(f"[DRY RUN] Would delete {count} expired rate limit records")
        return count

    result = await conn.execute(
        "DELETE FROM rate_limit_records "
        "WHERE query_timestamp < NOW() - INTERVAL '1 hour'"
    )
    count = int(result.split()[-1])
    logger.info(f"Deleted {count} expired rate limit records")
    return count


async def cleanup_orphaned_sessions(
    conn: asyncpg.Connection,
    retention_days: int,
    dry_run: bool = False
) -> int:
    """Delete sessions with no conversation turns older than retention period."""
    if dry_run:
        count = await conn.fetchval(
            "SELECT COUNT(*) FROM chat_sessions s "
            "WHERE s.last_active_at < NOW() - $1::interval "
            "AND NOT EXISTS ("
            "  SELECT 1 FROM conversation_turns t "
            "  WHERE t.session_id = s.session_id"
            ")",
            f"{retention_days} days"
        )
        logger.info(f"[DRY RUN] Would delete {count} orphaned sessions")
        return count

    result = await conn.execute(
        "DELETE FROM chat_sessions s "
        "WHERE s.last_active_at < NOW() - $1::interval "
        "AND NOT EXISTS ("
        "  SELECT 1 FROM conversation_turns t "
        "  WHERE t.session_id = s.session_id"
        ")",
        f"{retention_days} days"
    )
    count = int(result.split()[-1])
    logger.info(f"Deleted {count} orphaned sessions")
    return count


async def main(retention_days: int, dry_run: bool):
    """Run all cleanup tasks."""
    database_url = os.getenv("NEON_DATABASE_URL")
    if not database_url:
        logger.error("NEON_DATABASE_URL environment variable not set")
        sys.exit(1)

    logger.info(f"Starting cleanup (retention={retention_days} days, "
                f"dry_run={dry_run})")

    try:
        conn = await asyncpg.connect(database_url)

        turns_deleted = await cleanup_conversation_turns(
            conn, retention_days, dry_run
        )
        rate_deleted = await cleanup_rate_limit_records(conn, dry_run)
        sessions_deleted = await cleanup_orphaned_sessions(
            conn, retention_days, dry_run
        )

        await conn.close()

        total = turns_deleted + rate_deleted + sessions_deleted
        prefix = "[DRY RUN] " if dry_run else ""
        logger.info(
            f"{prefix}Cleanup complete: "
            f"{turns_deleted} turns, "
            f"{rate_deleted} rate records, "
            f"{sessions_deleted} sessions "
            f"({total} total)"
        )

    except asyncpg.PostgresError as e:
        logger.error(f"Database error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Clean up expired database records"
    )
    parser.add_argument(
        "--retention-days",
        type=int,
        default=90,
        help="Delete conversation turns older than N days (default: 90)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting"
    )
    args = parser.parse_args()

    asyncio.run(main(args.retention_days, args.dry_run))
