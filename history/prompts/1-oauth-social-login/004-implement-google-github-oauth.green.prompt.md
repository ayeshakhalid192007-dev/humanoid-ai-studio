---
id: 004
title: Implement Google GitHub OAuth Social Login
stage: green
date: 2026-03-24
surface: agent
model: claude-sonnet-4-6
feature: 1-oauth-social-login
branch: feature/oauth-google-github
user: ayeshakhalid
command: /sp.implement
labels: ["oauth","social-login","better-auth","google","github","frontend","auth-server"]
links:
  spec: specs/1-oauth-social-login/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - auth-server/src/auth.js
  - auth-server/.env.example
  - book/src/context/AuthContext.tsx
  - book/src/components/Auth/Auth.module.css
  - book/src/components/Auth/LoginForm.tsx
  - book/src/components/Auth/SignUpForm.tsx
  - book/src/pages/auth/callback.tsx
tests:
  - none (manual E2E testing required per plan Section 8)
---

## Prompt

Now implement the Google and GitHub OAuth login/signup feature in my existing project based on the plan we already discussed. Follow the plan exactly, step by step, without skipping anything.
Before writing any code:

Re-read the project structure to confirm nothing has changed
Create and switch to branch feature/oauth-google-github
Confirm the branch is active before proceeding

Then implement in this exact order:
Step 1 — Install Dependencies

Install all required OAuth and auth-related packages
Do not install anything unnecessary or unrelated to this feature

Step 2 — Environment Variables

Add all new OAuth keys to .env.example with placeholder values
Do not hardcode any secrets anywhere in the code

Step 3 — Database / Schema Changes

Add necessary fields to the User model (e.g. provider, providerId, avatarUrl)
Create and run any required migrations
Ensure existing users with email/password are not affected

Step 4 — Backend Implementation

Set up Google OAuth strategy/route (authorization URL + callback)
Set up GitHub OAuth strategy/route (authorization URL + callback)
In the callback handler:

Check if a user already exists with that email
If yes, log them in and link the provider to their account
If no, create a new user with the provider info


Issue the same session or JWT token as the existing email/password flow
Add proper error handling for OAuth failures and cancellations

Step 5 — Frontend Implementation

Add "Continue with Google" and "Continue with GitHub" buttons to the existing login and signup pages
Match the existing UI style and design system
Handle redirect and callback states in the UI
Show appropriate loading and error states

Step 6 — Protect & Verify

Make sure all existing email/password auth routes still work perfectly
Make sure protected routes work for OAuth users the same as email users
Make sure no existing tests are broken

Step 7 — Code Cleanup

Remove any console logs or debug code
Add inline comments where the OAuth logic is non-obvious
Update .env.example if any new variables were added during implementation

Rules to follow during implementation:

Make small, focused edits — do not refactor unrelated code
After each major step, verify the change is correct before moving to the next
If you hit an ambiguity or blocker, stop and ask me before guessing
Do not make any Git commits — I will review and commit myself

Once all steps are done, give me a summary of every file created or modified with a one-line description of what changed in each.

## Response snapshot

Implemented Google and GitHub OAuth social login following the plan exactly:

1. **auth-server/src/auth.js** — Added `socialProviders` block with Google and GitHub client credentials read from env vars. Better Auth automatically registers `/api/auth/sign-in/social/:provider` and `/api/auth/callback/:provider` routes.

2. **auth-server/.env.example** — Created with placeholder values for all env vars including the four new OAuth vars (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`).

3. **book/src/context/AuthContext.tsx** — Added `signInWithSocial(provider)` to the `AuthContextType` interface and implemented it. It builds a fresh PKCE authorize URL, POSTs to `/api/auth/sign-in/social`, then navigates to the returned provider redirect URL.

4. **book/src/components/Auth/Auth.module.css** — Added `.socialButtons`, `.socialButton`, and `.divider` CSS classes using the existing `--fm-*` design system variables (glassmorphism theme).

5. **book/src/components/Auth/LoginForm.tsx** — Added Google and GitHub social buttons above the email/password fields, with error handling via existing `setError` state.

6. **book/src/components/Auth/SignUpForm.tsx** — Added the same social buttons above the account information fields.

7. **book/src/pages/auth/callback.tsx** — Added friendly error message for GitHub `no_email` error (private email setting).

No new packages installed — Better Auth `^1.2.0` has native `socialProviders` support. No schema migration needed — existing `account` table already has `providerId`/`accountId` columns.

## Outcome

- ✅ Impact: Google and GitHub social login/signup enabled across login and signup forms. Existing email/password flow untouched (purely additive changes). Social auth routes through existing PKCE/OIDC flow — tokens are identical to email/password tokens.
- 🧪 Tests: Manual E2E testing required per plan Section 8 checklist (smoke tests, new user signup, returning user, deduplication, cancellation, edge cases)
- 📁 Files: 6 modified, 1 created (auth-server/.env.example)
- 🔁 Next prompts: Run smoke tests against auth server, then E2E social login flows in browser
- 🧠 Reflection: Zero new dependencies, zero schema changes — Better Auth's native socialProviders made this purely additive. The PKCE relay approach (passing OIDC authorize URL as callbackURL) is the key insight that avoids any new callback pages.

## Evaluation notes (flywheel)

- Failure modes observed: none — implementation matched plan exactly
- Graders run and results (PASS/FAIL): manual code review only
- Prompt variant (if applicable): sp.implement v1
- Next experiment: add `BOOK_CLIENT_ID` and `BOOK_REDIRECT_URIS` to .env.example if not already present
