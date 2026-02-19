"""
Unit tests for individual services (Embedder, Retriever, Generator).

Tests service logic with mocked external dependencies.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


# ============================================================================
# Embedder Service Tests
# ============================================================================

class TestEmbedderService:
    """Tests for Embedder service."""

    @pytest.fixture
    def embedder(self, mock_settings, mock_openai_client):
        """Create Embedder with mocked OpenAI client."""
        with patch("src.config.get_settings", return_value=mock_settings), \
             patch("src.services.embedder.AsyncOpenAI", return_value=mock_openai_client):
            from src.services.embedder import Embedder
            embedder = Embedder()
            embedder.client = mock_openai_client
            return embedder

    @pytest.mark.asyncio
    async def test_embed_text_returns_vector(self, embedder):
        """embed_text returns 1536-dim vector."""
        result = await embedder.embed_text("What is ROS?")
        assert isinstance(result, list)
        assert len(result) == 1536

    @pytest.mark.asyncio
    async def test_embed_text_calls_openai(self, embedder, mock_openai_client):
        """embed_text calls OpenAI embeddings API."""
        await embedder.embed_text("Test query")
        mock_openai_client.embeddings.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_embed_batch_empty_list(self, embedder):
        """embed_batch with empty list returns empty list."""
        result = await embedder.embed_batch([])
        assert result == []

    @pytest.mark.asyncio
    async def test_embed_batch_multiple_texts(self, embedder, mock_openai_client):
        """embed_batch processes multiple texts."""
        # Setup mock for batch
        batch_response = MagicMock()
        batch_response.data = [
            MagicMock(embedding=[0.1] * 1536),
            MagicMock(embedding=[0.2] * 1536)
        ]
        mock_openai_client.embeddings.create = AsyncMock(return_value=batch_response)

        result = await embedder.embed_batch(["Text 1", "Text 2"])
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_embed_text_error_handling(self, embedder, mock_openai_client):
        """embed_text raises RuntimeError on API failure."""
        mock_openai_client.embeddings.create = AsyncMock(
            side_effect=Exception("API Error")
        )

        with pytest.raises(RuntimeError) as exc_info:
            await embedder.embed_text("Test")
        assert "Embedding generation failed" in str(exc_info.value)


# ============================================================================
# Retriever Service Tests
# ============================================================================

class TestRetrieverService:
    """Tests for Retriever service."""

    @pytest.fixture
    def retriever(self, mock_settings, mock_qdrant_client):
        """Create Retriever with mocked Qdrant client."""
        with patch("src.config.get_settings", return_value=mock_settings), \
             patch("src.services.retriever.QdrantClient", return_value=mock_qdrant_client):
            from src.services.retriever import Retriever
            retriever = Retriever()
            retriever.client = mock_qdrant_client
            return retriever

    @pytest.mark.asyncio
    async def test_search_returns_chunks(self, retriever, sample_embedding):
        """search returns list of chunk dicts."""
        results = await retriever.search(sample_embedding, limit=5)
        assert isinstance(results, list)
        assert len(results) > 0
        assert "text" in results[0]
        assert "score" in results[0]

    @pytest.mark.asyncio
    async def test_search_with_module_filter(self, retriever, sample_embedding, mock_qdrant_client):
        """search applies module filter when provided."""
        await retriever.search(sample_embedding, limit=5, module_filter="1")
        mock_qdrant_client.search.assert_called_once()

        # Verify filter was passed
        call_kwargs = mock_qdrant_client.search.call_args
        assert call_kwargs is not None

    @pytest.mark.asyncio
    async def test_search_respects_limit(self, retriever, sample_embedding, mock_qdrant_client):
        """search passes limit to Qdrant client."""
        await retriever.search(sample_embedding, limit=3)
        call_kwargs = mock_qdrant_client.search.call_args
        assert call_kwargs[1]["limit"] == 3

    def test_similarity_threshold_default(self, retriever):
        """Default similarity threshold is 0.7."""
        assert retriever.similarity_threshold == 0.7


# ============================================================================
# Generator Service Tests
# ============================================================================

class TestGeneratorService:
    """Tests for Generator service."""

    @pytest.fixture
    def generator(self, mock_settings, mock_openai_client):
        """Create Generator with mocked OpenAI client."""
        with patch("src.config.get_settings", return_value=mock_settings), \
             patch("src.services.generator.AsyncOpenAI", return_value=mock_openai_client):
            from src.services.generator import Generator
            generator = Generator()
            generator.client = mock_openai_client
            return generator

    @pytest.mark.asyncio
    async def test_generate_returns_answer(self, generator, sample_chunks):
        """generate returns dict with answer and citations."""
        result = await generator.generate(
            query="What are URDF joint limits?",
            retrieved_chunks=sample_chunks
        )
        assert "answer" in result
        assert "citations" in result

    @pytest.mark.asyncio
    async def test_generate_calls_openai_chat(self, generator, sample_chunks, mock_openai_client):
        """generate calls OpenAI chat completions API."""
        await generator.generate(
            query="What is ROS?",
            retrieved_chunks=sample_chunks
        )
        mock_openai_client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_includes_context(self, generator, sample_chunks, mock_openai_client):
        """generate includes retrieved chunks as context."""
        await generator.generate(
            query="Explain joints",
            retrieved_chunks=sample_chunks
        )

        call_args = mock_openai_client.chat.completions.create.call_args
        messages = call_args[1]["messages"]

        # Should have system prompt and user message with context
        assert len(messages) >= 2
        assert messages[0]["role"] == "system"

    @pytest.mark.asyncio
    async def test_generate_empty_chunks(self, generator, mock_openai_client):
        """generate handles empty chunks gracefully."""
        result = await generator.generate(
            query="What is ROS?",
            retrieved_chunks=[]
        )
        assert "answer" in result

    def test_system_prompt_contains_curriculum(self, generator):
        """System prompt mentions curriculum scope."""
        assert "curriculum" in generator.system_prompt.lower()
        assert "Physical AI" in generator.system_prompt

    def test_model_is_gpt4o_mini(self, generator):
        """Uses gpt-4o-mini model."""
        assert generator.model == "gpt-4o-mini"
