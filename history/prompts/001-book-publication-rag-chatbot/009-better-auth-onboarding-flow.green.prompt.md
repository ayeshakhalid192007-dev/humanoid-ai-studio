---
id: 9
title: Better Auth + User Onboarding Flow
stage: green
date: 2026-02-14
surface: agent
model: claude-opus-4-6
feature: 001-book-publication-rag-chatbot
branch: 001-book-publication-rag-chatbot
user: architect
command: implement
labels: ["auth", "onboarding", "better-auth", "neon-postgres"]
links:
  spec: specs/001-book-publication-rag-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - auth-server/src/auth.js
  - auth-server/src/index.js
  - auth-server/package.json
  - auth-server/scripts/create-profiles-table.js
  - auth-server/scripts/migrate-to-better-auth.js
  - book/src/context/AuthContext.tsx
  - book/src/components/Auth/OnboardingForm.tsx
  - book/src/components/Auth/SignUpForm.tsx
  - book/src/components/Auth/Auth.module.css
  - book/src/components/Auth/index.ts
  - book/src/pages/auth/onboarding.tsx
  - book/src/pages/auth/signup.tsx
  - backend/src/api/auth.py
  - .env.example
tests:
  - Manual: signup flow → onboarding redirect
  - Manual: sign-in existing user → no onboarding redirect
  - Manual: GET /health → 200
  - Manual: POST /api/profile → saves and marks onboarding complete
  - Manual: backend session validation with new cookie name
---

## Prompt

Implement the following plan:

# Plan: Better Auth + User Onboarding

Replace the custom Express auth server with Better Auth SDK (using Neon Postgres), and add a post-signup onboarding flow that collects software background, hardware background, and robotics knowledge level via dropdown/radio options, stored in a `user_profiles` table.

## Response snapshot

Implemented the full 5-phase plan:

**Phase 1 — Auth Server Rewrite:**
- Rewrote `auth-server/src/auth.js` to use Better Auth SDK with Neon Postgres Pool, PBKDF2 password hashing (for backward compatibility), and `onboardingCompleted` additional field.
- Rewrote `auth-server/src/index.js` from ~400 lines custom implementation to ~170 lines using `toNodeHandler(auth)` for all `/api/auth/*` routes, plus custom `POST/GET /api/profile` endpoints.
- Updated `package.json` with migration scripts and removed SQLite dependency.
- Deleted legacy `auth.db`.

**Phase 2 — Database Scripts:**
- Created `create-profiles-table.js` — creates `user_profiles` table with CHECK constraints for experience levels.
- Created `migrate-to-better-auth.js` — migrates existing `auth_users` data to Better Auth's `user`/`account` tables.

**Phase 3 — Frontend Onboarding:**
- Updated `AuthContext.tsx` with `needsOnboarding`, `profile`, `saveProfile()`, `fetchProfile()`, and switched session endpoint to `/api/auth/get-session`.
- Created `OnboardingForm.tsx` with 3 radio groups (software, hardware, robotics) using styled card options.
- Created `onboarding.tsx` page at `/auth/onboarding`.
- Updated `SignUpForm.tsx` to navigate to `/auth/onboarding` after successful signup.
- Added CSS for `.radioGroup`, `.radioOption`, `.radioSelected`, `.radioDescription`.
- Updated `Auth/index.ts` exports.

**Phase 4 — Backend Python Fix:**
- Fixed cookie name: `better-auth.session_token` → `physical-ai.session_token`.
- Fixed session endpoint: `/api/auth/session` → `/api/auth/get-session`.

**Phase 5 — Config:**
- Updated `.env.example` BETTER_AUTH_URL to port 3002.

## Outcome

- ✅ Impact: Full auth rewrite + onboarding flow across 14 files
- 🧪 Tests: Manual verification required (signup → onboarding → profile save → session validation)
- 📁 Files: 14 files modified/created
- 🔁 Next prompts: Run Better Auth CLI migration, test end-to-end flow, consider email verification
- 🧠 Reflection: PBKDF2 compat layer is critical for existing users; Better Auth's toNodeHandler simplifies the server significantly

## Evaluation notes (flywheel)

- Failure modes observed: None during implementation; key risk is Better Auth API response shape mismatch
- Graders run and results (PASS/FAIL): N/A (manual testing required)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Start auth-server and verify /health + signup flow end-to-end
