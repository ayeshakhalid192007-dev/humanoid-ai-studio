# Better Auth & Login Bug Reference

## 1. OAuth / OIDC Flow Bugs

### loginPage / consentPage points to auth server (not frontend)
**Symptom:** After credential auth, browser gets a 404 or blank page instead of the login form.
**Cause:** `oidcProvider({ loginPage: "/auth/login" })` resolves relative to the auth server URL (e.g. `http://localhost:3002/auth/login`). The auth server serves no HTML at that path.
**Fix:** Use the full frontend URL: `loginPage: \`\${process.env.FRONTEND_URL}/auth/login\``

### redirectUri mismatch
**Symptom:** `redirect_uri_mismatch` error from the auth server after login.
**Cause:** The `redirect_uri` in the PKCE request doesn't exactly match what's registered in `trustedClients[].redirectUrls`.
**Check:** Compare `oauthRedirectUri` in frontend config vs `BOOK_REDIRECT_URIS` env var and `trustedClients` in auth.js.

### PKCE code_verifier missing
**Symptom:** "PKCE code verifier missing. Please start the login flow again."
**Cause:** `sessionStorage` was cleared between the authorize redirect and the callback page load, or the user opened the callback URL in a new tab.
**Fix:** Ensure the PKCE flow starts and completes in the same browser tab/session.

### State parameter invalid (CSRF check fails)
**Symptom:** "Invalid state parameter — possible CSRF attack."
**Cause:** `oauth_state` in sessionStorage doesn't match the `state` returned in the callback. Happens when state is stored after redirect instead of before, or sessionStorage is partitioned.
**Fix:** Store state in sessionStorage before redirecting to the auth server.

---

## 2. Docusaurus baseUrl Bugs

### Pages return 404 in React but 200 from curl
**Symptom:** Visiting `/auth/login` shows "page not found" in the browser even though the file exists at `src/pages/auth/login.tsx`.
**Cause:** Docusaurus `baseUrl` is set to `/some-path/`, so the page is actually at `/some-path/auth/login`. The React router doesn't match `/auth/login`.
**Fix:** Use `baseUrl: process.env.BASE_URL || '/'` in `docusaurus.config.js`. Set `BASE_URL=/some-path/` only in production/CI.

### Hardcoded redirect URIs don't include baseUrl
**Symptom:** OAuth callback lands on a 404 page after successful auth.
**Cause:** `oauthRedirectUri` is set to `http://localhost:3000/auth/callback` but the actual page is at `http://localhost:3000/some-path/auth/callback` due to baseUrl.
**Fix:** Keep baseUrl as `/` locally so all routes match without prefix.

---

## 3. Better Auth Session Bugs

### Session cookie not sent cross-origin (CORS/credentials)
**Symptom:** Login POST succeeds (200) but subsequent protected requests get 401.
**Cause:** `credentials: "include"` missing on fetch, or the auth server CORS config doesn't include `credentials: true`.
**Check:**
- Frontend fetches use `credentials: "include"` for cookie-based auth
- Auth server: `cors({ credentials: true, origin: allowedOrigins })`
- `trustedOrigins` in betterAuth config includes the frontend origin

### Bearer token rejected by auth server
**Symptom:** Requests with `Authorization: Bearer <token>` return 401 even with a valid token.
**Cause:** `bearer()` plugin not included in Better Auth plugins array.
**Fix:** Add `bearer()` to the plugins list in auth.js.

### Access token expired — refresh not triggered
**Symptom:** User gets logged out unexpectedly or API calls fail after a few hours.
**Cause:** Access token expires but the frontend doesn't attempt a refresh before giving up.
**Check:** `refreshSession()` in AuthContext must catch 401 errors and call `refreshAccessToken()` before clearing the session.

### `onboardingCompleted` field not returned in userinfo
**Symptom:** Users are redirected to onboarding after every login.
**Cause:** `getAdditionalUserInfoClaim` in oidcProvider not returning the field, or the field name casing is wrong.
**Fix:** Ensure `additionalFields` in betterAuth user config and `getAdditionalUserInfoClaim` both use the same camelCase field name.

---

## 4. Sign-Up Bugs

### Sign-up succeeds but user can't log in
**Symptom:** Account is created but credentials fail on login.
**Cause:** Password hash function used on sign-up differs from the verify function (e.g. bcrypt vs PBKDF2).
**Check:** The `hash` and `verify` functions in `emailAndPassword.password` must be symmetric — same algorithm and parameters.

### Profile save fails silently after sign-up
**Symptom:** User completes sign-up but profile/onboarding data is lost.
**Cause:** Profile POST uses `credentials: "include"` (cookie) but the cookie isn't set yet because the browser hasn't received it from the sign-up response.
**Fix:** Use the access token (from OAuth exchange) to authenticate the profile POST instead of relying on the session cookie.

---

## 5. Rate Limiting Bugs

### Legitimate logins blocked by rate limiter
**Symptom:** After a few login attempts, all requests return 429 even with correct credentials.
**Cause:** Rate limit key is based on IP only — shared IPs (NAT, proxies) hit limits for unrelated users.
**Check:** Rate limit key should combine IP + endpoint, not IP alone. Ensure `RATE_LIMIT_MAX` is sensible (not too low).

---

## 6. Environment / Config Bugs

### Auth server uses wrong database
**Symptom:** Users exist in one environment but not another; sessions don't persist.
**Cause:** `DATABASE_URL` and `NEON_DATABASE_URL` both present — auth.js uses `DATABASE_URL || NEON_DATABASE_URL`. If one is stale, the wrong DB is used.
**Fix:** Use a single canonical env var and verify in health check.

### `BETTER_AUTH_SECRET` missing or too short
**Symptom:** Sessions fail to verify; JWT signing errors in logs.
**Cause:** Secret not set in `.env`, or the secret is less than 32 characters.
**Fix:** Generate a 32+ char random secret: `openssl rand -hex 32`

### `BETTER_AUTH_URL` doesn't match actual server URL
**Symptom:** Cookie domain/path mismatch; tokens reference wrong issuer.
**Cause:** `BETTER_AUTH_URL` set to a different host/port than where the server is actually running.
**Fix:** Ensure `BETTER_AUTH_URL` exactly matches the origin the auth server is served from.
