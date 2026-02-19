"""
Pytest configuration and fixtures for backend tests.

Provides mock clients for external services (OpenAI, Qdrant, Neon)
to allow testing without API credentials.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4


# ============================================================================
# Event Loop Fixture
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Mock Settings
# ============================================================================

@pytest.fixture
def mock_settings():
    """Mock application settings."""
    settings = MagicMock()
    settings.OPENAI_API_KEY = "sk-test-key"
    settings.QDRANT_URL = "https://test.qdrant.io"
    settings.QDRANT_API_KEY = "test-qdrant-key"
    settings.NEON_DATABASE_URL = "postgresql://test:test@localhost/test"
    return settings


# ============================================================================
# Mock OpenAI Client
# ============================================================================

@pytest.fixture
def mock_openai_client():
    """Mock AsyncOpenAI client for embedder and generator."""
    client = AsyncMock()

    # Mock embeddings response
    embedding_response = MagicMock()
    embedding_response.data = [MagicMock(embedding=[0.1] * 1536)]
    client.embeddings.create = AsyncMock(return_value=embedding_response)

    # Mock chat completion response
    chat_response = MagicMock()
    chat_response.choices = [
        MagicMock(message=MagicMock(content="This is a test answer about URDF joints."))
    ]
    client.chat.completions.create = AsyncMock(return_value=chat_response)

    return client


# ============================================================================
# Mock Qdrant Client
# ============================================================================

@pytest.fixture
def mock_qdrant_client():
    """Mock Qdrant client for retriever."""
    client = MagicMock()

    # Mock search results
    mock_result = MagicMock()
    mock_result.id = str(uuid4())
    mock_result.score = 0.85
    mock_result.payload = {
        "text": "URDF joints define kinematic relationships between links.",
        "module": "1",
        "lesson": "lesson-3",
        "section_title": "Joint Constraints",
        "url": "https://example.com/docs/module1/lesson3#joints"
    }

    client.search = MagicMock(return_value=[mock_result])
    return client


# ============================================================================
# Mock Neon Client
# ============================================================================

@pytest.fixture
def mock_neon_client():
    """Mock Neon Postgres client."""
    client = AsyncMock()
    client.check_rate_limit = AsyncMock(return_value=True)
    client.record_query = AsyncMock()
    client.insert_conversation_turn = AsyncMock()
    client.get_session = AsyncMock(return_value=None)
    client.create_session = AsyncMock()
    return client


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def sample_query():
    """Sample chat request data."""
    return {
        "query": "What are URDF joint limits?",
        "session_id": str(uuid4()),
        "page_context": "https://example.com/docs/module1/lesson3",
        "selection_text": None
    }


@pytest.fixture
def sample_chunks():
    """Sample retrieved curriculum chunks."""
    return [
        {
            "chunk_id": str(uuid4()),
            "text": "URDF joints define kinematic relationships between links. Joint limits constrain the range of motion.",
            "module": "1",
            "lesson": "lesson-3",
            "section_title": "Joint Constraints",
            "url": "https://example.com/docs/module1/lesson3#joints",
            "score": 0.85
        },
        {
            "chunk_id": str(uuid4()),
            "text": "Joint types include revolute, prismatic, fixed, and continuous.",
            "module": "1",
            "lesson": "lesson-3",
            "section_title": "Joint Types",
            "url": "https://example.com/docs/module1/lesson3#types",
            "score": 0.78
        }
    ]


@pytest.fixture
def sample_embedding():
    """Sample 1536-dim embedding vector."""
    return [0.1] * 1536
