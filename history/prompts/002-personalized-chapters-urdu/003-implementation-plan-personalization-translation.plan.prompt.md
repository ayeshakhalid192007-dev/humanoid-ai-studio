---
id: 003
title: Implementation Plan Personalization Translation
stage: plan
date: 2026-02-16
surface: agent
model: claude-opus-4-6
feature: 002-personalized-chapters-urdu
branch: 002-personalized-chapters-urdu
user: MASTER
command: /sp.plan
labels: ["planning", "architecture", "rag", "personalization", "urdu-translation", "api-design"]
links:
  spec: specs/002-personalized-chapters-urdu/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-personalized-chapters-urdu/plan.md
  - specs/002-personalized-chapters-urdu/research.md
  - specs/002-personalized-chapters-urdu/data-model.md
  - specs/002-personalized-chapters-urdu/contracts/api-contracts.md
  - specs/002-personalized-chapters-urdu/quickstart.md
tests:
  - none
---

## Prompt

# Implementation Plan: Personalized Chapters and Urdu Translation

## Objective
Plan implementation of:
1. AI-based Personalized Chapters (auth required)
2. AI-based Urdu Translation (public access)

---

## Architecture Plan

### 1. Frontend
- Add two buttons on chapter page:
  - "Personalized Version"
  - "Translate to Urdu"
- Implement toggle state management.
- Show login modal for personalization if unauthenticated.
- Add loading and error states.

---

### 2. Backend API

Create endpoints:

- POST /api/personalize
  - Requires authentication
  - Inputs: chapterId
  - Fetch chapter content + user profile
  - Run AI personalization with RAG
  - Cache result
  - Return structured markdown

- POST /api/translate
  - Public endpoint
  - Inputs: chapterId
  - Translate content to Urdu
  - Preserve formatting
  - Cache result

---

### 3. AI Layer

- Define strict prompt templates:
  - Personalization prompt (uses chapter + user profile)
  - Translation prompt (preserves markdown and code blocks)
- Enforce hallucination prevention.
- Limit context strictly to provided chapter content.

---

### 4. Database Updates

Add optional fields:
- personalizedContent (per user per chapter)
- urduTranslation (per chapter)
- lastGeneratedAt

Create relational mapping:
- userId
- chapterId

---

### 5. Access Control

- Personalization requires valid session.
- Translation available without authentication.
- Protect personalization API via middleware.

---

### 6. Caching Strategy

- Cache personalized output per user per chapter.
- Cache translation per chapter.
- Regenerate only if not cached.

---

## Deliverables

- Updated UI components
- Middleware adjustments
- Two API routes
- AI prompt templates
- DB schema migration
- Clean production-ready implementation

## Response snapshot

Completed full implementation planning workflow (Phase 0 + Phase 1):

**Phase 0 - Research** (`research.md`): Resolved 10 research areas including RAG pipeline extension strategy, chapter retrieval via Qdrant metadata filtering, content version tracking, database schema design, AI prompt engineering approach, Docusaurus DocItem/Content swizzle pattern, Urdu RTL support, rate limiting strategy, and authentication flow integration.

**Phase 1 - Design & Contracts**:
- `data-model.md`: Three new Postgres tables (personalized_content, urdu_translations, ai_generation_rate_limits) with indexes, entity relationships, and state transition diagrams
- `contracts/api-contracts.md`: Four API endpoints (POST /api/personalize, POST /api/translate, GET status endpoints) with full request/response schemas and error taxonomy
- `quickstart.md`: Setup steps, manual test checklist, and key architecture decisions
- `plan.md`: Complete implementation plan with technical context, 6 architecture decisions, component interaction flows, project structure, and risk mitigation

Key architecture decisions:
1. Extend existing Qdrant RAG pipeline (no new vector DB)
2. Full chapter retrieval via Qdrant metadata filtering
3. Separate prompt templates for personalization vs translation
4. Docusaurus DocItem/Content swizzle for button injection
5. In-place content replacement (no tabs/side-by-side)
6. Cache in Neon Postgres (not Redis)

## Outcome

- ✅ Impact: Complete implementation plan with all Phase 0 and Phase 1 artifacts generated
- 🧪 Tests: none (planning phase only)
- 📁 Files: plan.md, research.md, data-model.md, contracts/api-contracts.md, quickstart.md created; CLAUDE.md updated with tech context
- 🔁 Next prompts: /sp.tasks to generate implementation task breakdown
- 🧠 Reflection: Thorough codebase exploration was critical — discovered existing RAG pipeline, Qdrant integration, AuthModal, AuthContext, and Docusaurus swizzle patterns that all get reused directly

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): N/A - planning phase
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
