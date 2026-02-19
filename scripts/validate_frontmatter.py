#!/usr/bin/env python3
"""
Markdown Frontmatter Validation Script

Validates YAML frontmatter in all markdown files to prevent build failures.

Usage: python scripts/validate_frontmatter.py [path/to/docs]
"""
import sys
import yaml
from pathlib import Path
from typing import List, Tuple


def extract_frontmatter(content: str) -> Tuple[str, str]:
    """Extract YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return "", content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return "", content

    return parts[1].strip(), parts[2].strip()


def validate_file(file_path: Path) -> List[str]:
    """
    Validate a single markdown file.

    Returns list of error messages (empty if valid).
    """
    errors = []

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"Failed to read file: {e}"]

    frontmatter, body = extract_frontmatter(content)

    if not frontmatter:
        errors.append("Missing frontmatter (should start with ---)")
        return errors

    # Parse YAML
    try:
        fm_data = yaml.safe_load(frontmatter)
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML syntax: {e}")
        return errors

    # Check required fields
    required_fields = ["title"]
    for field in required_fields:
        if field not in fm_data:
            errors.append(f"Missing required field: {field}")

    # Validate sidebar_position if present
    if "sidebar_position" in fm_data:
        try:
            int(fm_data["sidebar_position"])
        except (ValueError, TypeError):
            errors.append(f"sidebar_position must be an integer, got: {fm_data['sidebar_position']}")

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

    print(f"🔍 Validating {len(md_files)} markdown files...")

    all_errors = []
    for md_file in md_files:
        errors = validate_file(md_file)
        if errors:
            all_errors.append((md_file, errors))

    if all_errors:
        print(f"\n❌ Validation failed: {len(all_errors)} files with errors\n")
        for file_path, errors in all_errors:
            print(f"  {file_path.relative_to(docs_dir)}:")
            for error in errors:
                print(f"    - {error}")
        sys.exit(1)
    else:
        print(f"✅ All {len(md_files)} files validated successfully")
        sys.exit(0)


if __name__ == "__main__":
    main()
