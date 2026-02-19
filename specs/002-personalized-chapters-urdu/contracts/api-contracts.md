# API Contracts: Dynamic Personalized Chapters + Urdu Translation

**Feature Branch**: `002-personalized-chapters-urdu`
**Date**: 2026-02-16

## Endpoints Overview

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /api/personalize | Required | Generate/retrieve personalized chapter |
| POST | /api/translate | Public | Generate/retrieve Urdu translation |
| GET | /api/personalize/status/{chapter_slug} | Required | Check if cached version exists |
| GET | /api/translate/status/{chapter_slug} | Public | Check if cached translation exists |

---

## POST /api/personalize

Generate or retrieve a personalized version of a chapter.

### Request

```json
{
  "chapter_slug": "module1/lesson1-ros2-basics",
  "regenerate": false
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| chapter_slug | string | Yes | Docusaurus doc slug identifying the chapter |
| regenerate | boolean | No (default: false) | Force regeneration even if cached |

### Authentication

Session cookie `physical-ai.session_token` must be present and valid.

### Response 200 (Success)

```json
{
  "content": "# ROS 2 Basics\n\nSince you have an advanced software background...",
  "cached": true,
  "generated_at": "2026-02-16T10:30:00Z",
  "content_version": "abc123",
  "profile_used": {
    "software_background": "Advanced Python developer",
    "hardware_background": "Beginner with Arduino",
    "robotics_knowledge": "intermediate"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| content | string | Personalized Markdown content |
| cached | boolean | Whether this was served from cache |
| generated_at | string (ISO 8601) | When the content was generated |
| content_version | string | Chapter content version hash |
| profile_used | object | User profile snapshot used for generation |

### Response 401 (Unauthorized)

```json
{
  "detail": "Authentication required for personalized content."
}
```

### Response 404 (Chapter Not Found)

```json
{
  "detail": "Chapter not found: module1/lesson99"
}
```

### Response 429 (Rate Limited)

```json
{
  "detail": "Rate limit exceeded: 10 personalizations per hour."
}
```
Headers: `Retry-After: 3600`

### Response 503 (AI Service Unavailable)

```json
{
  "detail": "Unable to generate personalized content. Please try again later."
}
```

---

## POST /api/translate

Generate or retrieve an Urdu translation of a chapter.

### Request

```json
{
  "chapter_slug": "module1/lesson1-ros2-basics"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| chapter_slug | string | Yes | Docusaurus doc slug |

### Authentication

None required. Public endpoint.

### Response 200 (Success)

```json
{
  "content": "# آر او ایس 2 بنیادی باتیں\n\n...",
  "cached": true,
  "generated_at": "2026-02-16T10:30:00Z",
  "content_version": "abc123"
}
```

| Field | Type | Description |
|-------|------|-------------|
| content | string | Urdu Markdown content (RTL) |
| cached | boolean | Whether served from cache |
| generated_at | string (ISO 8601) | Generation timestamp |
| content_version | string | Source chapter version hash |

### Response 404 (Chapter Not Found)

```json
{
  "detail": "Chapter not found: module1/lesson99"
}
```

### Response 429 (Rate Limited)

```json
{
  "detail": "Rate limit exceeded: 20 translations per hour."
}
```

### Response 503 (AI Service Unavailable)

```json
{
  "detail": "Unable to generate translation. Please try again later."
}
```

---

## GET /api/personalize/status/{chapter_slug}

Check if a cached personalized version exists for the current user.

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| chapter_slug | string | URL-encoded chapter slug |

### Authentication

Session cookie required.

### Response 200

```json
{
  "has_cached": true,
  "content_version": "abc123",
  "is_stale": false,
  "generated_at": "2026-02-16T10:30:00Z"
}
```

---

## GET /api/translate/status/{chapter_slug}

Check if a cached Urdu translation exists.

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| chapter_slug | string | URL-encoded chapter slug |

### Authentication

None required.

### Response 200

```json
{
  "has_cached": true,
  "content_version": "abc123",
  "is_stale": false,
  "generated_at": "2026-02-16T10:30:00Z"
}
```

---

## Internal: Backend → Auth Server

### GET /api/profile (existing)

Fetches user profile data. Called by the backend's personalization endpoint after session validation.

**Cookie**: `physical-ai.session_token`

**Response 200**:
```json
{
  "profile": {
    "software_background": "Python, JavaScript, 5 years",
    "hardware_background": "Arduino basics",
    "robotics_knowledge": "intermediate"
  }
}
```

---

## Internal: Backend → Qdrant

### Chapter Content Retrieval

Uses existing `QdrantClient.search()` with `module_filter` + `lesson_filter` to retrieve all chunks for a chapter. Returns chunks ordered by position for content reconstruction.

**Filter parameters**:
- `module_filter`: Module number (e.g., "1")
- `lesson_filter`: Lesson slug (e.g., "lesson1-ros2-basics")
- `limit`: Set high (50+) to get all chunks
- `score_threshold`: Set to 0.0 (retrieve all, not similarity-filtered)

---

## Error Taxonomy

| HTTP Status | Meaning | Retry Strategy |
|-------------|---------|----------------|
| 200 | Success | N/A |
| 400 | Invalid request (bad chapter_slug) | Fix input |
| 401 | Authentication required (personalize only) | Login first |
| 404 | Chapter not found in Qdrant | Verify chapter exists |
| 429 | Rate limit exceeded | Wait per Retry-After header |
| 500 | Internal server error | Retry with backoff |
| 503 | AI service unavailable | Retry after delay |
