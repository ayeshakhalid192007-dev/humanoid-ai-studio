---
id: "003"
title: Better Auth Bug Detection & Fix Plan
stage: general
date: 2026-03-23
surface: agent
model: claude-sonnet-4-6
feature: none
branch: main
user: ayeshakhalid
command: /bug-detecter use this skill and create a plan to fix the bugs of better auth integration
labels: ["better-auth","oauth","pkce","bug-detection","fix-plan","security"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - auth-server/src/auth.js
  - auth-server/src/index.js
  - book/src/context/AuthContext.tsx
  - book/src/pages/auth/callback.tsx
  - book/src/lib/oauth.ts
  - book/src/components/Auth/LoginForm.tsx
  - book/src/components/Auth/SignUpForm.tsx
  - book/docusaurus.config.js
  - auth-server/scripts/create-profiles-table.js
tests:
  - none
---

## Prompt

use this skill and create a plan to fix the bugs of better auth integration

## Response snapshot

Ran full static inspection of the Better Auth + OAuth 2.1 PKCE stack (auth-server + Docusaurus frontend).
Found 5 bugs across 4 files. No issues in auth.js (loginPage, redirectUrls, bearer plugin all correct) or oauth.ts (PKCE verifier stored before redirect, state validated).

**Bugs found:**

| # | Severity | File | Issue |
|---|----------|------|-------|
| 1 | CRITICAL | AuthContext.tsx:362 | signOut() never calls /api/auth/sign-out — server session persists after logout |
| 2 | HIGH | index.js:23 | Pool uses NEON_DATABASE_URL only; auth.js uses DATABASE_URL \|\| NEON_DATABASE_URL — can hit different DBs |
| 3 | HIGH | AuthContext.tsx:329 + SignUpForm.tsx:131 | Profile save POST uses credentials:include (cookie) without Bearer token — silently fails cross-origin in production |
| 4 | MEDIUM | callback.tsx:61 | useEffect deps array is [] but closes over handleOAuthCallback, history, location |
| 5 | LOW | SignUpForm.tsx:335 | Dropdown missing "none" option; server accepts it, DB enforces it |

**Recommended fix order:** Bug 2 → Bug 3 → Bug 1 → Bug 5 → Bug 4

## Outcome

- ✅ Impact: Full audit of Better Auth integration; 5 actionable bugs identified with exact file:line references and code-level fixes
- 🧪 Tests: No tests run (static analysis only)
- 📁 Files: 9 files inspected, 0 modified
- 🔁 Next prompts: "implement the better auth bug fixes", "fix bug 2 first"
- 🧠 Reflection: Most bugs are production-only failures (cross-origin cookies, dual DB pool) invisible in local dev — important to catch before deployment

## Evaluation notes (flywheel)

- Failure modes observed: Static analysis script was missing from skills/engineering/bug-detecter (only existed in git status snapshot but not on disk) — fell back to manual file inspection per skill Step 3
- Graders run and results (PASS/FAIL): N/A (plan only)
- Prompt variant (if applicable): N/A
- Next experiment: Add runtime validation (Step 4 curl checks) against a running dev server to confirm Bug 2 manifests
