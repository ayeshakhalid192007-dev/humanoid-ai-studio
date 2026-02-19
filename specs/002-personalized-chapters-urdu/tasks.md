# Tasks: Dynamic Personalized Chapters + Urdu Translation

**Input**: Design documents from `/specs/002-personalized-chapters-urdu/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested in the spec. Test tasks are omitted. Manual E2E testing via quickstart.md checklist.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`, `backend/scripts/`
- **Frontend (Book)**: `book/src/`
- **Auth Server**: `auth-server/src/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Database schema and shared backend services needed by all user stories

- [X] T001 Create database migration script with tables `personalized_content`, `urdu_translations`, and `ai_generation_rate_limits` per data-model.md in `backend/scripts/setup_db_personalization.py`
- [X] T002 Add AI generation rate limit config fields (`PERSONALIZE_RATE_LIMIT_MAX`, `TRANSLATE_RATE_LIMIT_MAX`, `AI_RATE_LIMIT_WINDOW_HOURS`) to Settings class in `backend/src/config.py`
- [X] T003 [P] Add cache CRUD methods to NeonClient: `get_personalized_content(user_id, chapter_slug)`, `upsert_personalized_content(...)`, `get_urdu_translation(chapter_slug)`, `upsert_urdu_translation(...)`, `check_ai_rate_limit(identifier, request_type, max_requests)`, `record_ai_request(identifier, request_type)` in `backend/src/db/neon_client.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core services that MUST be complete before ANY user story API endpoint can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Create ChapterRetriever service that retrieves all Qdrant chunks for a chapter by `module` + `lesson` filter, reconstructs full chapter Markdown from ordered chunks, and returns content with `content_version` hash in `backend/src/services/chapter_retriever.py`
- [X] T005 [P] Create ContentPersonalizer service with personalization system prompt template that takes chapter Markdown + user profile (software_background, hardware_background, robotics_knowledge), calls OpenAI gpt-4o-mini to adapt explanations and examples while preserving headings/sections/ordering, and returns personalized Markdown in `backend/src/services/content_personalizer.py`
- [X] T006 [P] Create ContentTranslator service with Urdu translation system prompt template that takes chapter Markdown, calls OpenAI gpt-4o-mini to translate to Urdu preserving Markdown formatting, leaving code blocks completely untouched, keeping technical terms in English, and outputting RTL-compatible Markdown in `backend/src/services/content_translator.py`

**Checkpoint**: Foundation ready — chapter retrieval and AI generation services available for all user stories

---

## Phase 3: User Story 1 — Authenticated User Generates Personalized Chapter (Priority: P1) MVP

**Goal**: A logged-in user clicks "Personalized Version" on any chapter page. The system fetches their profile, generates personalized content via RAG + AI, caches it, and displays it in-place with a "Revert to Original" option.

**Independent Test**: Sign up with profile (software: advanced, hardware: beginner, robotics: intermediate), navigate to Module 1 Lesson 1, click "Personalized Version", verify content adapts terminology and depth. Revisit — cached version loads instantly. Click "Revert to Original" — original content restored.

### Implementation for User Story 1

- [X] T007 [US1] Create personalization API router with `POST /api/personalize` endpoint: validate session via Better Auth cookie, extract `chapter_slug` and `regenerate` from request body, check rate limit, check cache in `personalized_content` table (and content_version freshness), if miss then fetch user profile from auth-server `/api/profile`, retrieve chapter via ChapterRetriever, generate via ContentPersonalizer, upsert cache, return response per api-contracts.md in `backend/src/api/personalize.py`
- [X] T008 [US1] Add `GET /api/personalize/status/{chapter_slug}` endpoint to the personalize router: validate session, check if cached personalized content exists for this user+chapter, return `has_cached`, `is_stale`, `generated_at` in `backend/src/api/personalize.py`
- [X] T009 [US1] Register personalize router in FastAPI app with `app.include_router(personalize.router, tags=["personalization"])` in `backend/main.py`
- [X] T010 [US1] Create ChapterToolbar React component with "Personalized Version" button that: checks auth state from AuthContext, if authenticated calls `POST /api/personalize` with `chapter_slug` derived from current page URL, shows loading spinner during generation, on success replaces doc content in-place with personalized Markdown (rendered via `dangerouslySetInnerHTML` or a Markdown renderer), shows "Revert to Original" and "Regenerate" buttons when personalized content is active in `book/src/components/ChapterToolbar/index.tsx`
- [X] T011 [US1] Create ChapterToolbar styles with button layout (horizontal bar at top of chapter content), loading spinner animation, and active/inactive state styling in `book/src/components/ChapterToolbar/styles.module.css`
- [X] T012 [US1] Swizzle Docusaurus DocItem/Content theme component: wrap the original Content component, inject ChapterToolbar above the doc content, pass `chapter_slug` (derived from `useDoc()` hook or route metadata) as prop in `book/src/theme/DocItem/Content/index.tsx`

**Checkpoint**: Authenticated personalization is fully functional end-to-end. User can generate, view, revert, and regenerate personalized content.

---

## Phase 4: User Story 2 — Unauthenticated User Translates Chapter to Urdu (Priority: P2)

**Goal**: Any visitor (authenticated or not) clicks "Translate to Urdu" on a chapter page. The system translates the content to Urdu, preserves formatting and code blocks, applies RTL layout, and caches the result for all users.

**Independent Test**: Visit any chapter as an anonymous user, click "Translate to Urdu", verify headings/body in Urdu with RTL direction, code blocks unchanged. Click "View Original (English)" — English restored. Another user visits same chapter — cached translation loads instantly.

### Implementation for User Story 2

- [X] T013 [US2] Create translation API router with `POST /api/translate` endpoint: no auth required, extract `chapter_slug` from request body, check rate limit (by session or IP), check cache in `urdu_translations` table (and content_version freshness), if miss then retrieve chapter via ChapterRetriever, generate via ContentTranslator, upsert cache, return response per api-contracts.md in `backend/src/api/translate.py`
- [X] T014 [US2] Add `GET /api/translate/status/{chapter_slug}` endpoint to the translate router: check if cached Urdu translation exists, return `has_cached`, `is_stale`, `generated_at` in `backend/src/api/translate.py`
- [X] T015 [US2] Register translate router in FastAPI app with `app.include_router(translate.router, tags=["translation"])` in `backend/main.py`
- [X] T016 [US2] Add "Translate to Urdu" button to ChapterToolbar: calls `POST /api/translate` with `chapter_slug`, shows loading spinner, on success replaces content with Urdu Markdown and sets `dir="rtl"` and `lang="ur"` on content container, shows "View Original (English)" button to toggle back in `book/src/components/ChapterToolbar/index.tsx`
- [X] T017 [US2] Add RTL typography CSS rules: Urdu font family stack (Noto Nastaliq Urdu, Jameel Noori Nastaleeq, serif fallback), appropriate line-height for Nastaliq script (1.8+), text-align right, and scoped `.rtlContent` class that applies `direction: rtl` in `book/src/css/custom.css`
- [X] T018 [US2] Update ChapterToolbar styles to handle RTL layout: button positions, content container RTL class toggle, smooth transition between LTR and RTL content in `book/src/components/ChapterToolbar/styles.module.css`

**Checkpoint**: Urdu translation is fully functional. Any visitor can translate, toggle back, and cached translations are shared.

---

## Phase 5: User Story 3 — Unauthenticated User Attempts Personalization (Priority: P3)

**Goal**: An unauthenticated user clicks "Personalized Version" and sees an AuthModal prompting login. After successful login, personalization triggers automatically.

**Independent Test**: Visit a chapter as anonymous user, click "Personalized Version", verify AuthModal appears with "Login to unlock personalized content" message and sign-in/sign-up options. Login, verify personalization starts automatically.

### Implementation for User Story 3

- [X] T019 [US3] Update ChapterToolbar to handle unauthenticated personalization click: when `isAuthenticated` is false and user clicks "Personalized Version", open AuthModal (existing component from `book/src/components/Auth/AuthModal.tsx`) with message "Login to unlock personalized content", on successful login callback trigger personalization automatically in `book/src/components/ChapterToolbar/index.tsx`
- [X] T020 [US3] Add `onSuccess` callback integration: after AuthModal login success, call `refreshSession()` from AuthContext, then `fetchProfile()`, then automatically invoke the personalization API call without requiring a second button click in `book/src/components/ChapterToolbar/index.tsx`

**Checkpoint**: Unauthenticated personalization flow complete. Login modal gates access, post-login triggers auto-personalization.

---

## Phase 6: User Story 4 — Combined Personalization and Translation (Priority: P4)

**Goal**: A logged-in user can compose both features: generate personalized content, then translate it to Urdu (or vice versa). The system translates the personalized version, not the original.

**Independent Test**: Generate personalized version first, then click "Translate to Urdu" — verify Urdu translation reflects personalized content. Click "Revert to Original" — returns to English original.

### Implementation for User Story 4

- [X] T021 [US4] Add content state machine to ChapterToolbar tracking four states: `original`, `personalized`, `urdu`, `personalized-urdu`. When in `personalized` state and user clicks "Translate to Urdu", send the personalized content (not original) to `POST /api/translate` with an additional `content` field override. When reverting from `personalized-urdu`, return to `original` (not `personalized`) in `book/src/components/ChapterToolbar/index.tsx`
- [X] T022 [US4] Update `POST /api/translate` endpoint to accept an optional `content` field in the request body. When provided, translate the given content directly instead of fetching from Qdrant. This cached separately (do not overwrite the chapter-level translation cache) in `backend/src/api/translate.py`
- [X] T023 [US4] Update button visibility logic in ChapterToolbar: show appropriate buttons based on content state (e.g., in `personalized` state show both "Translate to Urdu" and "Revert to Original"; in `personalized-urdu` show "Revert to Original" only) in `book/src/components/ChapterToolbar/index.tsx`

**Checkpoint**: All four content states work correctly. Users can compose personalization + translation.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Security hardening, error handling, and production readiness across all user stories

- [X] T024 [P] Add input sanitization for `chapter_slug` parameter: validate format (alphanumeric, hyphens, slashes only), strip dangerous tokens (reuse pattern from `rag_pipeline.py`), enforce max length in both `backend/src/api/personalize.py` and `backend/src/api/translate.py`
- [X] T025 [P] Add comprehensive error handling: wrap AI service calls in try/except, return 503 with user-friendly message on OpenAI failures, return 404 when chapter not found in Qdrant, log errors via existing logger in `backend/src/services/content_personalizer.py` and `backend/src/services/content_translator.py`
- [X] T026 Add CORS configuration update: add backend URL to allowed origins for personalize and translate endpoints in `backend/main.py` (verify existing CORS config covers new routes)
- [X] T027 [P] Add error state UI to ChapterToolbar: show user-friendly error message ("Unable to generate content. Please try again later.") when API returns 429/503/500, retain current view on error, add retry button in `book/src/components/ChapterToolbar/index.tsx`
- [X] T028 Run quickstart.md manual validation checklist: verify all 7 test steps pass end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on T001, T002, T003 from Setup — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Phase 2 completion (T004, T005, T006)
- **User Story 2 (Phase 4)**: Depends on Phase 2 completion (T004, T006) — can run in PARALLEL with US1
- **User Story 3 (Phase 5)**: Depends on US1 (Phase 3) — needs the personalization button and API
- **User Story 4 (Phase 6)**: Depends on US1 (Phase 3) AND US2 (Phase 4) — composes both features
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: After Foundational → independent, MVP scope
- **User Story 2 (P2)**: After Foundational → independent from US1, can run in parallel
- **User Story 3 (P3)**: After US1 → extends the personalization button behavior
- **User Story 4 (P4)**: After US1 + US2 → composes both features

### Within Each User Story

- Backend API before frontend integration
- Services before API routes
- API routes before frontend calls
- Core implementation before state management refinements

### Parallel Opportunities

- **Phase 1**: T002 and T003 can run in parallel (config vs db methods)
- **Phase 2**: T005 and T006 can run in parallel (different service files)
- **Phase 3 + Phase 4**: US1 and US2 can run in parallel after foundational phase (different API routes, different services)
- **Phase 7**: T024, T025, T027 can all run in parallel (different files)

---

## Parallel Example: User Story 1 + User Story 2

```bash
# After Phase 2 completes, US1 and US2 can proceed in parallel:

# Developer A: User Story 1 (Personalization)
T007 → T008 → T009 → T010 → T011 → T012

# Developer B: User Story 2 (Translation)
T013 → T014 → T015 → T016 → T017 → T018

# Then sequentially:
# US3 (T019-T020) after US1 completes
# US4 (T021-T023) after both US1 + US2 complete
# Polish (T024-T028) after all stories complete
```

---

## Implementation Strategy

### MVP Scope: User Story 1 (Phase 1 + 2 + 3)

The minimum viable product is personalized chapter content for authenticated users. This delivers the core differentiating feature (P1 priority) and exercises the full stack: database, RAG retrieval, AI generation, caching, and frontend integration.

**MVP task count**: 12 tasks (T001–T012)

### Incremental Delivery

1. **MVP**: US1 (personalization) — 12 tasks
2. **+Translation**: US2 (Urdu) — 6 additional tasks (T013–T018)
3. **+Auth gate**: US3 (login modal) — 2 additional tasks (T019–T020)
4. **+Composition**: US4 (combined) — 3 additional tasks (T021–T023)
5. **+Polish**: Cross-cutting — 5 additional tasks (T024–T028)

### Total: 28 tasks
