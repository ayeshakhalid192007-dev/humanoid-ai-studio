---
id: 005
title: Implement Personalization Translation Features
stage: green
date: 2026-02-16
surface: agent
model: claude-opus-4-6
feature: 002-personalized-chapters-urdu
branch: 002-personalized-chapters-urdu
user: MASTER
command: /sp.implement
labels: ["implementation", "personalization", "urdu-translation", "backend", "frontend", "database"]
links:
  spec: specs/002-personalized-chapters-urdu/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/scripts/setup_db_personalization.py
  - backend/src/config.py
  - backend/src/db/neon_client.py
  - backend/src/services/chapter_retriever.py
  - backend/src/services/content_personalizer.py
  - backend/src/services/content_translator.py
  - backend/src/api/personalize.py
  - backend/src/api/translate.py
  - backend/main.py
  - book/src/components/ChapterToolbar/index.tsx
  - book/src/components/ChapterToolbar/styles.module.css
  - book/src/theme/DocItem/Content/index.tsx
  - book/src/css/custom.css
  - specs/002-personalized-chapters-urdu/tasks.md
tests:
  - none
---

## Prompt

now implement these features in my project

## Response snapshot

Completed full implementation of all 28 tasks across 7 phases:

**Phase 1 (Setup)**: Created DB migration script, added AI rate limit config, added NeonClient cache CRUD methods
**Phase 2 (Foundational)**: Created ChapterRetriever, ContentPersonalizer, ContentTranslator services
**Phase 3 (US1)**: Created personalize API (POST + GET status), registered router, created ChapterToolbar component with personalize button, created DocItem/Content swizzle
**Phase 4 (US2)**: Created translate API (POST + GET status), registered router, added translate button, RTL CSS, RTL content styles
**Phase 5 (US3)**: Added AuthModal integration for unauthenticated users, auto-personalization after login
**Phase 6 (US4)**: Added 4-state content machine (original/personalized/urdu/personalized-urdu), content override in translate API, button visibility logic
**Phase 7 (Polish)**: Input sanitization, error handling (503/404/429), CORS verified, error UI with retry

New files: 8 | Modified files: 5 | Total tasks: 28/28 complete

## Outcome

- ✅ Impact: All 4 user stories implemented end-to-end
- 🧪 Tests: Manual E2E via quickstart.md checklist
- 📁 Files: 13 files created/modified (8 new, 5 modified)
- 🔁 Next prompts: Run DB migration, start all 3 servers, manual E2E testing
- 🧠 Reflection: Combined US3/US4 logic into ChapterToolbar from the start (state machine + auth modal) rather than building incrementally — more efficient, fewer rewrites

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): N/A - implementation phase, manual testing needed
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
