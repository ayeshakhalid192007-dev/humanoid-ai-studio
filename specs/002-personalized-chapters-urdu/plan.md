# Implementation Plan: Dynamic Personalized Chapters + Urdu Translation

**Branch**: `002-personalized-chapters-urdu` | **Date**: 2026-02-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-personalized-chapters-urdu/spec.md`

## Summary

Add two AI-powered features to the Physical AI book platform: (1) a "Personalized Version" button on every chapter page that adapts explanations and examples based on the authenticated user's profile (software background, hardware background, robotics knowledge level) using the existing Qdrant RAG pipeline, and (2) a "Translate to Urdu" button available to all users that translates chapter content to Urdu while preserving Markdown formatting and leaving code blocks untouched. Both features cache results in Neon Postgres and replace content in-place with toggle behavior.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/React 18 (frontend, Docusaurus 3.6.3), Node.js 18+ (auth-server)
**Primary Dependencies**: FastAPI 0.100+, OpenAI SDK 1.0+, qdrant-client 1.7+, asyncpg 0.29+, Docusaurus 3.6.3, Better Auth
**Storage**: Neon Postgres (asyncpg, raw SQL), Qdrant Cloud (vector search)
**Testing**: pytest + pytest-asyncio (backend), manual E2E (frontend)
**Target Platform**: Web — Linux server (Railway/Cloud backend), GitHub Pages or similar (static frontend)
**Project Type**: Web application (backend + auth-server + book frontend)
**Performance Goals**: <15s AI generation, <2s cached retrieval, <1s content toggle, 20 concurrent AI requests
**Constraints**: OpenAI API rate limits, Qdrant Cloud query limits, session-based auth via Better Auth cookies
**Scale/Scope**: ~35 chapters, hundreds of users, personalization is per-user-per-chapter, translation is per-chapter

## Constitution Check

*GATE: Constitution is templated (not customized). Proceeding with standard best practices.*

- **Smallest viable diff**: Yes — new files only, no refactoring of existing code
- **No hardcoded secrets**: Yes — all API keys via `.env`
- **Clarify first**: Yes — `/sp.clarify` completed with 5 decisions resolved
- **Testable acceptance criteria**: Yes — spec has 10 measurable success criteria

## Project Structure

### Documentation (this feature)

```text
specs/002-personalized-chapters-urdu/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── api-contracts.md # Phase 1 output
└── tasks.md             # Phase 2 output (via /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   ├── personalize.py          # NEW — POST /api/personalize, GET /api/personalize/status
│   │   └── translate.py            # NEW — POST /api/translate, GET /api/translate/status
│   ├── services/
│   │   ├── content_personalizer.py # NEW — Personalization prompt + generation
│   │   ├── content_translator.py   # NEW — Urdu translation prompt + generation
│   │   └── chapter_retriever.py    # NEW — Full chapter retrieval from Qdrant
│   ├── db/
│   │   └── neon_client.py          # MODIFY — Add personalization/translation cache methods
│   └── config.py                   # MODIFY — Add rate limit config for AI endpoints
├── scripts/
│   └── setup_db_personalization.py # NEW — DB migration script
├── tests/
│   ├── test_personalize_api.py     # NEW
│   ├── test_translate_api.py       # NEW
│   └── test_chapter_retriever.py   # NEW
└── main.py                         # MODIFY — Register new routers

book/
├── src/
│   ├── components/
│   │   └── ChapterToolbar/
│   │       ├── index.tsx           # NEW — Personalize + Translate buttons
│   │       └── styles.module.css   # NEW — Button styles + RTL support
│   └── theme/
│       └── DocItem/
│           └── Content/
│               └── index.tsx       # NEW — Swizzled wrapper to inject ChapterToolbar
└── src/css/
    └── custom.css                  # MODIFY — Add RTL typography rules
```

**Structure Decision**: Follows the existing web application structure with `backend/`, `book/`, and `auth-server/` as separate projects. New backend files follow the existing module pattern (api/, services/, db/). New frontend components follow Docusaurus swizzle pattern already used for Navbar/Content.

## Architecture Decisions

### 1. Extend Existing RAG Pipeline (not new vector DB)

**Decision**: Reuse Qdrant Cloud + OpenAI pipeline already serving the chatbot.

**Rationale**: Infrastructure is already provisioned and curriculum content is already embedded. The `Retriever`, `Embedder`, and `Generator` classes provide the building blocks. Adding a separate vector DB would duplicate data and increase operational cost.

**Trade-offs**: Tied to Qdrant Cloud availability. If Qdrant goes down, both chatbot and personalization/translation are affected. Acceptable given single-provider simplicity.

### 2. Full Chapter Retrieval via Qdrant Metadata Filtering

**Decision**: Retrieve all chunks for a chapter by filtering on `module` + `lesson` metadata fields in Qdrant, then reconstruct the full chapter from ordered chunks.

**Rationale**: The `embed_curriculum.py` script already chunks and indexes all chapters with metadata. Filtering by module+lesson returns the complete chapter content without needing filesystem access from the backend.

**Trade-offs**: Content reconstruction depends on chunk ordering being preserved. The embedding script uses sequential chunking, so ordering is maintained by Qdrant point IDs.

### 3. Separate Prompt Templates for Personalization vs Translation

**Decision**: Two distinct system prompts — one for personalization (chapter content + user profile → adapted content) and one for translation (chapter content → Urdu).

**Rationale**: Different objectives require different instructions. Personalization must preserve structure while adapting depth; translation must preserve formatting while changing language. Separate prompts allow independent tuning.

### 4. Docusaurus DocItem/Content Swizzle

**Decision**: Swizzle the `DocItem/Content` theme component to inject the ChapterToolbar at the top of every doc page.

**Rationale**: This is the standard Docusaurus pattern for adding UI to doc pages without modifying individual Markdown files. The project already uses swizzling (Navbar/Content, Root). No per-file changes needed for 35+ chapters.

### 5. In-Place Content Replacement (no tabs or side-by-side)

**Decision**: Toggle between original/personalized/Urdu by replacing content in-place within the same container.

**Rationale**: Simplest UX approach. Avoids layout complexity of tabs or split views. Users toggle via clear button labels ("Revert to Original", "View Original (English)").

### 6. Cache in Neon Postgres (not Redis)

**Decision**: Store cached personalized content and Urdu translations in Neon Postgres tables using asyncpg.

**Rationale**: The project already uses Neon Postgres for session and conversation data. Adding Redis would introduce a new dependency and operational complexity. Content is text (not high-frequency key-value access), so Postgres is sufficient. Cache access patterns are simple (lookup by user+chapter or chapter).

## Component Interaction Flow

### Personalization Flow

```
User clicks "Personalized Version"
    │
    ├── Unauthenticated? → Show AuthModal → Login → Continue
    │
    ▼
Frontend sends POST /api/personalize { chapter_slug }
    │
    ▼
Backend validates session (Better Auth cookie)
    │
    ├── Check cache (personalized_content table)
    │   ├── Cache hit + version matches → Return cached content
    │   └── Cache miss or stale →
    │       │
    │       ├── Fetch user profile (auth-server /api/profile)
    │       ├── Retrieve all chapter chunks (Qdrant, module+lesson filter)
    │       ├── Reconstruct chapter content from chunks
    │       ├── Generate personalized content (OpenAI gpt-4o-mini)
    │       ├── Store in personalized_content table
    │       └── Return generated content
    │
    ▼
Frontend replaces doc content with personalized Markdown
    │
    ▼
Show "Revert to Original" + "Regenerate" buttons
```

### Translation Flow

```
User clicks "Translate to Urdu"
    │
    ▼
Frontend sends POST /api/translate { chapter_slug }
    │
    ▼
Backend (no auth required)
    │
    ├── Check cache (urdu_translations table)
    │   ├── Cache hit + version matches → Return cached content
    │   └── Cache miss or stale →
    │       │
    │       ├── Retrieve all chapter chunks (Qdrant, module+lesson filter)
    │       ├── Reconstruct chapter content from chunks
    │       ├── Generate Urdu translation (OpenAI gpt-4o-mini)
    │       ├── Store in urdu_translations table
    │       └── Return generated content
    │
    ▼
Frontend replaces doc content with Urdu Markdown
    │
    ├── Set dir="rtl" and lang="ur" on content container
    │
    ▼
Show "View Original (English)" button
```

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| AI output quality varies | Medium | Structured prompt templates with explicit constraints; preserve heading structure |
| Large chapters exceed token limits | Medium | Chunk-by-chunk processing; split into sections if needed |
| Qdrant Cloud downtime | High | Graceful error handling with user-friendly message; retry logic |
| OpenAI API rate limits | Medium | Backend rate limiting (10 personalizations/hr, 20 translations/hr); caching |

## Complexity Tracking

No constitution violations. All components follow existing patterns.

## Follow-ups and Risks

- **Post-launch monitoring**: Track AI generation latency and error rates via existing logger
- **Content quality review**: Sample personalized outputs for accuracy before full rollout
- **Future extensibility**: Additional languages beyond Urdu can reuse the translation pipeline with minimal changes
