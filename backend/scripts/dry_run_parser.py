#!/usr/bin/env python3
"""
Dry-run script for curriculum parsing validation.
No external dependencies required.

Usage: python backend/scripts/dry_run_parser.py
"""
import sys
import re
from pathlib import Path

# Fix Windows console encoding for Unicode output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def parse_markdown(file_path: Path, base_url: str):
    """Parse markdown file into chunks at heading boundaries."""
    content = file_path.read_text(encoding="utf-8")

    # Extract frontmatter
    frontmatter = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            # Simple YAML parsing for title
            for line in parts[1].strip().split("\n"):
                if line.startswith("title:"):
                    frontmatter["title"] = line.split(":", 1)[1].strip().strip('"\'')
            content = parts[2]

    # Determine module and lesson from path
    path_parts = file_path.parts
    module = ""
    lesson = ""

    for i, part in enumerate(path_parts):
        if part.startswith("module") or part == "capstone":
            module = part.replace("module", "") if part.startswith("module") else "capstone"
            if i + 1 < len(path_parts):
                lesson = path_parts[i + 1].replace(".md", "")
            break

    # Split into chunks at heading boundaries (## and ###)
    heading_pattern = r'^(#{2,3})\s+(.+)$'
    lines = content.split("\n")

    chunks = []
    current_chunk = []
    current_heading = frontmatter.get("title", "Introduction")

    for line in lines:
        match = re.match(heading_pattern, line)
        if match:
            if current_chunk:
                chunk_text = "\n".join(current_chunk).strip()
                if len(chunk_text) > 50:
                    chunks.append({
                        "text": chunk_text,
                        "section_title": current_heading,
                        "module": module,
                        "lesson": lesson
                    })
            current_heading = match.group(2)
            current_chunk = [line]
        else:
            current_chunk.append(line)

    # Add final chunk
    if current_chunk:
        chunk_text = "\n".join(current_chunk).strip()
        if len(chunk_text) > 50:
            chunks.append({
                "text": chunk_text,
                "section_title": current_heading,
                "module": module,
                "lesson": lesson
            })

    # Add URL to each chunk
    try:
        relative_path = str(file_path.relative_to(file_path.parents[2])).replace("\\", "/")
        for chunk in chunks:
            section_anchor = chunk["section_title"].lower().replace(" ", "-")
            section_anchor = re.sub(r'[^a-z0-9-]', '', section_anchor)
            chunk["url"] = f"{base_url}/{relative_path.replace('.md', '')}#{section_anchor}"
    except:
        for chunk in chunks:
            chunk["url"] = base_url

    return chunks


def main():
    print("=" * 70)
    print("  CURRICULUM PARSING DRY-RUN")
    print("=" * 70)

    docs_dir = Path("book/docs")
    base_url = "https://yourdomain.github.io/physical_ai"

    if not docs_dir.exists():
        print(f"ERROR: Docs directory not found: {docs_dir}")
        print("Make sure you're running from the project root directory.")
        return

    md_files = list(docs_dir.rglob("*.md"))
    print(f"\nFound {len(md_files)} markdown files\n")

    # Parse and collect stats
    module_stats = {}
    all_chunks = []

    for md_file in sorted(md_files):
        chunks = parse_markdown(md_file, base_url)
        all_chunks.extend(chunks)

        # Determine module
        module = "other"
        for part in md_file.parts:
            if part.startswith("module"):
                module = part
                break
            elif part == "capstone":
                module = "capstone"
                break

        if module not in module_stats:
            module_stats[module] = {"files": 0, "chunks": 0, "words": 0}

        module_stats[module]["files"] += 1
        module_stats[module]["chunks"] += len(chunks)
        module_stats[module]["words"] += sum(len(c["text"].split()) for c in chunks)

        rel_path = md_file.relative_to(docs_dir)
        print(f"  [OK] {rel_path}: {len(chunks)} chunks")

    # Summary
    print("\n" + "=" * 70)
    print("  SUMMARY BY MODULE")
    print("=" * 70)
    print(f"{'Module':<15} {'Files':>10} {'Chunks':>12} {'Words':>14}")
    print("-" * 70)

    total_files = 0
    total_chunks = 0
    total_words = 0

    for module in sorted(module_stats.keys()):
        stats = module_stats[module]
        print(f"{module:<15} {stats['files']:>10} {stats['chunks']:>12} {stats['words']:>14,}")
        total_files += stats["files"]
        total_chunks += stats["chunks"]
        total_words += stats["words"]

    print("-" * 70)
    print(f"{'TOTAL':<15} {total_files:>10} {total_chunks:>12} {total_words:>14,}")

    # Validation
    print("\n" + "=" * 70)
    print("  VALIDATION")
    print("=" * 70)

    issues = []

    # Large chunks check
    large_chunks = [c for c in all_chunks if len(c["text"].split()) > 1000]
    if large_chunks:
        issues.append(f"WARNING: {len(large_chunks)} chunks exceed 1000 words")
        for c in large_chunks[:3]:
            issues.append(f"  - Module {c['module']}, {c['lesson']}: {c['section_title']} ({len(c['text'].split())} words)")

    # Missing module check
    no_module = [c for c in all_chunks if not c["module"]]
    if no_module:
        issues.append(f"WARNING: {len(no_module)} chunks missing module metadata")

    if issues:
        for issue in issues:
            print(issue)
    else:
        print("[PASS] All validation checks passed!")

    # Sample output
    print("\n" + "=" * 70)
    print("  SAMPLE CHUNKS")
    print("=" * 70)

    for i, chunk in enumerate(all_chunks[:3], 1):
        print(f"\n--- Sample {i} ---")
        print(f"Module: {chunk['module']}")
        print(f"Lesson: {chunk['lesson']}")
        print(f"Section: {chunk['section_title']}")
        print(f"URL: {chunk['url']}")
        print(f"Words: {len(chunk['text'].split())}")
        preview = chunk['text'][:150].replace('\n', ' ').strip()
        print(f"Preview: {preview}...")

    print("\n" + "=" * 70)
    print(f"  RESULT: {total_chunks} chunks ready for embedding")
    print("=" * 70)


if __name__ == "__main__":
    main()
