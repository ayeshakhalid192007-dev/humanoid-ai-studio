---
id: "003"
title: Google GitHub OAuth implementation plan
stage: plan
date: 2026-03-24
surface: agent
model: claude-sonnet-4-6
feature: 1-oauth-social-login
branch: feature/oauth-google-github
user: ayeshakhalid
command: /sp.plan
labels: ["oauth", "google", "github", "better-auth", "plan", "social-login"]
links:
  spec: specs/1-oauth-social-login/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/1-oauth-social-login/plan.md
tests:
  - Manual: Google new user signup → onboarding → dashboard
  - Manual: GitHub new user signup → onboarding → dashboard
  - Manual: Returning social login (no onboarding shown)
  - Manual: Email/password regression — existing flow unchanged
  - Manual: Account deduplication (same email, different auth methods)
  - Manual: OAuth cancellation → friendly error shown
---

## Prompt

I want to add Google and GitHub OAuth login/signup to my existing project. Before writing any code, I want you to only create a detailed implementation plan — do not touch any files yet.
First, explore the project by:

Reading the folder structure
Checking the existing auth implementation
Identifying the database, ORM, session/JWT strategy, and any existing auth libraries
Checking the current User model/schema for existing fields
Reviewing existing login/signup UI components and routes

Then produce a full plan that includes:
1. Branch Strategy
   Branch name to create (e.g. feature/oauth-google-github)
   Base branch to branch off from

2. Dependencies to Install
   List every npm/pip/composer package that needs to be added and why

3. Environment Variables
   List all new .env variables needed with placeholder values

4. Database / Schema Changes
   Specify any new fields or tables/collections needed in the User model
   Show the exact schema diff or migration needed

5. Backend Changes — File by File
   List every file that will be created or modified
   For each file, describe exactly what will change and why
   Include OAuth callback route logic, token exchange, user lookup/creation strategy

6. Frontend Changes — File by File
   List every UI file that will be updated
   Describe where Google and GitHub buttons will be added
   Describe any new pages or redirects needed

7. Potential Risks & Edge Cases
   Account already exists with same email via password
   User tries to link multiple providers
   OAuth failure or cancellation handling
   Existing auth flow breaking

8. Testing Checklist
   List every scenario that should be manually tested after implementation

Do not create any branch, install any package, or modify any file. Present the full plan and wait for my approval before proceeding.

## Response snapshot

Created `specs/1-oauth-social-login/plan.md` — full implementation plan covering:

**Branch**: `feature/oauth-google-github` (already exists, no action needed)

**Dependencies**: None — `better-auth ^1.2.0` has built-in `socialProviders` support

**Schema**: No migration needed — existing `account` table already stores `providerId` + `accountId`

**Backend change (1 file)**: `auth-server/src/auth.js` — add `socialProviders: { google: {...}, github: {...} }` config block (5 lines). Better Auth automatically adds `/api/auth/sign-in/social/*` and `/api/auth/callback/*` routes.

**Frontend changes (4 files)**:
- `AuthContext.tsx` — add `signInWithSocial(provider)` method
- `LoginForm.tsx` — add Google + GitHub buttons above email form
- `SignUpForm.tsx` — same social buttons on signup form
- `Auth.module.css` — social button styles

**Architecture decision**: Social auth routes through the existing PKCE/OIDC flow — `signInWithSocial` generates PKCE params, sets the OIDC authorize URL as the social sign-in `callbackURL`. After provider auth, Better Auth redirects to the OIDC authorize URL which issues a code → existing `/auth/callback` page handles it unchanged.

**No new pages, no new packages, no schema changes.**

## Outcome

- ✅ Impact: Complete implementation plan created; zero files modified; awaiting user approval to proceed
- 🧪 Tests: 12 manual test scenarios documented in plan Section 8
- 📁 Files: specs/1-oauth-social-login/plan.md (created)
- 🔁 Next prompts: User approves plan → run /sp.implement or execute plan manually
- 🧠 Reflection: The existing PKCE/OIDC infrastructure is reused entirely — social auth piggybacks on it with no new callback pages or token handling paths needed

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): n/a — planning stage
- Prompt variant (if applicable): n/a
- Next experiment: Validate that Better Auth accepts same-server OIDC authorize URL as social sign-in callbackURL (Risk 1 in plan)
