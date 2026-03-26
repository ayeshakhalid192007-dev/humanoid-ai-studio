---
name: Fix GET /api/profile 401 — OAuth2 JWT Token Validation
description: Fixed 401 on GET /api/profile by adding OAuth2 JWT validation via OIDC userinfo endpoint in getSessionFromRequest
type: general
stage: green
date: 2026-03-27
surface: agent
model: claude-sonnet-4-6
feature: none
branch: main
user: ayeshakhalid
command: continuation of authentication debugging session
labels: ["auth", "better-auth", "oauth2", "jwt", "bug-fix"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - auth-server/src/index.js
tests: []
---

## Prompt

(Continuation from prior session) Fix the `GET /api/profile → 401` race condition identified during Playwright end-to-end verification of the authentication flow.

## Response

**Root cause identified:** `getSessionFromRequest()` in `auth-server/src/index.js` called `auth.api.getSession()` with the Bearer token. The `bearer()` plugin handles Better Auth *session tokens* (database-backed), not OAuth2 JWT access tokens issued by the `oidcProvider` plugin. These are fundamentally different token types — the JWT has no session entry to look up.

**Fix applied:** Added fallback path `1b` in `getSessionFromRequest` that, when `auth.api.getSession()` fails for a Bearer token, calls `auth.handler()` for `/api/auth/oauth2/userinfo` — the OIDC userinfo endpoint which natively validates JWTs. If the token is valid, the user is fetched from the database by `sub` claim and returned as a synthetic session object.

**Files changed:**
- `auth-server/src/index.js`: Added JWT fallback in `getSessionFromRequest` (lines 168-210)

**Commit:** `c3d393e` pushed to `main`

## Outcome

`GET /api/profile` now authenticates correctly for users who signed in via OAuth2 PKCE flow. The 401 race condition is resolved.
