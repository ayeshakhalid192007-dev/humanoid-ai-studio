"""
Chapter Retriever Service

Retrieves all chunks for a chapter from Qdrant by module + lesson filter,
reconstructs full chapter Markdown, and provides content version hash.

Author: Physical AI Platform Team
Date: 2026-02-16
"""
import asyncio
import hashlib
import re
from pathlib import Path
from typing import Dict, Any, Optional, List

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

from ..config import get_settings


class ChapterRetriever:
    """
    Retrieves full chapter content from Qdrant vector database.

    Uses metadata filtering (module + lesson) to get all chunks for a chapter,
    then reconstructs the original Markdown content in order.
    """

    def __init__(self):
        self.settings = get_settings()
        if not QDRANT_AVAILABLE:
            raise ImportError(
                "qdrant-client package is required. "
                "Install with: pip install qdrant-client"
            )
        self.client = QdrantClient(
            url=self.settings.QDRANT_URL,
            api_key=self.settings.QDRANT_API_KEY
        )
        self.collection_name = "curriculum"
        # Filesystem fallback: project_root/book/docs/
        self._docs_dir = Path(__file__).resolve().parent.parent.parent.parent / "book" / "docs"

    def _parse_chapter_slug(self, chapter_slug: str) -> Dict[str, str]:
        """
        Parse chapter slug into module and lesson components.

        Args:
            chapter_slug: e.g., 'module1/lesson1-ros2-basics'

        Returns:
            Dict with 'module' and 'lesson' keys
        """
        parts = chapter_slug.strip("/").split("/")
        if len(parts) < 2:
            raise ValueError(f"Invalid chapter_slug format: {chapter_slug}")

        module_part = parts[0]  # e.g., 'module1'
        lesson_part = parts[1]  # e.g., 'lesson1-ros2-basics'

        # Extract module number (e.g., 'module1' -> '1')
        module_num = module_part.replace("module", "")

        return {"module": module_num, "lesson": lesson_part}

    async def get_chapter_content(
        self, chapter_slug: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve all chunks for a chapter and reconstruct Markdown content.

        Args:
            chapter_slug: Docusaurus doc slug (e.g., 'module1/lesson1-ros2-basics')

        Returns:
            Dict with 'content' (reconstructed Markdown), 'content_version' (hash),
            and 'chunk_count'. None if chapter not found.
        """
        try:
            parsed = self._parse_chapter_slug(chapter_slug)
        except ValueError:
            return None

        try:
            # Build filter for module + lesson
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="module",
                        match=MatchValue(value=parsed["module"])
                    ),
                    FieldCondition(
                        key="lesson",
                        match=MatchValue(value=parsed["lesson"])
                    ),
                ]
            )

            # Scroll to get ALL chunks (no similarity threshold, no query vector)
            # Wrap sync Qdrant call in asyncio.to_thread to avoid blocking the event loop
            results, _ = await asyncio.to_thread(
                self.client.scroll,
                collection_name=self.collection_name,
                scroll_filter=search_filter,
                limit=200,  # Max chunks per chapter
                with_payload=True,
                with_vectors=False,
            )

            if not results:
                # Fallback: read directly from filesystem
                return await self._read_from_filesystem(chapter_slug)

            # Sort by point ID to preserve original chunk ordering
            sorted_chunks = sorted(results, key=lambda r: str(r.id))

            # Reconstruct chapter content
            content_parts = []
            for chunk in sorted_chunks:
                text = chunk.payload.get("text", "")
                if text.strip():
                    content_parts.append(text)

            full_content = "\n\n".join(content_parts)

            # Compute content version hash
            content_version = hashlib.sha256(full_content.encode()).hexdigest()[:16]

            return {
                "content": full_content,
                "content_version": content_version,
                "chunk_count": len(sorted_chunks),
            }

        except Exception as e:
            # If Qdrant fails entirely, try filesystem fallback
            fs_result = await self._read_from_filesystem(chapter_slug)
            if fs_result:
                return fs_result
            raise RuntimeError(f"Chapter retrieval failed for {chapter_slug}: {str(e)}")

    async def _read_from_filesystem(
        self, chapter_slug: str
    ) -> Optional[Dict[str, Any]]:
        """
        Fallback: read chapter markdown directly from book/docs/ filesystem.

        Used when Qdrant collection is empty or unreachable.
        """
        slug = chapter_slug.strip("/")
        md_path = self._docs_dir / f"{slug}.md"

        if not md_path.exists():
            return None

        try:
            content = await asyncio.to_thread(md_path.read_text, "utf-8")

            # Strip YAML frontmatter if present
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    content = parts[2].strip()

            content_version = hashlib.sha256(content.encode()).hexdigest()[:16]

            return {
                "content": content,
                "content_version": content_version,
                "chunk_count": 1,
                "source": "filesystem",
            }
        except Exception:
            return None
