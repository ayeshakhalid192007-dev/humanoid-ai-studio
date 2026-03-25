---
id: "002"
title: Better Auth OAuth OIDC Full Implementation
stage: general
date: 2026-03-23
surface: agent
model: claude-sonnet-4-6
feature: none
branch: main
user: ayeshakhalid
command: /better-auth-setup (implementation)
labels: ["auth","oauth","oidc","pkce","jwt","jwks","implementation","better-auth"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - auth-server/src/auth.js (modified — added oidcProvider, jwt, bearer, admin plugins)
  - auth-server/src/index.js (modified — Bearer token support for /api/profile, admin client registration endpoint, crypto import)
  - auth-server/scripts/migrate-oidc.js (new — creates oauth_application, oauth_access_token, oauth_consent, jwks tables)
  - auth-server/scripts/seed-public-client.js (new — seeds physical-ai-book public client)
  - auth-server/package.json (modified — added db:migrate-oidc and db:seed-client npm scripts)
  - book/docusaurus.config.js (modified — added oauthClientId and oauthRedirectUri customFields)
  - book/src/lib/oauth.ts (new — PKCE utilities, token storage, userinfo, refresh)
  - book/src/pages/auth/callback.tsx (new — OAuth callback page)
  - book/src/context/AuthContext.tsx (rewritten — token-based OAuth flow)
  - book/src/components/Auth/LoginForm.tsx (modified — OAuth relay + PKCE param preservation)
  - book/src/components/Auth/SignUpForm.tsx (modified — OAuth relay + PKCE param preservation)
  - book/src/components/ChatKitWidget/index.tsx (fixed — AuthContext import path)
  - backend/src/api/auth.py (modified — OIDC userinfo Bearer token validation + legacy session fallback)
tests:
  - auth-server syntax check (node --check) — PASS
  - backend syntax check (ast.parse) — PASS
  - TypeScript check (no new logic errors) — PASS
---

## Prompt

now continue with the plan which you have created implement it

## Response snapshot

Implemented the complete Better Auth OAuth 2.1 / OIDC + PKCE system across all 6 phases:

**Phase 1** — Added `oidcProvider()`, `jwt()` (RS256/JWKS), `bearer()`, and `admin()` plugins to `auth-server/src/auth.js`. Exposed `role` and `onboardingCompleted` as custom OIDC claims. Configured 6h access tokens, 7d refresh tokens, 10m auth codes. Trusted client `physical-ai-book` seeded inline. ALLOWED_ORIGINS now read from env.

**Phase 2** — Created `scripts/migrate-oidc.js`: idempotent DDL for `oauth_application`, `oauth_access_token`, `oauth_consent`, and `jwks` tables. Added `db:migrate-oidc` and `db:seed-client` npm scripts.

**Phase 3** — Created `scripts/seed-public-client.js`: upserts the book app as a public client (no secret, PKCE only). Respects `BOOK_CLIENT_ID` and `BOOK_REDIRECT_URIS` env vars.

**Phase 4** — Updated `getSessionFromRequest()` to accept `Authorization: Bearer` header in addition to cookies. Added `POST /api/admin/clients/register` (admin-only, generates clientId/clientSecret, inserts into oauth_application).

**Phase 5a** — Created `book/src/lib/oauth.ts`: PKCE helpers (generateCodeVerifier, generateCodeChallenge), buildAuthorizationUrl (stores verifier in sessionStorage), exchangeCodeForTokens (no client_secret), refreshAccessToken, getUserInfo, storeTokens/clearTokens, validateState.

**Phase 5b** — Created `book/src/pages/auth/callback.tsx`: extracts code+state, validates CSRF state, retrieves PKCE verifier, exchanges for tokens, stores in localStorage, redirects to intended route.

**Phase 5c** — Rewrote `AuthContext.tsx`: refreshSession() reads access_token from localStorage → userinfo endpoint → auto-refreshes with refresh_token; signIn() → PKCE redirect; signOut() → clears localStorage; signUpWithProfile() creates account then OAuth redirect; added handleOAuthCallback() for the callback page. Session object is synthetic (backwards-compatible).

**Phase 5d** — Updated LoginForm and SignUpForm: detect "OAuth relay mode" (URL has client_id + code_challenge), do direct credential auth via POST, preserve all PKCE/OAuth params, redirect back to auth server's authorize endpoint. Standalone mode unchanged.

**Phase 6** — Rewrote BetterAuthClient in `backend/src/api/auth.py`: `validate_bearer_token()` tries OIDC userinfo first (OAuth access tokens), falls back to legacy session-cookie endpoint for opaque tokens. `get_optional_user()` dependency updated to call `validate_bearer_token`.

## Outcome

- ✅ Impact: Full OAuth 2.1/OIDC + PKCE auth system implemented across auth-server, book frontend, and backend. Backwards compatible with existing cookie sessions during migration.
- 🧪 Tests: Syntax checks pass. Full E2E test requires running services and DB migration.
- 📁 Files: 13 files created/modified across auth-server, book, and backend
- 🔁 Next prompts: Run `npm run db:migrate-oidc` and `npm run db:seed-client` in auth-server to set up DB. Then test E2E PKCE flow.
- 🧠 Reflection: The OAuth relay pattern in LoginForm/SignUpForm (preserving PKCE params through the auth server's login-page redirect) is the most fragile part — monitor for "code verification failed" errors in production.

## Evaluation notes (flywheel)

- Failure modes observed: Uint8Array iteration in oauth.ts (fixed — use index loop not for-of); ChatKitWidget had wrong AuthContext import path (fixed)
- Graders run and results (PASS/FAIL): syntax checks PASS, tsc no new logic errors PASS
- Prompt variant (if applicable): better-auth-setup skill
- Next experiment: Test OIDC discovery endpoint after running DB migration
