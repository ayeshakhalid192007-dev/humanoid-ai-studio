# Implementation Plan: OAuth Social Login (Google & GitHub)

**Branch**: `feature/oauth-google-github` | **Date**: 2026-03-24 | **Spec**: [spec.md](./spec.md)
**Base branch**: `main`

---

## Summary

Add Google and GitHub social login to the existing Better Auth stack. Better Auth (`^1.2.0`) has built-in `socialProviders` support — enabling Google and GitHub is a single config block in `auth.js`. The frontend adds social buttons to the login/signup forms; clicking one triggers a Better Auth social sign-in that routes through the existing PKCE/OIDC flow so the callback page, token storage, and session logic require no changes.

---

## Technical Context

**Language/Version**: Node.js ≥18 (auth-server), TypeScript/React (book frontend)
**Auth Library**: Better Auth `^1.2.0` — already installed, has built-in `socialProviders` support
**Database**: Neon Postgres — `account` table already stores `provider` + `providerAccountId`; **zero schema migration needed**
**Token Strategy**: OAuth 2.1 PKCE — access token (6 h) + refresh token (7 d) stored in localStorage
**Frontend**: Docusaurus 3 + React 18
**No new npm/pip packages required**

---

## 1. Branch Strategy

| Item | Value |
|------|-------|
| Branch name | `feature/oauth-google-github` (**already created and checked out**) |
| Base branch | `main` |

No branch action needed — the working branch already exists.

---

## 2. Dependencies to Install

**None.** `better-auth ^1.2.0` includes social provider support natively via the `socialProviders` top-level config key. No additional packages are required for auth-server or the frontend.

---

## 3. Environment Variables

### `auth-server/.env` (and `.env.example`)

```
# Google OAuth — register app at https://console.developers.google.com
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# GitHub OAuth — register app at https://github.com/settings/developers
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

### OAuth App Registration Settings (for reference, not code)

**Google** — Authorized redirect URI:
```
http://localhost:3002/api/auth/callback/google         ← development
https://<your-auth-server>/api/auth/callback/google    ← production
```

**GitHub** — Authorization callback URL:
```
http://localhost:3002/api/auth/callback/github         ← development
https://<your-auth-server>/api/auth/callback/github    ← production
```

No frontend env vars are needed — the frontend only calls the auth server's existing endpoints.

---

## 4. Database / Schema Changes

**No migration required.**

The existing `account` table (created and managed by Better Auth) already has all needed columns:

```sql
-- Already exists — no ALTER TABLE needed
account (
  id              TEXT  PRIMARY KEY,
  userId          TEXT  REFERENCES user(id),
  providerId      TEXT,   -- will store "google" or "github"
  accountId       TEXT,   -- will store provider's user ID
  accessToken     TEXT,
  refreshToken    TEXT,
  expiresAt       TIMESTAMPTZ,
  ...
)
```

Better Auth's social providers write into `providerId` and `accountId` automatically. Email-based deduplication and account linking is handled by Better Auth's built-in `linkAccounts` behaviour.

---

## 5. Backend Changes — File by File

### 5.1 `auth-server/src/auth.js` — **MODIFY**

**What changes:** Add `socialProviders` block to the `betterAuth({...})` config object.

**Where:** After the closing brace of `emailAndPassword`, before `session`, or anywhere at the top level of the config.

**Exact diff:**

```js
// ADD this block inside betterAuth({...}):
socialProviders: {
  google: {
    clientId: process.env.GOOGLE_CLIENT_ID,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET,
  },
  github: {
    clientId: process.env.GITHUB_CLIENT_ID,
    clientSecret: process.env.GITHUB_CLIENT_SECRET,
  },
},
```

**What this enables automatically (no other code changes in auth-server):**

| New Route | Purpose |
|-----------|---------|
| `GET /api/auth/sign-in/social/google` | Initiates Google OAuth redirect |
| `GET /api/auth/sign-in/social/github` | Initiates GitHub OAuth redirect |
| `POST /api/auth/sign-in/social` | Accepts `{ provider, callbackURL }` JSON body; returns redirect URL |
| `GET /api/auth/callback/google` | Google callback — exchanges code, creates/finds user |
| `GET /api/auth/callback/github` | GitHub callback — exchanges code, creates/finds user |

Better Auth automatically:
- Creates a new `user` row on first social login (email, name, image from provider)
- Uses GitHub's `login` as name fallback if `name` is null
- Links to an existing account if the provider email matches an existing `user.email`
- Writes `provider` + `providerAccountId` into the `account` table
- Sets `user.image` from the provider's avatar URL
- Leaves `role` = `"student"` and `onboardingCompleted` = `false` on new accounts (default values)

### 5.2 `auth-server/.env.example` — **MODIFY** (or CREATE if absent)

Add the four new variables with placeholder values (shown in Section 3 above).

---

## 6. Frontend Changes — File by File

### Architecture: How Social Auth Connects to Existing PKCE Flow

The social auth flow is designed to **reuse the entire existing PKCE/OIDC infrastructure** — the `/auth/callback` page, `handleOAuthCallback`, and token storage all work unchanged.

```
User clicks "Continue with Google"
        │
        ▼
signInWithSocial("google")          [AuthContext.tsx — new method]
  1. Generate PKCE verifier + challenge
  2. Store verifier in sessionStorage (existing PKCE_VERIFIER_KEY)
  3. Build OIDC authorize URL with challenge:
     AUTH_API_URL/api/auth/oauth2/authorize?client_id=...&code_challenge=...&state=...
  4. POST AUTH_API_URL/api/auth/sign-in/social
       body: { provider: "google", callbackURL: <oidcAuthorizeUrl> }
  5. Navigate to returned Google redirect URL
        │
        ▼
Google OAuth consent screen
        │
        ▼
GET /api/auth/callback/google       [auth-server — Better Auth handles]
  - Exchanges Google code for Google tokens
  - Creates/links user + session
  - Redirects to callbackURL = OIDC authorize URL (with active session cookie)
        │
        ▼
GET /api/auth/oauth2/authorize?...  [auth-server — Better Auth OIDC plugin handles]
  - Sees valid session cookie
  - Validates PKCE challenge
  - Issues platform auth code
  - Redirects to redirect_uri: /auth/callback?code=...&state=...
        │
        ▼
/auth/callback page                 [existing — ZERO changes needed]
  - Validates state
  - Exchanges code for access + refresh tokens
  - Stores in localStorage
  - Redirects to /dashboard (or /auth/onboarding if first-time user)
```

**Why this approach:** The social auth leverages the auth server as a relay — it's already an OIDC provider. The PKCE flow guarantees the frontend gets platform tokens identical to those from email/password login, so the rest of the app behaves identically regardless of auth method. No new callback pages or token handling paths are introduced.

---

### 6.1 `book/src/context/AuthContext.tsx` — **MODIFY**

**What changes:**
1. Add `signInWithSocial(provider: 'google' | 'github'): Promise<void>` to the `AuthContextType` interface
2. Implement `signInWithSocial` inside `AuthProvider`

**Interface addition:**
```ts
signInWithSocial: (provider: 'google' | 'github') => Promise<void>;
```

**Implementation:**
```ts
const signInWithSocial = useCallback(async (provider: 'google' | 'github') => {
  // Build the PKCE authorize URL — this is the callbackURL for Better Auth social sign-in.
  // After social auth, Better Auth redirects to this URL. The auth server sees the
  // active session and issues a platform PKCE code, completing the token flow.
  const { url: authorizeUrl } = await buildAuthorizationUrl({
    authServerUrl: AUTH_API_URL,
    clientId: CLIENT_ID,
    redirectUri: REDIRECT_URI,
    scope: "openid email profile",
  });

  // Call Better Auth social sign-in — returns the provider redirect URL
  const resp = await fetch(`${AUTH_API_URL}/api/auth/sign-in/social`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ provider, callbackURL: authorizeUrl }),
  });

  if (!resp.ok) {
    throw new Error("Failed to initiate social sign-in");
  }

  const data = await resp.json();
  const redirectUrl: string = data.url ?? data.redirect ?? data.redirectTo;

  if (!redirectUrl) {
    throw new Error("No redirect URL returned from auth server");
  }

  // Navigate to provider's OAuth consent screen
  window.location.href = redirectUrl;
}, [AUTH_API_URL, CLIENT_ID, REDIRECT_URI]);
```

**Context value:** Add `signInWithSocial` to the returned context value object.

---

### 6.2 `book/src/components/Auth/LoginForm.tsx` — **MODIFY**

**What changes:** Add social login buttons above the email/password form fields. Wire up `signInWithSocial` from `useAuth()`.

**Where:** Inside the `<form>` element, between the title/subtitle and the first `<div className={styles.inputGroup}>`.

**Visual structure to add:**
```tsx
{/* Social login buttons */}
<div className={styles.socialButtons}>
  <button
    type="button"
    onClick={() => signInWithSocial('google')}
    className={styles.socialButton}
    disabled={isLoading}
  >
    <svg ...googleIcon... />
    Continue with Google
  </button>
  <button
    type="button"
    onClick={() => signInWithSocial('github')}
    className={styles.socialButton}
    disabled={isLoading}
  >
    <svg ...githubIcon... />
    Continue with GitHub
  </button>
</div>

<div className={styles.divider}>
  <span>or sign in with email</span>
</div>

{/* existing email/password fields unchanged below */}
```

**OAuth relay mode consideration:** In relay mode (when `isOAuthRelay` is true), the social buttons should also work. `signInWithSocial` already generates fresh PKCE params — the relay's original PKCE params are irrelevant for social login. No special-casing needed.

**Error handling:** Wrap `signInWithSocial` call in try/catch; display error via existing `setError` state.

---

### 6.3 `book/src/components/Auth/SignUpForm.tsx` — **MODIFY**

**What changes:** Same social buttons as LoginForm, placed above the account information fields.

**Where:** After the title/subtitle, before the "Account Information" section.

**Visual structure:** Identical to LoginForm — `socialButtons` div with Google and GitHub buttons, followed by `divider`.

**Note:** The buttons on the signup form behave identically to the login form — Better Auth handles the "new user vs existing user" distinction server-side via email matching.

---

### 6.4 `book/src/components/Auth/Auth.module.css` — **MODIFY**

**New CSS classes to add:**

```css
/* Social login buttons container */
.socialButtons {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

/* Individual social login button */
.socialButton {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.625rem;
  width: 100%;
  padding: 0.625rem 1rem;
  border: 1px solid var(--ifm-color-emphasis-300);
  border-radius: 6px;
  background: var(--ifm-background-color);
  color: var(--ifm-font-color-base);
  font-size: 0.9375rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}

.socialButton:hover:not(:disabled) {
  background: var(--ifm-color-emphasis-100);
  border-color: var(--ifm-color-emphasis-500);
}

.socialButton:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* "or sign in with email" divider */
.divider {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 1rem 0;
  color: var(--ifm-color-emphasis-500);
  font-size: 0.8125rem;
}

.divider::before,
.divider::after {
  content: "";
  flex: 1;
  height: 1px;
  background: var(--ifm-color-emphasis-300);
}
```

---

### 6.5 Files that do NOT need changes

| File | Reason |
|------|--------|
| `book/src/pages/auth/callback.tsx` | Already handles PKCE code exchange correctly — social flow ends there unchanged |
| `book/src/lib/oauth.ts` | `buildAuthorizationUrl` is reused as-is by `signInWithSocial` |
| `book/src/context/AuthContext.tsx` — `handleOAuthCallback` | Not touched — social flow ends at the existing PKCE callback |
| `backend/src/api/auth.py` | FastAPI validates tokens via `/api/auth/oauth2/userinfo` — social tokens are identical to email tokens |
| `auth-server/src/index.js` | Better Auth's `toNodeHandler` already handles all `/api/auth/*` routes including new social routes |
| All database migration scripts | No schema changes needed |

---

## 7. Potential Risks & Edge Cases

### Risk 1 — `callbackURL` validation in Better Auth
**Risk:** Better Auth may validate the social sign-in `callbackURL` against `trustedOrigins`. The callbackURL used here is the auth server's own OIDC authorize URL (`http://localhost:3002/api/auth/oauth2/authorize?...`). Since `http://localhost:3002` is already in `trustedOrigins`, this should pass.

**Mitigation:** If Better Auth rejects a same-server callbackURL, fall back to a two-step approach: set callbackURL to `{FRONTEND_URL}/auth/social-callback`, add a thin new page there that reads the sessionStorage PKCE verifier and redirects to the OIDC authorize URL. This is a contained 20-line change.

**Detection:** Test in local dev before any other steps. If Better Auth returns a 400 on the social sign-in POST, this is the cause.

---

### Risk 2 — Account already exists with same email (different provider)
**Behavior:** Better Auth automatically links the incoming social account to the existing `user` row by email. The existing `account` table gets a new row with the new `provider`, and the `user` record is unchanged.

**Edge case:** A user who signed up with email/password tries Google with the same email → they get logged in, no duplicate. Their existing password still works too.

**No action required** — Better Auth handles this natively.

---

### Risk 3 — GitHub private email (no email returned)
**Behavior:** GitHub API may return `null` for email if the user has set their email to private.

**Better Auth behaviour:** If no email is returned, Better Auth cannot create a user (email is the identity key). It will redirect to the error callback URL with `error=no_email`.

**Mitigation:** The frontend callback page already handles `?error=...` params — it displays the error message. Add a user-friendly message: *"We couldn't retrieve your email from GitHub. Please make your GitHub email public or use email/password signup."*

**Where to add:** `book/src/pages/auth/callback.tsx` — in the existing `error` block, add a check for `error === "no_email"` and display the specific message.

---

### Risk 4 — OAuth cancellation / state mismatch
**Behaviour:** If the user cancels on Google/GitHub, the provider redirects back to `/api/auth/callback/google?error=access_denied`. Better Auth then redirects to the error callback URL.

**Current callback page:** Already handles `?error=...` params (lines 43–47 of `callback.tsx`) — shows error message with "Back to Login" button.

**No code change needed.** The existing error path handles this correctly.

---

### Risk 5 — Onboarding redirect for first-time social users
**Behaviour:** First-time social signup creates a user with `onboardingCompleted = false`. After PKCE token exchange, `getUserInfo` returns `onboardingCompleted: false`. `AuthContext` already exposes `needsOnboarding = !user.onboardingCompleted`. The `/dashboard` page (or `Root.tsx`) already checks this and redirects to `/auth/onboarding`.

**No code change needed.** The existing onboarding gate handles social users automatically.

---

### Risk 6 — Existing email/password flow regression
**Risk:** Adding `socialProviders` to `auth.js` is purely additive — it does not touch `emailAndPassword`, session config, or any existing plugin. No existing route changes.

**Verification:** Run the existing email/password login and signup flows first in testing.

---

## 8. Testing Checklist

### Pre-flight (before writing any code)
- [ ] `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` set in `auth-server/.env` (real dev credentials)
- [ ] `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET` set in `auth-server/.env`
- [ ] Google OAuth app has `http://localhost:3002/api/auth/callback/google` as authorized redirect URI
- [ ] GitHub OAuth app has `http://localhost:3002/api/auth/callback/github` as callback URL

### Auth Server Smoke Tests
- [ ] `GET http://localhost:3002/api/auth/sign-in/social/google` → redirects to Google (302)
- [ ] `GET http://localhost:3002/api/auth/sign-in/social/github` → redirects to GitHub (302)
- [ ] `POST http://localhost:3002/api/auth/sign-in/social` with `{ provider: "google", callbackURL: "..." }` → returns `{ url: "https://accounts.google.com/..." }`

### New User Social Signup — Google
- [ ] Click "Continue with Google" on `/auth/signup`
- [ ] Google consent screen appears
- [ ] After consent: land on `/auth/onboarding` (first-time user)
- [ ] Complete onboarding → land on `/dashboard` as authenticated
- [ ] Check Neon DB: one new `user` row, one `account` row with `providerId = "google"`

### New User Social Signup — GitHub
- [ ] Click "Continue with GitHub" on `/auth/signup`
- [ ] GitHub authorization screen appears
- [ ] After authorization: land on `/auth/onboarding`
- [ ] Complete onboarding → land on `/dashboard`

### Returning Social User Login
- [ ] Sign out → click "Continue with Google" on `/auth/login`
- [ ] After Google → land directly on `/dashboard` (no onboarding shown)
- [ ] Tokens visible in localStorage (`physical_ai_access_token`, `physical_ai_refresh_token`)

### Account Deduplication
- [ ] Sign up with email/password using `test@example.com`
- [ ] Sign out
- [ ] Click "Continue with Google" using the same `test@example.com` Google account
- [ ] Verify: lands on dashboard, no duplicate user in DB (check `user` table count)

### OAuth Cancellation
- [ ] Click "Continue with Google" → click "Cancel" on Google consent screen
- [ ] Verify: redirected to `/auth/login` (or `/auth/signup`) with error message shown

### Existing Email/Password Flow — Regression
- [ ] Email/password signup still creates account and redirects to onboarding
- [ ] Email/password login still works and redirects to dashboard
- [ ] Profile save (`/api/profile`) still works after email/password auth

### Edge Cases
- [ ] GitHub login with private email → user sees friendly error message (not a crash)
- [ ] Refresh page while logged in via social → session persists (token refresh works)
- [ ] Social login buttons visible on both `/auth/login` and `/auth/signup`
- [ ] Social login buttons work at mobile viewport (320px width)

---

## 9. Implementation Order (for execution)

1. **`auth-server/src/auth.js`** — add `socialProviders` block (5 lines)
2. **`auth-server/.env.example`** — add 4 new env vars
3. Set real credentials in `auth-server/.env` and smoke-test auth server routes
4. **`book/src/context/AuthContext.tsx`** — add `signInWithSocial` method
5. **`book/src/components/Auth/Auth.module.css`** — add social button styles
6. **`book/src/components/Auth/LoginForm.tsx`** — add social buttons
7. **`book/src/components/Auth/SignUpForm.tsx`** — add social buttons
8. End-to-end test all scenarios in Section 8

---

## Project Structure (artifacts for this feature)

```
specs/1-oauth-social-login/
├── spec.md           ← requirements (complete)
├── plan.md           ← this file
└── checklists/       ← spec quality checklist (complete)
```

No `data-model.md` or `contracts/` needed — no new API contracts or entities; Better Auth handles the social provider routes internally.
