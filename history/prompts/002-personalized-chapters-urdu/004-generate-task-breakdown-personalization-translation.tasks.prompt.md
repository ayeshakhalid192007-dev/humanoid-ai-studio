---
id: 004
title: Generate Task Breakdown Personalization Translation
stage: tasks
date: 2026-02-16
surface: agent
model: claude-opus-4-6
feature: 002-personalized-chapters-urdu
branch: 002-personalized-chapters-urdu
user: MASTER
command: /sp.tasks
labels: ["tasks", "breakdown", "personalization", "urdu-translation", "implementation"]
links:
  spec: specs/002-personalized-chapters-urdu/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-personalized-chapters-urdu/tasks.md
tests:
  - none
---

## Prompt

# Task Breakdown: Personalized Chapters and Urdu Translation

## Objective
Implement:
1. AI-based Personalized Chapters (requires authentication)
2. AI-based Urdu Translation (public access)

[Full task breakdown provided by user covering 8 phases: Database, Authentication Validation, Backend API Development, AI Prompt Engineering, Frontend Integration, Caching Strategy, Security & Stability, Testing]

## Response snapshot

Generated dependency-ordered tasks.md with 28 tasks across 7 phases organized by user story:

- **Phase 1 (Setup)**: 3 tasks — DB migration, config, NeonClient cache methods
- **Phase 2 (Foundational)**: 3 tasks — ChapterRetriever, ContentPersonalizer, ContentTranslator services
- **Phase 3 (US1 - Personalization)**: 6 tasks — API endpoints, router registration, ChapterToolbar component, DocItem/Content swizzle
- **Phase 4 (US2 - Translation)**: 6 tasks — Translation API, RTL CSS, toolbar translation button
- **Phase 5 (US3 - Auth Gate)**: 2 tasks — AuthModal integration, auto-personalization after login
- **Phase 6 (US4 - Combined)**: 3 tasks — Content state machine, optional content override in translate API, button visibility logic
- **Phase 7 (Polish)**: 5 tasks — Input sanitization, error handling, CORS, error UI, E2E validation

Key decisions:
- US1 and US2 can run in parallel after foundational phase
- MVP scope is US1 only (12 tasks)
- No test tasks (not explicitly requested in spec)
- Each user story independently testable

## Outcome

- ✅ Impact: 28 executable tasks generated, organized by user story with clear dependencies
- 🧪 Tests: none (not requested in spec)
- 📁 Files: specs/002-personalized-chapters-urdu/tasks.md created
- 🔁 Next prompts: /sp.implement to begin executing tasks, or /sp.analyze for cross-artifact consistency check
- 🧠 Reflection: Reorganized user's phase-based breakdown into story-based phases for independent testability. Combined user's 8 phases into 7 story-aligned phases.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): N/A - task generation phase
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
