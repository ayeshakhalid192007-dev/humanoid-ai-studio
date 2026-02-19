"""
Shared request validators for API endpoints.

Author: Physical AI Platform Team
Date: 2026-02-16
"""
import re
from fastapi import HTTPException, status

SLUG_PATTERN = re.compile(r"^[a-zA-Z0-9\-/]+$")
MAX_SLUG_LENGTH = 100


def validate_slug(chapter_slug: str) -> str:
    """Validate and sanitize chapter_slug."""
    slug = chapter_slug.strip().strip("/")
    if not slug or len(slug) > MAX_SLUG_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid chapter_slug: must be 1-{MAX_SLUG_LENGTH} characters."
        )
    if not SLUG_PATTERN.match(slug):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid chapter_slug: only alphanumeric, hyphens, and slashes allowed."
        )
    return slug
