"""
Verify All Service Connections

This script verifies connectivity to all external services:
- OpenAI API (embedding + chat)
- Qdrant Cloud (vector database)
- Neon Postgres (session/rate limit storage)
- Better Auth (session validation - optional)

Run with:
    python backend/scripts/verify_connections.py

Author: Physical AI Platform Team
Date: 2026-02-13
"""
import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


async def verify_openai():
    """Verify OpenAI API connectivity."""
    print("\n" + "=" * 60)
    print("1. OpenAI API")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("   ❌ OPENAI_API_KEY not set")
        return False

    print(f"   API Key: {'*' * 20}{api_key[-8:]}")

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=api_key)

        # Test embedding
        print("\n   Testing embedding generation...")
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input="Test embedding for Physical AI curriculum"
        )
        embedding = response.data[0].embedding
        print(f"   ✅ Embedding generated: {len(embedding)} dimensions")

        # Test chat completion
        print("\n   Testing chat completion...")
        chat_response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'Hello from Physical AI' in exactly 5 words"}],
            max_tokens=20
        )
        answer = chat_response.choices[0].message.content
        print(f"   ✅ Chat response: {answer}")

        return True

    except Exception as e:
        print(f"   ❌ OpenAI error: {e}")
        return False


async def verify_qdrant():
    """Verify Qdrant Cloud connectivity."""
    print("\n" + "=" * 60)
    print("2. Qdrant Cloud")
    print("=" * 60)

    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")

    if not qdrant_url or not qdrant_api_key:
        print("   ❌ QDRANT_URL or QDRANT_API_KEY not set")
        return False

    print(f"   URL: {qdrant_url}")
    print(f"   API Key: {'*' * 20}{qdrant_api_key[-8:]}")

    try:
        from qdrant_client import QdrantClient

        client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

        # Check collections
        print("\n   Checking collections...")
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]
        print(f"   ✅ Collections found: {collection_names}")

        # Check curriculum collection
        if "curriculum" in collection_names:
            info = client.get_collection("curriculum")
            print(f"\n   Curriculum collection:")
            print(f"     - Points count: {info.points_count}")
            print(f"     - Vector size: {info.config.params.vectors.size}")
            print(f"     - Distance: {info.config.params.vectors.distance.name}")
            print(f"     - Status: {info.status.name}")

            if info.points_count == 0:
                print("\n   ⚠️  Collection is empty - run embed_curriculum.py to populate")
        else:
            print("\n   ⚠️  'curriculum' collection not found - run init_qdrant.py first")

        return True

    except Exception as e:
        print(f"   ❌ Qdrant error: {e}")
        return False


async def verify_neon():
    """Verify Neon Postgres connectivity."""
    print("\n" + "=" * 60)
    print("3. Neon Postgres")
    print("=" * 60)

    database_url = os.getenv("NEON_DATABASE_URL")

    if not database_url:
        print("   ❌ NEON_DATABASE_URL not set")
        return False

    # Mask password in URL for display
    masked_url = database_url
    if "@" in database_url:
        parts = database_url.split("@")
        user_pass = parts[0].split("//")[1] if "//" in parts[0] else parts[0]
        if ":" in user_pass:
            user = user_pass.split(":")[0]
            masked_url = f"postgresql://{user}:****@{parts[1]}"
    print(f"   URL: {masked_url}")

    try:
        import asyncpg

        # Test connection
        print("\n   Testing connection...")
        conn = await asyncpg.connect(database_url)

        # Test query
        result = await conn.fetchval("SELECT 1")
        print(f"   ✅ Connection successful (SELECT 1 = {result})")

        # Check tables
        print("\n   Checking tables...")
        tables = await conn.fetch("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        table_names = [r["table_name"] for r in tables]
        print(f"   Tables found: {table_names}")

        expected_tables = ["chat_sessions", "conversation_turns", "rate_limit_records"]
        missing = [t for t in expected_tables if t not in table_names]
        if missing:
            print(f"\n   ⚠️  Missing tables: {missing}")
            print("      Run: python backend/scripts/setup_db.py")
        else:
            print(f"\n   ✅ All required tables exist")

            # Get row counts
            for table in expected_tables:
                count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
                print(f"     - {table}: {count} rows")

        await conn.close()
        return True

    except Exception as e:
        print(f"   ❌ Neon error: {e}")
        return False


async def verify_better_auth():
    """Verify Better Auth connectivity (optional)."""
    print("\n" + "=" * 60)
    print("4. Better Auth (Optional)")
    print("=" * 60)

    auth_url = os.getenv("BETTER_AUTH_URL", "http://localhost:3000")
    print(f"   URL: {auth_url}")

    try:
        import httpx

        async with httpx.AsyncClient() as client:
            # Try to reach auth endpoint
            response = await client.get(
                f"{auth_url}/api/auth/session",
                timeout=5.0
            )

            if response.status_code in [200, 401]:
                print(f"   ✅ Better Auth endpoint reachable (status: {response.status_code})")
                return True
            else:
                print(f"   ⚠️  Unexpected status: {response.status_code}")
                return False

    except httpx.ConnectError:
        print("   ⚠️  Better Auth not running (this is OK if not using auth)")
        return True
    except Exception as e:
        print(f"   ⚠️  Better Auth check failed: {e}")
        return True  # Non-critical


async def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Physical AI RAG Chatbot - Connection Verification")
    print("=" * 60)

    results = {
        "OpenAI": await verify_openai(),
        "Qdrant": await verify_qdrant(),
        "Neon": await verify_neon(),
        "BetterAuth": await verify_better_auth(),
    }

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    all_passed = True
    for service, passed in results.items():
        status = "✅ Connected" if passed else "❌ Failed"
        print(f"   {service}: {status}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n🎉 All services connected successfully!")
        print("\nNext steps:")
        print("  1. Initialize Qdrant collection: python backend/scripts/init_qdrant.py")
        print("  2. Initialize Neon schema: python backend/scripts/setup_db.py")
        print("  3. Embed curriculum content: python backend/scripts/embed_curriculum.py")
        print("  4. Start the server: uvicorn main:app --reload")
        return 0
    else:
        print("\n❌ Some services failed to connect. Check the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
