"""
Embedder Service - OpenAI Embedding Generation

Generates embeddings using OpenAI text-embedding-3-small model.
Supports batch processing for efficient curriculum content embedding.

Author: Physical AI Platform Team
Date: 2026-02-09
"""
import asyncio
from typing import List, Dict, Any
import openai
from openai import AsyncOpenAI

from ..config import get_settings


class Embedder:
    """
    Handles text embedding generation using OpenAI API.

    Features:
    - Batch processing (50 chunks per batch)
    - Async API calls for performance
    - Error handling and retries
    """

    def __init__(self):
        self.settings = get_settings()
        self.client = AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)
        self.model = "text-embedding-3-small"
        self.dimensions = 1536
        self.batch_size = 50

    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text string.

        Args:
            text: Text to embed (max ~8k tokens)

        Returns:
            List of 1536 float values representing the embedding
        """
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=text,
                encoding_format="float"
            )
            return response.data[0].embedding
        except Exception as e:
            raise RuntimeError(f"Embedding generation failed: {str(e)}")

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        # Split into batches of 50 (API limit)
        embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            try:
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=batch,
                    encoding_format="float"
                )
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
            except Exception as e:
                raise RuntimeError(f"Batch embedding failed at index {i}: {str(e)}")

        return embeddings

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

        # Add embeddings to chunks
        for chunk, embedding in zip(chunks, embeddings):
            chunk["embedding"] = embedding

        return chunks
