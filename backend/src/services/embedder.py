"""
Embedder Service - Local Sentence-Transformers Embedding

Generates embeddings using sentence-transformers all-MiniLM-L6-v2.
Runs fully locally — no API key required, completely free.
Model downloads automatically from HuggingFace on first use (~80MB).

Output: 384-dimensional float vectors
"""
import asyncio
from typing import List, Dict, Any
from functools import lru_cache

try:
    from sentence_transformers import SentenceTransformer as _SentenceTransformer
except ImportError:
    _SentenceTransformer = None  # type: ignore

SentenceTransformer = _SentenceTransformer


@lru_cache(maxsize=1)
def _load_model():
    """Load model once and cache it (singleton)."""
    if SentenceTransformer is None:
        raise RuntimeError("sentence-transformers not installed. Run: pip install sentence-transformers")
    return SentenceTransformer("all-MiniLM-L6-v2")


class Embedder:
    """
    Handles text embedding using local sentence-transformers model.

    Features:
    - No API key required
    - Model cached in memory after first load
    - Async-safe via thread pool executor
    - 384-dimensional output (matches Qdrant VECTOR_SIZE=384)
    """

    def __init__(self):
        self.model_name = "all-MiniLM-L6-v2"
        self.dimensions = 384
        self.batch_size = 64

    def _get_model(self) -> SentenceTransformer:
        return _load_model()

    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text string.

        Args:
            text: Text to embed

        Returns:
            List of 384 float values representing the embedding
        """
        loop = asyncio.get_running_loop()
        model = self._get_model()
        embedding = await loop.run_in_executor(None, model.encode, text)
        return embedding.tolist()

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors (each 384 floats)
        """
        if not texts:
            return []

        loop = asyncio.get_running_loop()
        model = self._get_model()

        def _encode_batch():
            return model.encode(texts, batch_size=self.batch_size, show_progress_bar=False)

        embeddings = await loop.run_in_executor(None, _encode_batch)
        return [e.tolist() for e in embeddings]

    async def embed_curriculum_chunks(
        self,
        chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Embed curriculum chunks with metadata preservation.

        Args:
            chunks: List of dicts with 'text' and metadata fields

        Returns:
            List of dicts with added 'embedding' field
        """
        texts = [chunk["text"] for chunk in chunks]
        embeddings = await self.embed_batch(texts)

        for chunk, embedding in zip(chunks, embeddings):
            chunk["embedding"] = embedding

        return chunks
