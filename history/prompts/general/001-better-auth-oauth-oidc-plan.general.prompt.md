---
id: "001"
title: Better Auth OAuth OIDC Implementation Plan
stage: general
date: 2026-03-23
surface: agent
model: claude-sonnet-4-6
feature: none
branch: main
user: ayeshakhalid
command: /better-auth-setup
labels: ["auth","oauth","oidc","pkce","planning","better-auth"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - auth-server/src/auth.js (planned modification)
  - auth-server/src/index.js (planned modification)
  - auth-server/scripts/seed-public-client.js (planned new file)
  - book/src/lib/oauth.ts (planned new file)
  - book/src/pages/auth/callback.tsx (planned new file)
  - book/src/context/AuthContext.tsx (planned modification)
tests:
  - OIDC discovery endpoint validation
  - PKCE end-to-end flow
  - Bearer token userinfo validation
---

## Prompt

use this skill and make a plan to implement the better auth authentication system in my project

## Response snapshot

Produced a 7-phase implementation plan to add OAuth 2.1 / OIDC with PKCE to the existing Better Auth v1.2.0 setup. Current state uses cookie-based direct auth; target is token-based OAuth flow via the book SPA as a public client.

Phases:
1. Auth Server — add oidcProvider + jwt plugins (RS256/JWKS)
2. Database migration for OIDC tables (oauth_application, oauth_access_token, oauth_consent, jwks)
3. Seed public client for book frontend (no secret, PKCE only)
4. Admin-only client registration endpoint
5. Book frontend — PKCE utilities, callback page, AuthContext overhaul, login form PKCE preservation
6. Backend — switch from cookie session validation to Bearer token / userinfo
7. Security hardening

## Outcome

- ✅ Impact: Full OAuth 2.1/OIDC architecture plan with phased rollout, no unrelated changes
- 🧪 Tests: 9 acceptance criteria defined (OIDC discovery, JWKS, PKCE flow, userinfo, profile, backend, sign out, admin endpoint)
- 📁 Files: Plan only — no files modified yet
- 🔁 Next prompts: Implement Phase 1 (auth.js OIDC plugins), then Phase 2 (DB migration)
- 🧠 Reflection: Key risk is the frontend cookie-to-token cutover (Phase 5c/5d) — must ensure profile endpoints accept Bearer tokens BEFORE switching frontend

## Evaluation notes (flywheel)

- Failure modes observed: none (planning stage)
- Graders run and results (PASS/FAIL): none
- Prompt variant (if applicable): better-auth-setup skill
- Next experiment: implement Phase 1 and validate OIDC discovery endpoint
