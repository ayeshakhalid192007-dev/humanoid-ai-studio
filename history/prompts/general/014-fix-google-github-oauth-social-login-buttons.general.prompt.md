---
name: Fix Google & GitHub OAuth Social Login Buttons
description: Diagnosed and fixed 4 bugs causing social login failures — broken onClick handlers on /login and /register pages, wrong Facebook icon, and missing GitHub email scope.
type: general
stage: general
id: "014"
date: 2026-03-25
surface: agent
model: claude-sonnet-4-6
feature: oauth-google-github
branch: feature/oauth-google-github
user: ayeshakhalid
command: "use the skill /code-analyzer and analyze the auth server code and fix all the small and critical issues..."
labels: ["auth", "oauth", "social-login", "google", "github", "bug-fix"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
---

## Prompt

use the skill /code-analyzer and analyze the auth server code and fix all the small and critical issues which are facing by users as when they are trying to login with their google account or github account they cannot be loginned properly facing issue as authentication failed also use the context7 mcp server and fetch the plugins and different skills from the marketplace and solve all issues regarding authentication

## Response

Used code-analyzer + bug-detecter skills. Ran static analysis (18 checks — all passed). Proceeded with deep manual analysis across all auth-related files. Found 4 bugs:

### Bugs Found & Fixed

**BUG 1 — CRITICAL: `/login` page social buttons had no `onClick` handler**
- File: `book/src/pages/login.tsx`
- Root cause: Google and GitHub buttons were decorative `<button>` elements with no onClick. Users clicking them got no response.
- Additionally: second button used Facebook SVG (wrong provider — app uses GitHub).
- Fix: Added `handleSocialSignIn` helper calling `signInWithSocial(provider)` from `useAuth()`. Wired `onClick={() => handleSocialSignIn('google')}` and `onClick={() => handleSocialSignIn('github')}`. Replaced Facebook SVG with GitHub SVG. Added `disabled` state during loading.

**BUG 2 — CRITICAL: `/register` page social buttons had no `onClick` handler + showed Facebook**
- File: `book/src/pages/register.tsx`
- Root cause: Both social buttons (Google + Facebook) had no onClick. Neither worked. Second button said "Continue with Facebook" — wrong provider.
- Fix: Added same `handleSocialSignIn` helper. Wired both buttons. Replaced Facebook icon + label with GitHub.

**BUG 3 — MEDIUM: GitHub provider missing explicit email scope**
- File: `auth-server/src/auth.js`
- Root cause: GitHub social provider had no `scope` configured. GitHub does not return the primary email by default for users with private email settings. Better Auth's default scope may or may not include `user:email`.
- Fix: Added `scope: ["read:user", "user:email"]` to the github provider config.

**BUG 4 — MINOR: `.env.example` missing `BOOK_CLIENT_ID` / `BOOK_REDIRECT_URIS`**
- File: `auth-server/.env.example`
- Root cause: These env vars control the trusted OIDC client and redirect URIs but were undocumented in the example file.
- Fix: Added both vars with their default values and explanatory comment.

### Files Modified
- `book/src/pages/login.tsx`
- `book/src/pages/register.tsx`
- `auth-server/src/auth.js`
- `auth-server/.env.example`

### Root cause summary
The primary auth failure was that the social login buttons on the **main** `/login` and `/register` pages (Tailwind-styled) were completely disconnected from the auth logic. The separate `/auth/login` page (CSS Modules, OIDC relay) had working buttons via `LoginForm.tsx`, but users landing on `/login` or `/register` (the default routes) saw non-functional buttons.
