---
id: 006
title: Refactoring Bugfixes and Localhost Startup
stage: green
date: 2026-02-16
surface: agent
model: claude-opus-4-6
feature: 002-personalized-chapters-urdu
branch: 002-personalized-chapters-urdu
user: architect
command: implement
labels: ["bugfix", "refactor", "localhost", "xss", "connection-pool", "startup"]
links:
  spec: specs/002-personalized-chapters-urdu/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/api/sessions.py
  - backend/src/api/rate_limit.py
  - backend/src/api/personalize.py
  - backend/src/api/translate.py
  - backend/src/api/auth.py
  - backend/src/api/validators.py
  - backend/src/api/__init__.py
  - backend/src/config.py
  - backend/src/services/content_personalizer.py
  - backend/src/services/content_translator.py
  - backend/src/services/__init__.py
  - backend/main.py
  - book/src/components/ChapterToolbar/index.tsx
  - .env.example
tests:
  - curl http://localhost:8000/ (200 OK)
  - curl http://localhost:8000/health (200 OK, qdrant up, openai up)
  - curl http://localhost:3002/health (200 OK, healthy)
  - Docusaurus compiled successfully with no errors
---

## Prompt

Implement the following plan:

# Refactoring & Localhost Startup Plan

## Goal
Fix bugs and issues in the Feature 002 (Personalized Chapters + Urdu Translation) implementation, then get all 3 servers running on localhost for manual E2E testing.

[Full 5-phase plan covering: Backend Critical Fixes, Backend Code Hygiene, Frontend Critical Fixes, Localhost Startup, and Verification]

## Response snapshot

Implemented all 5 phases of the refactoring plan:

**Phase 1 - Backend Critical Fixes:**
- Fixed NeonClient pool-per-request leak in `sessions.py` — replaced local `get_neon_client()` with singleton import, removed all `finally: await client.close()` blocks
- Fixed NeonClient in `rate_limit.py` — replaced lazy local client with singleton `get_neon_client()` from `neon_client.py`
- Fixed hardcoded profile URL in `personalize.py` — now uses `settings.BETTER_AUTH_URL`
- Fixed BETTER_AUTH_URL default port in `config.py` (3000 → 3002) and fallback in `auth.py`
- Added null checks on OpenAI responses in `content_personalizer.py` and `content_translator.py`

**Phase 2 - Backend Code Hygiene:**
- Extracted shared slug validation into `backend/src/api/validators.py`
- Updated `personalize.py` and `translate.py` to import from shared `validators.py`
- Updated `__init__.py` files for api and services packages
- Cleaned up `main.py` imports (consolidated duplicate import block)

**Phase 3 - Frontend Critical Fixes:**
- Replaced fragile `simpleMarkdownToHtml()` with `marked` + `DOMPurify` for XSS-safe rendering
- Added `lastFailedAction` state for correct retry button behavior
- Removed dead `handleAuthSuccess` callback
- Fixed urdu→personalized state transition: Personalize button now only shows in `original` state
- Changed all `catch (err: any)` to `catch (err: unknown)` with proper type narrowing

**Phase 4 - Localhost Startup:**
- Verified .env files exist with all required keys
- Fixed corrupted Python 3.14 asyncio/runners.py (commented-out return statements)
- Ran DB migration successfully (3 tables + indexes created)
- Started all 3 servers: auth-server (:3002), backend (:8000), Docusaurus (:3000)

**Phase 5 - Verification:**
- Backend root, health, and docs endpoints return 200
- Auth server health returns 200
- Docusaurus compiled successfully with zero errors
- Note: Qdrant scroll requires keyword index on "module" field (infra issue, not code bug)

## Outcome

- Impact: 14 files modified, 1 new file created, all critical bugs fixed, all 3 servers running
- Tests: Manual curl tests pass for all health endpoints; Docusaurus webpack compilation clean
- Files: 14 modified + 1 new (validators.py)
- Next prompts: Create Qdrant payload index for "module" field; manual E2E testing of personalization and translation flows
- Reflection: The NeonClient pool leak was the most impactful fix — would have caused connection exhaustion in production. The Python 3.14 asyncio corruption was an unexpected blocker.

## Evaluation notes (flywheel)

- Failure modes observed: Python 3.14 stdlib corruption (asyncio/runners.py had return statements commented out); Qdrant missing payload index for filtered scroll
- Graders run and results (PASS/FAIL): Manual endpoint health checks PASS; Webpack compilation PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add Qdrant payload index for "module" field to unblock chapter retrieval
