---
id: 010
title: Fix Better Auth Signup Failure & Course Display
stage: green
date: 2026-02-15
surface: agent
model: claude-opus-4-6
feature: 001-book-publication-rag-chatbot
branch: 001-book-publication-rag-chatbot
user: MASTER
command: implement
labels: ["bugfix", "auth", "routing", "database", "better-auth"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/.env
  - .env
  - auth-server/src/index.js
  - book/src/theme/Root.tsx
  - auth-server/scripts/fix-schema.js
  - auth-server/package.json
  - book/src/components/Auth/index.ts
  - book/src/components/Auth/RouteGuard.tsx (deleted)
tests:
  - Manual: run fix-schema.js migration against Neon DB
  - Manual: test signup API POST to localhost:3002
  - Manual: verify docs pages load without redirect
  - Manual: verify dashboard requires authentication
---

## Prompt

Implement the following plan:

# Fix Better Auth Integration — Signup Failure & Course Display

## Root Cause Analysis — 5 interconnected bugs:

1. BETTER_AUTH_URL misconfigured (pointing to port 3000 instead of 3002)
2. user_profiles CHECK constraints block free-text signup
3. RouteGuard blocks all content for unauthenticated users
4. Duplicate RouteGuard implementations with conflicting logic
5. Better Auth user table may be missing custom columns (role, onboardingCompleted)

## Response snapshot

Implemented all 6 fixes from the plan:

**Fix 1 — BETTER_AUTH_URL**: Changed `http://localhost:3000` → `http://localhost:3002` in both `backend/.env` and root `.env`. This was the critical bug — the Python backend was validating sessions against the Docusaurus frontend instead of the auth server.

**Fix 2 — DB migration script**: Created `auth-server/scripts/fix-schema.js` — an idempotent script that adds `role` and `onboardingCompleted` columns to the `user` table if missing, ensures `user_profiles` table exists, and drops CHECK constraints on `software_background`/`hardware_background` to allow free-text values.

**Fix 3 — RouteGuard logic inversion**: Changed `Root.tsx` from "block everything except whitelist" to "allow everything except protected routes". Only `/dashboard` and `/auth/onboarding` now require authentication. Docs, features, testimonials, and home are publicly accessible.

**Fix 4 — auth.js Kysely driver**: Reviewed and confirmed the connection pattern is correct — `pool.connect()` returns a pg client with `.release()` which the custom driver handles properly. No changes needed.

**Fix 5 — roboticsKnowledge validation**: Added `"none"` to `ALLOWED_ROBOTICS_LEVELS` array in `auth-server/src/index.js` and updated the error message.

**Fix 6 — Removed unused RouteGuard.tsx**: Deleted `book/src/components/Auth/RouteGuard.tsx` and removed its barrel export from `index.ts`. This file was never imported by `Root.tsx` and had stale/conflicting redirect logic.

## Outcome

- ✅ Impact: 5 bugs fixed across auth, routing, and database layers; signup flow should now work end-to-end
- 🧪 Tests: Manual verification plan provided (DB migration, signup API, docs visibility, dashboard auth)
- 📁 Files: 6 modified, 1 created, 1 deleted
- 🔁 Next prompts: Run `cd auth-server && npm run db:fix-schema` to apply DB migration, then test full signup flow
- 🧠 Reflection: The bugs were interconnected — BETTER_AUTH_URL alone would cause silent auth failures, but the RouteGuard compounded the issue by redirecting even authenticated users

## Evaluation notes (flywheel)

- Failure modes observed: Misconfigured env var caused silent cascade across all auth-dependent features
- Graders run and results (PASS/FAIL): N/A — manual verification required
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Run fix-schema.js and test signup end-to-end
