#!/usr/bin/env python3
"""
Internal Link Validation Script

Checks that internal links in markdown files point to existing files.

Usage: python scripts/check_links.py [path/to/docs]
"""
import sys
import re
from pathlib import Path
from typing import List, Tuple


def extract_internal_links(content: str) -> List[str]:
    """
    Extract internal markdown links.

    Matches: [text](./path.md) or [text](../path.md)
    Ignores: [text](https://...) or [text](#anchor)
    """
    # Pattern for markdown links
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(pattern, content)

    internal_links = []
    for text, url in matches:
        # Skip external URLs and anchors
        if url.startswith("http") or url.startswith("#"):
            continue
        internal_links.append(url)

    return internal_links


def validate_file(file_path: Path, docs_dir: Path) -> List[str]:
    """
    Validate internal links in a markdown file.

    Returns list of broken link errors (empty if valid).
    """
    errors = []

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"Failed to read file: {e}"]

    links = extract_internal_links(content)

    for link in links:
        # Remove anchor if present
        link_path = link.split("#")[0]

        # Resolve relative path
        target = (file_path.parent / link_path).resolve()

        if not target.exists():
            errors.append(f"Broken link: {link} (target not found: {target})")

    return errors


def main():
    """Main validation entry point."""
    docs_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("book/docs")

    if not docs_dir.exists():
        print(f"❌ Directory not found: {docs_dir}")
        sys.exit(1)

    # Find all markdown files
    md_files = list(docs_dir.rglob("*.md"))

    if not md_files:
        print(f"⚠️  No markdown files found in {docs_dir}")
        sys.exit(0)

    print(f"🔍 Checking links in {len(md_files)} markdown files...")

    all_errors = []
    for md_file in md_files:
        errors = validate_file(md_file, docs_dir)
        if errors:
            all_errors.append((md_file, errors))

    if all_errors:
        print(f"\n❌ Link validation failed: {len(all_errors)} files with broken links\n")
        for file_path, errors in all_errors:
            print(f"  {file_path.relative_to(docs_dir)}:")
            for error in errors:
                print(f"    - {error}")
        sys.exit(1)
    else:
        print(f"✅ All links validated successfully")
        sys.exit(0)


if __name__ == "__main__":
    main()
