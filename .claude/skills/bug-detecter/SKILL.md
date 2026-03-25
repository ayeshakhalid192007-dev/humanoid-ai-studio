---
name: bug-detecter
description: Detects bugs in Better Auth + OAuth 2.1 PKCE login flows. Use this skill when the user reports login failures, "page not found" on auth routes, sign-up/sign-in not working, token issues, or CORS/session errors in a Better Auth + Docusaurus + FastAPI stack. Runs a static analysis script and matches symptoms against a curated bug reference.
---

# Bug Detecter — Login & Better Auth

Diagnoses configuration and code bugs that prevent successful login in a Better Auth +
OAuth 2.1 PKCE + Docusaurus frontend stack. Combines static file analysis with a
curated reference of known failure patterns.

## Detection Workflow

### Step 1 — Run the static analysis script

```bash
python3 .claude/skills/engineering/bug-detecter/scripts/detect_login_bugs.py <project_root>
```

Pass the monorepo root as `project_root`. The script auto-locates and checks:
- `auth.js` / `auth.ts` — Better Auth config
- `docusaurus.config.js` — frontend config
- `AuthContext.tsx` — auth state + token handling
- `oauth.ts` / `oauth.js` — PKCE utilities
- `.env` — auth server environment

Read the output — each `❌` line includes a suggested fix.

### Step 2 — Cross-reference the bug reference

Load `references/better-auth-login-bugs.md` to look up symptoms in detail.
Each entry contains: symptom, root cause, and exact fix.

Categories covered:
1. OAuth / OIDC flow bugs (loginPage URL, redirect_uri mismatch, PKCE issues)
2. Docusaurus baseUrl bugs (pages 404 in browser but 200 from curl)
3. Better Auth session bugs (CORS, bearer plugin, token refresh)
4. Sign-up bugs (password hash mismatch, profile save after signup)
5. Rate limiting bugs (legitimate logins blocked)
6. Environment / config bugs (wrong DB, missing secret, URL mismatch)

### Step 3 — Inspect specific files

For bugs not caught by the script, read these files and check:

| File | What to check |
|------|--------------|
| `auth-server/src/auth.js` | `loginPage` is full frontend URL, `trustedClients.redirectUrls` matches frontend, `trustedOrigins` includes frontend origin |
| `book/docusaurus.config.js` | `baseUrl` uses `process.env.BASE_URL \|\| '/'`, `oauthRedirectUri` matches auth server `redirectUrls` |
| `book/src/context/AuthContext.tsx` | `signIn()` redirects to auth server OAuth endpoint, `handleOAuthCallback()` exchanges code for tokens |
| `book/src/lib/oauth.ts` | PKCE verifier stored BEFORE redirect, state nonce stored BEFORE redirect, `validateState()` present |
| `book/src/pages/auth/callback.tsx` | Reads `code`+`state` from URL, calls `handleOAuthCallback`, redirects on success |
| `auth-server/.env` | `BETTER_AUTH_SECRET` ≥32 chars, `BETTER_AUTH_URL` matches running port, `FRONTEND_URL` set |

### Step 4 — Validate the full OAuth flow end-to-end

```bash
# 1. Auth server healthy
curl http://localhost:3002/health

# 2. OAuth authorize redirects to FRONTEND login page (not auth server 404)
curl -sv "http://localhost:3002/api/auth/oauth2/authorize?client_id=physical-ai-book&redirect_uri=http://localhost:3000/auth/callback&response_type=code&scope=openid&state=test&code_challenge=E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM&code_challenge_method=S256" 2>&1 | grep "location:"
# Expected: location: http://localhost:3000/auth/login?...

# 3. Frontend login and callback pages load (not 404)
curl -o /dev/null -w "%{http_code}" http://localhost:3000/auth/login   # → 200
curl -o /dev/null -w "%{http_code}" http://localhost:3000/auth/callback # → 200
```

**Diagnosis:**
- Step 2 shows `location: http://localhost:3002/auth/login` → `loginPage` bug in `auth.js`
- Step 3 returns 200 from curl but browser shows 404 → `baseUrl` bug in `docusaurus.config.js`

## Most Common Fixes (Quick Reference)

| Bug | File | Fix |
|-----|------|-----|
| `loginPage` points to auth server | `auth-server/src/auth.js` | `loginPage: \`\${process.env.FRONTEND_URL}/auth/login\`` |
| Pages 404 in browser (not curl) | `book/docusaurus.config.js` | `baseUrl: process.env.BASE_URL \|\| '/'` |
| `redirect_uri_mismatch` | `auth-server/src/auth.js` | Match `redirectUrls` to `oauthRedirectUri` exactly |
| 401 on API calls after login | `auth-server/src/auth.js` | Add `bearer()` to plugins array |
| Session lost cross-origin | `AuthContext.tsx` + `auth.js` | `credentials: 'include'` in fetches + `cors({ credentials: true })` |
| PKCE verifier missing | `book/src/lib/oauth.ts` | Store verifier in sessionStorage BEFORE redirect |
| Users always re-onboarded | `auth-server/src/auth.js` | Verify `getAdditionalUserInfoClaim` returns `onboardingCompleted` |
