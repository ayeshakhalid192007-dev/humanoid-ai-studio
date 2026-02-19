# Research: Dynamic Personalized Chapters + Urdu Translation

**Feature Branch**: `002-personalized-chapters-urdu`
**Date**: 2026-02-16

## Research Areas

### 1. RAG Pipeline Extension for Personalization & Translation

**Decision**: Extend the existing Qdrant-based RAG pipeline (already serving the chatbot) to also power personalization and translation.

**Rationale**: The codebase already has a fully operational RAG stack:
- `Embedder` (OpenAI `text-embedding-3-small`, 1536 dims)
- `Retriever` (Qdrant Cloud with cosine similarity, threshold 0.7)
- `Generator` (OpenAI `gpt-4o-mini`, async)
- `RAGPipeline` orchestrator with input sanitization

Reusing this stack avoids duplicating infrastructure. The existing `embed_curriculum.py` script already indexes `book/docs/**/*.md` into Qdrant with metadata (module, lesson, section_title, url, content_version). Chapter content is already chunked and indexed.

**Alternatives considered**:
- **pgvector on Neon Postgres**: Would consolidate to one DB but adds vector extension dependency and lacks Qdrant's mature search features (filtering, payload indexing). Rejected.
- **New standalone vector DB**: Unnecessary given Qdrant Cloud is already provisioned and populated.

### 2. Chapter Content Retrieval Strategy

**Decision**: For personalization/translation, retrieve ALL chunks for a specific chapter (filter by module + lesson metadata in Qdrant) rather than semantic search with a query.

**Rationale**: Unlike the chatbot which answers questions (needs semantic search), personalization and translation operate on the full chapter content. The Qdrant retriever already supports `module_filter` and `lesson_filter` parameters. We retrieve all chunks for a chapter, reconstruct the original ordering, and pass the full content to the generator.

**Alternatives considered**:
- **Fetch raw markdown from filesystem**: Backend doesn't serve static files from `book/docs/`; would need a new file-serving mechanism. Rejected for now — using the already-indexed vectors is cleaner.
- **Scrape from Docusaurus build output**: Fragile, depends on build artifacts. Rejected.

### 3. Chapter Identification

**Decision**: Use the Docusaurus doc slug (URL path segment, e.g., `module1/lesson1-ros2-basics`) as the canonical chapter identifier. This maps directly to the `module` and `lesson` metadata in Qdrant payloads and the `url` field.

**Rationale**: The frontend already knows the current page URL. The Qdrant chunks have `module` and `lesson` payload fields that map to the doc path. No new identifier system needed.

### 4. Content Version Tracking for Cache Invalidation

**Decision**: Use a content hash (MD5/SHA256 of the chapter's raw markdown) stored alongside cached content. The `embed_curriculum.py` script already attaches a `content_version` field to each Qdrant point. Compare at generation time.

**Rationale**: When the book is re-embedded after content changes, the `content_version` changes. Before serving cached content, compare the stored version hash against the current Qdrant content version for that chapter.

### 5. Database Schema for Caching

**Decision**: Add two new Neon Postgres tables: `personalized_content` and `urdu_translations`. Use raw SQL via `asyncpg` (matching existing `setup_db.py` pattern). No ORM.

**Rationale**: The project uses `asyncpg` with raw SQL everywhere (NeonClient, setup_db.py). Adding Drizzle or another ORM for just two tables would break consistency. The tables are simple key-value caches with metadata.

### 6. AI Prompt Engineering

**Decision**: Create two specialized prompt templates:
- **Personalization prompt**: Takes chapter content + user profile (software background, hardware background, robotics knowledge level). Instructs the model to adapt explanations and examples while preserving headings, sections, and ordering.
- **Translation prompt**: Takes chapter content. Instructs the model to translate to Urdu preserving Markdown formatting, leaving code blocks untouched, keeping technical terms in English, and outputting RTL-compatible Markdown.

**Rationale**: Separate prompts allow independent optimization. The existing `Generator` class uses a system prompt pattern that can be extended with new prompt templates.

### 7. Frontend: Docusaurus Doc Page Integration

**Decision**: Create a Docusaurus theme component wrapper (`DocItem/Content` swizzle) that injects the personalization and translation buttons at the top of every doc page. Use React context for state management.

**Rationale**: Docusaurus supports [swizzling](https://docusaurus.io/docs/swizzling) theme components. The project already swizzles `Navbar/Content` and `Root`. Wrapping `DocItem/Content` is the standard pattern for adding UI to doc pages without modifying individual Markdown files.

**Alternatives considered**:
- **MDX component in every doc file**: Would require editing 35+ Markdown files. Rejected.
- **Remark/Rehype plugin**: More complex, harder to maintain. Rejected.
- **Custom Docusaurus plugin**: Overkill for adding buttons. Rejected.

### 8. Urdu RTL Support

**Decision**: When Urdu content is displayed, wrap the content area with `dir="rtl"` and `lang="ur"` attributes. Add CSS rules for RTL-specific typography (font family, line height, text alignment).

**Rationale**: Modern browsers handle RTL layout well with the `dir` attribute. Docusaurus uses CSS modules, so scoped RTL styles won't leak to other components.

### 9. Rate Limiting for AI Endpoints

**Decision**: Reuse the existing `rate_limit.py` pattern with separate rate limit records for personalization and translation. Personalization: 10 requests/hour/user. Translation: 20 requests/hour/session.

**Rationale**: The existing sliding-window rate limiter in `rate_limit_records` table can be extended with a `request_type` column or separate tracking. Lower personalization limits due to higher API cost (larger prompts with user context).

### 10. Authentication Flow for Personalization Button

**Decision**: The "Personalized Version" button is always visible. When clicked by an unauthenticated user, the existing `AuthModal` component is shown. On successful login, personalization triggers automatically. The `AuthContext` already provides `isAuthenticated`, `user`, and `profile` state.

**Rationale**: The `AuthModal` component already exists with login/signup views. The `AuthContext` already manages session state with `refreshSession`. The `UserProfile` interface already has `softwareBackground`, `hardwareBackground`, and `roboticsKnowledge` fields.
