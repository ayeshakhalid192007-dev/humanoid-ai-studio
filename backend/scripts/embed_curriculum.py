#!/usr/bin/env python3
"""
Curriculum Embedding Script

Parses markdown files from book/docs/, extracts content chunks,
generates embeddings, and uploads to Qdrant vector database.

Usage: python backend/scripts/embed_curriculum.py [--dry-run]
"""
import asyncio
import sys
import re
import os
from pathlib import Path
from typing import List, Dict, Any
import uuid

# Fix Windows console encoding for emoji output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Project root (physical_ai/)
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Load backend/.env FIRST (override root .env mock keys)
from dotenv import load_dotenv
_backend_env = Path(__file__).parent.parent / ".env"
if _backend_env.exists():
    load_dotenv(_backend_env, override=True)

from src.services.embedder import Embedder
from src.db.qdrant_client import QdrantClient as CustomQdrantClient
from qdrant_client.models import PointStruct


def _is_inside_code_fence(lines: List[str], index: int) -> bool:
    """
    Returns True if line at `index` is inside a fenced code block.
    Scans from the start tracking triple-backtick toggles.
    """
    in_fence = False
    for i in range(index):
        if lines[i].strip().startswith("```"):
            in_fence = not in_fence
    return in_fence


def _detect_file_type(file_path: Path) -> str:
    """
    Returns file type based on filename patterns.
    One of: 'lesson', 'intro', 'exercise', 'capstone', 'reference'.
    """
    name = file_path.name.lower()
    parts_lower = [p.lower() for p in file_path.parts]

    if "exercises.md" in name or "exercise" in name:
        return "exercise"
    if "capstone" in parts_lower:
        return "capstone"
    if name == "intro.md" or name == "introduction.md":
        return "intro"
    if "reference" in name or "appendix" in name:
        return "reference"
    return "lesson"


def _split_large_chunk(text: str, max_words: int = 400) -> List[str]:
    """
    Recursively splits text exceeding max_words at paragraph then sentence boundaries.
    Never splits inside a fenced code block or a markdown table.
    Returns list of sub-chunk strings.
    """
    if len(text.split()) <= max_words:
        return [text]

    # Strategy 1: Split at paragraph boundaries (\n\n)
    paragraphs = re.split(r'\n\n+', text)
    if len(paragraphs) > 1:
        # Group paragraphs into chunks respecting code fences and tables
        groups = []
        current_group = []
        in_fence = False
        in_table = False

        for para in paragraphs:
            stripped = para.strip()
            # Track code fences
            fence_count = stripped.count("```")
            if fence_count % 2 == 1:
                in_fence = not in_fence

            # Track tables (lines starting with |)
            para_lines = stripped.split("\n")
            if any(l.strip().startswith("|") for l in para_lines):
                in_table = True
            else:
                in_table = False

            current_group.append(para)

            # Only split when outside fences and tables
            if not in_fence and not in_table:
                group_text = "\n\n".join(current_group)
                if len(group_text.split()) >= max_words and len(current_group) > 1:
                    # Push all but the last paragraph as a group
                    groups.append("\n\n".join(current_group[:-1]))
                    current_group = [current_group[-1]]

        if current_group:
            groups.append("\n\n".join(current_group))

        if len(groups) > 1:
            result = []
            for g in groups:
                result.extend(_split_large_chunk(g, max_words))
            return result

    # Strategy 2: Split at sentence boundaries
    # Match '. ' followed by uppercase letter, '? ', or '! '
    sentence_breaks = list(re.finditer(r'(?<=[.!?])\s+(?=[A-Z])', text))
    if sentence_breaks:
        # Find the split point closest to the middle
        mid = len(text) // 2
        best_break = min(sentence_breaks, key=lambda m: abs(m.start() - mid))
        part1 = text[:best_break.start()].strip()
        part2 = text[best_break.end():].strip()

        if part1 and part2:
            result = []
            result.extend(_split_large_chunk(part1, max_words))
            result.extend(_split_large_chunk(part2, max_words))
            return result

    # Cannot split further, return as-is
    return [text]


def _extract_last_sentences(text: str, count: int = 2) -> str:
    """Extract the last `count` sentences from text for overlap context."""
    # Split on sentence boundaries
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    # Filter out very short fragments and code-like lines
    prose_sentences = [s for s in sentences if len(s) > 20 and not s.strip().startswith("```")]
    if not prose_sentences:
        return ""
    selected = prose_sentences[-count:]
    return " ".join(selected)


def parse_markdown(file_path: Path, base_url: str) -> List[Dict[str, Any]]:
    """
    Parse markdown file into metadata-rich chunks at heading boundaries.

    Features:
    - Code-fence aware heading detection
    - Code-prose separation for large code blocks
    - Recursive splitting of large chunks (>400 words)
    - Chunk overlap for prose continuity
    - Enriched metadata (content_type, code_language, heading_level, etc.)

    Args:
        file_path: Path to markdown file
        base_url: Base URL for the book (e.g., https://yourdomain.github.io)

    Returns:
        List of chunks with metadata
    """
    content = file_path.read_text(encoding="utf-8")

    # Extract frontmatter
    frontmatter = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            import yaml
            try:
                frontmatter = yaml.safe_load(parts[1])
                content = parts[2]
            except Exception:
                pass

    # Determine module and lesson from path
    path_parts = file_path.parts
    module = ""
    lesson = ""

    for i, part in enumerate(path_parts):
        if part.startswith("module"):
            module = part.replace("module", "")
            if i + 1 < len(path_parts):
                lesson = path_parts[i + 1].replace(".md", "")
            break
        elif part in ("capstone", "lab-architecture"):
            module = part
            if i + 1 < len(path_parts):
                lesson = path_parts[i + 1].replace(".md", "")
            break

    # Root-level intro.md gets overview metadata
    if not module and file_path.name.lower() in ("intro.md", "introduction.md"):
        module = "overview"
        lesson = "intro"

    file_type = _detect_file_type(file_path)

    # Split into chunks at heading boundaries (## and ###) -- CODE-FENCE AWARE
    heading_pattern = r'^(#{2,3})\s+(.+)$'
    lines = content.split("\n")

    raw_chunks = []
    current_chunk_lines = []
    current_heading = frontmatter.get("title", "Introduction")
    current_heading_level = 2
    parent_heading = ""
    in_code_fence = False

    for line in lines:
        # Track code fence state
        if line.strip().startswith("```"):
            in_code_fence = not in_code_fence

        match = re.match(heading_pattern, line)
        if match and not in_code_fence:
            # Save previous chunk if it has content
            if current_chunk_lines:
                chunk_text = "\n".join(current_chunk_lines).strip()
                if len(chunk_text) > 50:
                    raw_chunks.append({
                        "text": chunk_text,
                        "section_title": current_heading,
                        "heading_level": current_heading_level,
                        "parent_heading": parent_heading,
                    })

            # Update heading tracking
            level = len(match.group(1))
            heading_text = match.group(2)

            if level == 2:
                parent_heading = heading_text
            current_heading = heading_text
            current_heading_level = level
            current_chunk_lines = [line]
        else:
            current_chunk_lines.append(line)

    # Add final chunk
    if current_chunk_lines:
        chunk_text = "\n".join(current_chunk_lines).strip()
        if len(chunk_text) > 50:
            raw_chunks.append({
                "text": chunk_text,
                "section_title": current_heading,
                "heading_level": current_heading_level,
                "parent_heading": parent_heading,
            })

    # --- CODE-PROSE SEPARATION ---
    separated_chunks = []
    for raw_chunk in raw_chunks:
        text = raw_chunk["text"]
        # Find fenced code blocks
        code_block_pattern = re.compile(r'(```(\w*)\n(.*?)```)', re.DOTALL)
        code_blocks = list(code_block_pattern.finditer(text))

        # Separate large code blocks (>10 lines)
        large_code_blocks = [
            cb for cb in code_blocks
            if cb.group(3).strip().count("\n") >= 10
        ]

        if large_code_blocks:
            # Build heading context: parent heading + first prose sentence
            heading_ctx = raw_chunk["section_title"]
            if raw_chunk["parent_heading"] and raw_chunk["parent_heading"] != raw_chunk["section_title"]:
                heading_ctx = f"{raw_chunk['parent_heading']} > {raw_chunk['section_title']}"

            # Extract first prose sentence for code block context
            first_sentence = ""
            prose_start = text[:large_code_blocks[0].start()].strip()
            sentence_match = re.match(r'.*?[.!?]', prose_start.replace("\n", " "))
            if sentence_match:
                first_sentence = sentence_match.group(0).strip()

            # Remove large code blocks from text to get prose remainder
            prose_text = text
            for cb in reversed(large_code_blocks):
                prose_text = prose_text[:cb.start()] + prose_text[cb.end():]
            prose_text = prose_text.strip()

            # Add prose chunk if substantial
            if len(prose_text.split()) > 20:
                separated_chunks.append({
                    **raw_chunk,
                    "text": prose_text,
                    "content_type": "prose",
                    "code_language": None,
                })

            # Add each large code block as its own chunk
            for cb in large_code_blocks:
                lang = cb.group(2) or None
                code_text = cb.group(1)  # includes the fences
                context_prefix = f"[{heading_ctx}]"
                if first_sentence:
                    context_prefix += f" {first_sentence}"
                separated_chunks.append({
                    **raw_chunk,
                    "text": f"{context_prefix}\n\n{code_text}",
                    "section_title": f"{raw_chunk['section_title']} (code)",
                    "content_type": "code",
                    "code_language": lang,
                })
        else:
            # Determine content_type
            ct = "prose"
            if file_type == "exercise":
                ct = "exercise"
            separated_chunks.append({
                **raw_chunk,
                "content_type": ct,
                "code_language": None,
            })

    # --- RECURSIVE SIZE SPLITTING ---
    split_chunks = []
    for chunk in separated_chunks:
        if len(chunk["text"].split()) > 400 and chunk["content_type"] != "code":
            sub_texts = _split_large_chunk(chunk["text"], max_words=400)
            for idx, sub_text in enumerate(sub_texts, 1):
                if len(sub_text.strip()) > 50:
                    split_chunks.append({
                        **chunk,
                        "text": sub_text,
                        "section_title": f"{chunk['section_title']} (part {idx})" if len(sub_texts) > 1 else chunk["section_title"],
                    })
        else:
            split_chunks.append(chunk)

    # --- CHUNK OVERLAP (prose only) ---
    for i in range(1, len(split_chunks)):
        prev = split_chunks[i - 1]
        curr = split_chunks[i]
        if curr["content_type"] == "prose" and prev["content_type"] == "prose":
            # Strip any existing context prefix before extracting overlap
            prev_text = re.sub(r'^\[Context:.*?\]\s*', '', prev["text"], count=1, flags=re.DOTALL)
            overlap = _extract_last_sentences(prev_text, count=2)
            if overlap:
                curr["text"] = f"[Context: {overlap}]\n\n{curr['text']}"

    # --- ENRICH METADATA ---
    relative_path = str(file_path.relative_to(file_path.parents[2])).replace("\\", "/")
    for chunk in split_chunks:
        # URL with section anchor
        section_anchor = chunk["section_title"].lower().replace(" ", "-")
        # Clean anchor of special chars
        section_anchor = re.sub(r'[^a-z0-9\-]', '', section_anchor)
        chunk["url"] = f"{base_url}/{relative_path.replace('.md', '')}#{section_anchor}"

        # Add remaining metadata
        chunk["module"] = module
        chunk["lesson"] = lesson
        chunk["file_type"] = file_type
        chunk["word_count"] = len(chunk["text"].split())

        # Ensure defaults
        chunk.setdefault("content_type", "prose")
        chunk.setdefault("code_language", None)
        chunk.setdefault("heading_level", 2)
        chunk.setdefault("parent_heading", "")

    return split_chunks


def dry_run(docs_dir: Path, base_url: str):
    """
    Dry run: validate parsing without API calls.

    Args:
        docs_dir: Path to docs directory
        base_url: Base URL for the book
    """
    print("🔍 DRY RUN: Validating markdown parsing (no API calls)\n")

    # Find all markdown files
    md_files = list(docs_dir.rglob("*.md"))
    print(f"📄 Found {len(md_files)} markdown files\n")

    # Parse and collect stats by module
    module_stats = {}
    all_chunks = []

    for md_file in md_files:
        chunks = parse_markdown(md_file, base_url)
        all_chunks.extend(chunks)

        # Determine module from chunk metadata
        module = "other"
        if chunks and chunks[0].get("module"):
            module = chunks[0]["module"]
        else:
            for part in md_file.parts:
                if part.startswith("module") or part in ("capstone", "lab-architecture"):
                    module = part
                    break

        if module not in module_stats:
            module_stats[module] = {"files": 0, "chunks": 0, "words": 0}

        module_stats[module]["files"] += 1
        module_stats[module]["chunks"] += len(chunks)
        module_stats[module]["words"] += sum(c.get("word_count", len(c["text"].split())) for c in chunks)

        print(f"  ✓ {md_file.relative_to(docs_dir)}: {len(chunks)} chunks")

    # Summary by module
    print("\n" + "=" * 60)
    print("📊 SUMMARY BY MODULE")
    print("=" * 60)
    print(f"{'Module':<15} {'Files':>8} {'Chunks':>10} {'Words':>12}")
    print("-" * 60)

    total_files = 0
    total_chunks = 0
    total_words = 0

    for module in sorted(module_stats.keys()):
        stats = module_stats[module]
        print(f"{module:<15} {stats['files']:>8} {stats['chunks']:>10} {stats['words']:>12}")
        total_files += stats["files"]
        total_chunks += stats["chunks"]
        total_words += stats["words"]

    print("-" * 60)
    print(f"{'TOTAL':<15} {total_files:>8} {total_chunks:>10} {total_words:>12}")

    # Word count distribution
    print("\n" + "=" * 60)
    print("📏 WORD COUNT DISTRIBUTION")
    print("=" * 60)

    word_counts = [c.get("word_count", len(c["text"].split())) for c in all_chunks]
    if word_counts:
        print(f"  Min:  {min(word_counts)} words")
        print(f"  Avg:  {sum(word_counts) // len(word_counts)} words")
        print(f"  Max:  {max(word_counts)} words")

    # Content type breakdown
    print("\n" + "=" * 60)
    print("📂 CONTENT TYPE BREAKDOWN")
    print("=" * 60)

    type_counts = {}
    for c in all_chunks:
        ct = c.get("content_type", "prose")
        type_counts[ct] = type_counts.get(ct, 0) + 1

    for ct in sorted(type_counts.keys()):
        print(f"  {ct}: {type_counts[ct]} chunks")

    # Code language breakdown (for code chunks)
    code_langs = {}
    for c in all_chunks:
        if c.get("content_type") == "code" and c.get("code_language"):
            lang = c["code_language"]
            code_langs[lang] = code_langs.get(lang, 0) + 1

    if code_langs:
        print("\n  Code languages:")
        for lang in sorted(code_langs.keys()):
            print(f"    {lang}: {code_langs[lang]} chunks")

    # Validation checks
    print("\n" + "=" * 60)
    print("✅ VALIDATION CHECKS")
    print("=" * 60)

    issues = []

    # Check 1: Empty chunks
    empty_chunks = [c for c in all_chunks if len(c["text"].strip()) < 50]
    if empty_chunks:
        issues.append(f"⚠️  {len(empty_chunks)} chunks with <50 chars (filtered out)")

    # Check 2: Very large chunks (>500 words after splitting)
    large_chunks = [c for c in all_chunks if c.get("word_count", len(c["text"].split())) > 500]
    if large_chunks:
        issues.append(f"⚠️  {len(large_chunks)} chunks exceed 500 words after splitting")
        for c in large_chunks[:5]:
            ct = c.get("content_type", "prose")
            issues.append(f"     - [{ct}] {c['module']}/{c['lesson']}: {c['section_title']} ({c.get('word_count', '?')} words)")

    # Check 3: Missing module metadata
    no_module = [c for c in all_chunks if not c.get("module")]
    if no_module:
        issues.append(f"⚠️  {len(no_module)} chunks missing module metadata")
        for c in no_module[:5]:
            issues.append(f"     - {c['section_title']}")

    # Check 4: URL validation
    bad_urls = [c for c in all_chunks if not c.get("url", "").startswith("http")]
    if bad_urls:
        issues.append(f"⚠️  {len(bad_urls)} chunks with invalid URLs")

    # Check 5: Missing file_type
    no_file_type = [c for c in all_chunks if not c.get("file_type")]
    if no_file_type:
        issues.append(f"⚠️  {len(no_file_type)} chunks missing file_type metadata")

    if issues:
        for issue in issues:
            print(issue)
    else:
        print("✅ All validation checks passed!")

    # Sample chunks
    print("\n" + "=" * 60)
    print("📝 SAMPLE CHUNKS (first 3)")
    print("=" * 60)

    for i, chunk in enumerate(all_chunks[:3], 1):
        print(f"\n--- Chunk {i} ---")
        print(f"Module: {chunk.get('module', '')}")
        print(f"Lesson: {chunk.get('lesson', '')}")
        print(f"Section: {chunk.get('section_title', '')}")
        print(f"Type: {chunk.get('content_type', 'prose')}")
        print(f"File Type: {chunk.get('file_type', '')}")
        print(f"Code Lang: {chunk.get('code_language', '')}")
        print(f"URL: {chunk.get('url', '')}")
        print(f"Words: {chunk.get('word_count', len(chunk['text'].split()))}")
        preview = chunk['text'][:200].replace('\n', ' ')
        print(f"Preview: {preview}...")

    print("\n" + "=" * 60)
    print(f"🎯 DRY RUN COMPLETE: {total_chunks} chunks ready for embedding")
    print("=" * 60)

    return all_chunks


async def main():
    """Main embedding pipeline."""
    # Check for dry-run flag
    dry_run_mode = "--dry-run" in sys.argv or "-d" in sys.argv

    # Configuration - use absolute path relative to project root
    docs_dir = PROJECT_ROOT / "book" / "docs"
    base_url = "https://yourdomain.github.io/physical_ai"  # TODO: Update with actual URL

    if not docs_dir.exists():
        print(f"[ERROR] Docs directory not found: {docs_dir}")
        print(f"  Project root: {PROJECT_ROOT}")
        print(f"  Expected: {docs_dir}")
        sys.exit(1)

    if dry_run_mode:
        dry_run(docs_dir, base_url)
        return

    print("🚀 Starting curriculum embedding pipeline...")

    # Find all markdown files
    md_files = list(docs_dir.rglob("*.md"))
    print(f"📄 Found {len(md_files)} markdown files")

    # Parse all files into chunks
    all_chunks = []
    for md_file in md_files:
        chunks = parse_markdown(md_file, base_url)
        all_chunks.extend(chunks)
        print(f"  ✓ {md_file.name}: {len(chunks)} chunks")

    print(f"\n📦 Total chunks: {len(all_chunks)}")

    # Generate embeddings
    print("\n🧠 Generating embeddings...")
    embedder = Embedder()
    embedded_chunks = await embedder.embed_curriculum_chunks(all_chunks)
    print(f"✅ Generated {len(embedded_chunks)} embeddings")

    # Upload to Qdrant in batches to avoid timeout
    print("\n☁️  Uploading to Qdrant (batch size: 50)...")
    qdrant_client = CustomQdrantClient()

    points = []
    for chunk in embedded_chunks:
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=chunk["embedding"],
            payload={
                "text": chunk["text"],
                "module": chunk["module"],
                "lesson": chunk["lesson"],
                "section_title": chunk["section_title"],
                "url": chunk["url"],
                "content_type": chunk.get("content_type", "prose"),
                "code_language": chunk.get("code_language"),
                "heading_level": chunk.get("heading_level", 2),
                "parent_heading": chunk.get("parent_heading", ""),
                "word_count": chunk.get("word_count", 0),
                "file_type": chunk.get("file_type", "lesson"),
                "content_version": "2.0.0"
            }
        )
        points.append(point)

    batch_size = 50
    total_uploaded = 0
    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]
        qdrant_client.client.upsert(
            collection_name="curriculum",
            points=batch
        )
        total_uploaded += len(batch)
        print(f"  ↑ Uploaded batch {i // batch_size + 1}: {total_uploaded}/{len(points)} points")

    print(f"✅ Uploaded {total_uploaded} points to Qdrant")

    # Verify retrieval
    print("\n🧪 Testing retrieval...")
    test_query = "What are URDF joint limits?"
    test_embedding = await embedder.embed_text(test_query)

    from src.services.retriever import Retriever
    retriever = Retriever()
    results = await retriever.search(test_embedding, limit=3)

    print(f"  Query: '{test_query}'")
    print(f"  Results: {len(results)} chunks retrieved")
    for i, result in enumerate(results, 1):
        print(f"    {i}. {result['section_title']} (score: {result['score']:.3f})")

    print("\n✅ Curriculum embedding complete!")


if __name__ == "__main__":
    asyncio.run(main())
