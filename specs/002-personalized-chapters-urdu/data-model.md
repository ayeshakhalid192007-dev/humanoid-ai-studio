# Data Model: Dynamic Personalized Chapters + Urdu Translation

**Feature Branch**: `002-personalized-chapters-urdu`
**Date**: 2026-02-16

## New Tables (Neon Postgres)

### personalized_content

Stores cached personalized chapter content per user per chapter.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing ID |
| user_id | TEXT | NOT NULL | Better Auth user ID (references `user.id`) |
| chapter_slug | TEXT | NOT NULL | Docusaurus doc slug (e.g., `module1/lesson1-ros2-basics`) |
| personalized_markdown | TEXT | NOT NULL | AI-generated personalized Markdown content |
| user_profile_snapshot | JSONB | NOT NULL | Profile data used for generation (software_background, hardware_background, robotics_knowledge) |
| content_version | TEXT | NOT NULL | Hash of the source chapter content at generation time |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | Generation timestamp |

**Unique constraint**: `(user_id, chapter_slug)` — one personalized version per user per chapter.

**Indexes**:
- `idx_personalized_user_chapter` on `(user_id, chapter_slug)` — lookup by user + chapter
- `idx_personalized_chapter_version` on `(chapter_slug, content_version)` — cache invalidation queries

### urdu_translations

Stores cached Urdu translations per chapter (shared across all users).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing ID |
| chapter_slug | TEXT | NOT NULL UNIQUE | Docusaurus doc slug |
| urdu_markdown | TEXT | NOT NULL | AI-generated Urdu Markdown content |
| content_version | TEXT | NOT NULL | Hash of the source chapter content at generation time |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | Generation timestamp |

**Indexes**:
- `idx_urdu_chapter` on `(chapter_slug)` — lookup by chapter (covered by UNIQUE)
- `idx_urdu_chapter_version` on `(chapter_slug, content_version)` — cache invalidation

### ai_generation_rate_limits

Extends rate limiting for AI generation endpoints (separate from chat rate limits).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing ID |
| identifier | TEXT | NOT NULL | User ID (personalization) or session ID (translation) |
| request_type | TEXT | NOT NULL | `personalize` or `translate` |
| request_timestamp | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | When the request was made |

**Indexes**:
- `idx_ai_rate_identifier_type_time` on `(identifier, request_type, request_timestamp DESC)` — sliding window queries

## Existing Tables Referenced

### user (Better Auth managed)

| Column | Type | Notes |
|--------|------|-------|
| id | TEXT | Primary key, referenced by personalized_content.user_id |
| email | TEXT | |
| name | TEXT | |
| onboardingCompleted | BOOLEAN | |

### user_profiles (custom, managed by auth-server)

| Column | Type | Notes |
|--------|------|-------|
| user_id | TEXT | FK to user.id |
| software_background | TEXT | Free text, max 2000 chars |
| hardware_background | TEXT | Free text, max 2000 chars |
| robotics_knowledge | TEXT | Enum: none, beginner, intermediate, advanced |

## Qdrant Collection (Existing)

### curriculum collection

Already populated by `embed_curriculum.py`. Used for chapter content retrieval.

| Payload Field | Type | Notes |
|---------------|------|-------|
| text | string | Chunk text content |
| module | string | Module number (e.g., "1") |
| lesson | string | Lesson identifier (e.g., "lesson1-ros2-basics") |
| section_title | string | Section heading |
| url | string | Book page URL |
| content_version | string | Book version hash |
| content_type | string | prose, code, exercise |

**Retrieval pattern for personalization/translation**: Filter by `module` + `lesson` to get all chunks for a chapter, ordered by original position.

## Entity Relationships

```
User (Better Auth)
  |-- 1:1 -- UserProfile (auth-server)
  |-- 1:N -- PersonalizedContent (per chapter)

Chapter (identified by slug)
  |-- 1:N -- PersonalizedContent (per user)
  |-- 1:1 -- UrduTranslation
  |-- 1:N -- CurriculumChunk (Qdrant)
```

## State Transitions

### PersonalizedContent Lifecycle
1. **Not generated**: No row exists → user sees "Personalized Version" button
2. **Generating**: API call in progress → loading indicator shown
3. **Cached**: Row exists with current `content_version` → served instantly
4. **Stale**: Row exists but `content_version` doesn't match current Qdrant version → regeneration required
5. **Regenerating**: User clicked "Regenerate" → old content replaced

### UrduTranslation Lifecycle
1. **Not generated**: No row exists → first user request triggers generation
2. **Generating**: API call in progress → loading indicator shown
3. **Cached**: Row exists with current `content_version` → served to all users
4. **Stale**: `content_version` mismatch → regeneration on next request
