#!/usr/bin/env python3
"""
End-to-end RAG pipeline validation script.

Tests the full pipeline without starting the FastAPI server.
- Mock mode: uses mock services, validates flow
- Production mode: connects to real services, runs sample query

Usage:
    python backend/scripts/run_pipeline.py              # auto-detect mode from .env
    python backend/scripts/run_pipeline.py --mock        # force mock mode
    python backend/scripts/run_pipeline.py --production  # force production mode
"""
import asyncio
import sys
import os
import time
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment
from dotenv import load_dotenv
_backend_env = Path(__file__).parent.parent / ".env"
if _backend_env.exists():
    load_dotenv(_backend_env, override=True)
else:
    _root_env = Path(__file__).parent.parent.parent / ".env"
    if _root_env.exists():
        load_dotenv(_root_env, override=True)


def print_header(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_step(step: int, description: str):
    print(f"\n  [{step}] {description}")
    print("  " + "-" * 60)


async def run_mock_pipeline():
    """Run the pipeline using mock services."""
    from src.services.mock_services import (
        MockEmbedder,
        MockRetriever,
        MockGenerator,
        MockNeonClient,
    )

    query = "What is ROS 2 and how do nodes communicate?"
    session_id = "test-session-001"

    print_step(1, "Initialize mock services")
    embedder = MockEmbedder()
    retriever = MockRetriever()
    generator = MockGenerator()
    neon = MockNeonClient()
    print("    Embedder:  MockEmbedder (random 1536-d vectors)")
    print("    Retriever: MockRetriever (keyword matching)")
    print("    Generator: MockGenerator (template responses)")
    print("    Neon:      MockNeonClient (in-memory)")

    print_step(2, f"Generate embedding for query")
    print(f"    Query: \"{query}\"")
    t0 = time.perf_counter()
    embedding = await embedder.embed(query)
    t1 = time.perf_counter()
    print(f"    Embedding dims: {len(embedding)}")
    print(f"    Time: {(t1 - t0) * 1000:.1f}ms")

    print_step(3, "Search for relevant chunks")
    t0 = time.perf_counter()
    chunks = await retriever.search(query, limit=5, score_threshold=0.7)
    t1 = time.perf_counter()
    print(f"    Found {len(chunks)} chunks")
    for i, chunk in enumerate(chunks[:3], 1):
        title = chunk["payload"]["title"]
        score = chunk["score"]
        print(f"      {i}. [{score:.2f}] {title}")
    print(f"    Time: {(t1 - t0) * 1000:.1f}ms")

    print_step(4, "Check rate limit")
    t0 = time.perf_counter()
    rate_check = await neon.check_rate_limit(session_id, max_queries=20)
    t1 = time.perf_counter()
    print(f"    Allowed: {rate_check['allowed']}")
    print(f"    Remaining: {rate_check['remaining']}")
    print(f"    Time: {(t1 - t0) * 1000:.1f}ms")

    if not rate_check["allowed"]:
        print("    BLOCKED by rate limit - stopping")
        return False

    print_step(5, "Generate answer")
    t0 = time.perf_counter()
    result = await generator.generate(query, chunks, max_tokens=2000)
    t1 = time.perf_counter()
    answer = result["answer"]
    preview = answer[:200].replace('\n', ' ').strip()
    print(f"    Answer preview: {preview}...")
    print(f"    Citations: {len(result['citations'])}")
    print(f"    Model: {result['model']}")
    print(f"    Time: {(t1 - t0) * 1000:.1f}ms")

    print_step(6, "Log conversation & record query")
    t0 = time.perf_counter()
    conv_id = await neon.log_conversation(
        session_id=session_id,
        query=query,
        response=answer,
        citations=result["citations"],
    )
    await neon.record_query(session_id)
    t1 = time.perf_counter()
    print(f"    Conversation ID: {conv_id}")
    print(f"    Time: {(t1 - t0) * 1000:.1f}ms")

    return True


async def run_production_pipeline():
    """Run the pipeline using real services."""
    from src.config import get_settings

    settings = get_settings()

    print_step(1, "Verify configuration")
    checks = {
        "OPENAI_API_KEY": bool(settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith("sk-proj-your")),
        "QDRANT_URL": bool(settings.QDRANT_URL and "your-cluster" not in settings.QDRANT_URL),
        "QDRANT_API_KEY": bool(settings.QDRANT_API_KEY and settings.QDRANT_API_KEY != "your-qdrant-api-key-here"),
        "NEON_DATABASE_URL": bool(settings.NEON_DATABASE_URL and "user:password" not in settings.NEON_DATABASE_URL),
    }

    all_ok = True
    for key, ok in checks.items():
        status = "OK" if ok else "MISSING/PLACEHOLDER"
        print(f"    {key}: {status}")
        if not ok:
            all_ok = False

    if not all_ok:
        print("\n    ERROR: Missing production credentials. Configure .env or use --mock")
        return False

    print_step(2, "Test Qdrant connectivity")
    try:
        from src.db.qdrant_client import QdrantClient
        qdrant = QdrantClient()
        # Just verifying instantiation succeeds with real creds
        print("    Qdrant client initialized successfully")
    except Exception as e:
        print(f"    ERROR: {e}")
        return False

    print_step(3, "Test Neon connectivity")
    neon = None
    try:
        from src.db.neon_client import NeonClient
        neon = NeonClient()
        await neon.connect()
        healthy = await neon.health_check()
        print(f"    Neon health: {'OK' if healthy else 'FAILED'}")
        if not healthy:
            return False
    except Exception as e:
        print(f"    ERROR: {e}")
        return False

    print_step(4, "Run RAG pipeline query")
    try:
        from src.services.rag_pipeline import RAGPipeline
        pipeline = RAGPipeline()

        query = "What is ROS 2 and how do nodes communicate?"
        print(f"    Query: \"{query}\"")

        t0 = time.perf_counter()
        result = await pipeline.process_query(
            query=query,
            session_id="test-pipeline-run",
        )
        t1 = time.perf_counter()

        print(f"    Answer length: {len(result['answer'])} chars")
        print(f"    Citations: {len(result['citations'])}")
        print(f"    Retrieved chunks: {len(result['retrieved_chunks'])}")
        print(f"    Total time: {(t1 - t0) * 1000:.0f}ms")

        preview = result['answer'][:200].replace('\n', ' ').strip()
        print(f"    Preview: {preview}...")
    except Exception as e:
        print(f"    ERROR: {e}")
        return False
    finally:
        if neon:
            await neon.close()

    return True


async def main():
    # Parse args
    force_mock = "--mock" in sys.argv
    force_prod = "--production" in sys.argv

    if force_mock and force_prod:
        print("ERROR: Cannot specify both --mock and --production")
        sys.exit(1)

    # Determine mode
    if force_mock:
        mock_mode = True
    elif force_prod:
        mock_mode = False
    else:
        mock_mode = os.getenv("MOCK_MODE", "false").lower() in ("true", "1", "yes")

    mode_label = "MOCK" if mock_mode else "PRODUCTION"

    print_header(f"RAG PIPELINE END-TO-END TEST ({mode_label} MODE)")

    t_start = time.perf_counter()

    if mock_mode:
        success = await run_mock_pipeline()
    else:
        success = await run_production_pipeline()

    t_end = time.perf_counter()

    print_header("RESULT")
    if success:
        print(f"  PASS - Pipeline completed successfully in {(t_end - t_start) * 1000:.0f}ms")
    else:
        print(f"  FAIL - Pipeline encountered errors")

    print("=" * 70)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
