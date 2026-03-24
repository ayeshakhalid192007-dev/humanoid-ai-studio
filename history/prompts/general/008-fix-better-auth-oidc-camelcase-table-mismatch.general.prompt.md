---
id: 008
title: Fix Better Auth OIDC camelCase Table Mismatch
stage: general
date: 2026-03-24
surface: agent
model: claude-sonnet-4-6
feature: none
branch: main
user: ayeshakhalid
command: "ok now it is still giving the same issue thoroughly check the issue and detects what is happening with the auth server why it didn't take the request and check that better auth is completely integrated or not"
labels: ["better-auth","oidc","database","bug-fix","migration"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - auth-server/scripts/migrate-oidc.js
  - auth-server/scripts/seed-public-client.js
  - auth-server/src/index.js
  - auth-server/src/auth.js
tests:
  - "curl /health → 200 healthy"
  - "curl /api/auth/oauth2/authorize (with session cookie) → 302 with code"
  - "curl /api/auth/oauth2/token (with correct PKCE verifier) → 200 with access_token"
  - "curl /api/auth/oauth2/userinfo (with Bearer token) → 200 with user claims"
---

## Prompt

ok now it is still giving the same issue thoroughly check the issue and detects what is happening with the auth server why it didn't take the request and check that better auth is completely integrated or not

## Response snapshot

Performed thorough end-to-end diagnostic of the auth server and Better Auth OIDC integration.

**Root causes found and fixed:**

1. **Bug 1 (Critical) — camelCase/snake_case table name mismatch**: Better Auth v1.5.6 uses camelCase table names directly (no automatic conversion). The `migrate-oidc.js` script created `oauth_consent`, `oauth_application`, `oauth_access_token` (snake_case) but Better Auth's Kysely adapter queries `"oauthConsent"`, `"oauthApplication"`, `"oauthAccessToken"`. The server log confirmed: `relation "oauthConsent" does not exist` → 500 on every authorize request.

2. **Bug 2 (Critical) — jwks column name mismatch**: The `jwks` table had columns `public_key`, `private_key`, `created_at` (snake_case) but Better Auth's JWT plugin expects `publicKey`, `privateKey`, `createdAt`.

3. **Bug 3 — seed-public-client.js used wrong table/column names**: Was inserting into `"oauth_application"` with snake_case columns. Better Auth would never find the client in its DB lookup.

4. **Bug 4 — ALLOWED_ORIGINS vs CORS_ORIGINS env var mismatch**: `auth.js` read `process.env.ALLOWED_ORIGINS` for Better Auth's internal CORS, but `.env` sets `CORS_ORIGINS`. Fix: read either env var.

**Fixes applied:**
- `migrate-oidc.js`: Now creates `"oauthApplication"`, `"oauthAccessToken"`, `"oauthConsent"` with camelCase columns; renames jwks columns to camelCase
- `seed-public-client.js`: Now inserts into `"oauthApplication"` with correct camelCase columns
- `src/index.js` admin endpoint: Updated to use `"oauthApplication"` with camelCase columns
- `src/auth.js`: Fixed env var to read `CORS_ORIGINS || ALLOWED_ORIGINS`

**Migration and seed run**: All tables created with correct names, `physical-ai-book` client seeded.

**Verified end-to-end**: authorize → 302 with code, token exchange → 200 with access_token + id_token (RS256 signed), userinfo → 200 with user claims including role and onboardingCompleted.

## Outcome

- ✅ Impact: Full OAuth 2.1 PKCE login flow now works end-to-end. Auth server no longer crashes with 500 on authorize requests.
- 🧪 Tests: Manual curl flow verified: sign-in → authorize (302) → token exchange (200) → userinfo (200)
- 📁 Files: 4 files modified, migration and seed scripts run
- 🔁 Next prompts: Test login via the actual browser UI; verify token refresh flow
- 🧠 Reflection: Better Auth v1.x Kysely adapter uses exact model names as table names (no snake_case conversion). Always verify table names match the adapter's schema definitions, not generic SQL conventions.

## Evaluation notes (flywheel)

- Failure modes observed: Custom migration script created snake_case tables without checking Better Auth's internal naming expectations
- Graders run and results (PASS/FAIL): Manual curl E2E flow PASS
- Prompt variant (if applicable): null
- Next experiment: Run automated login test from the browser frontend
