# Tasks: OAuth Social Login (Google & GitHub)

**Input**: `specs/1-oauth-social-login/` — spec.md + plan.md
**Branch**: `feature/oauth-google-github`
**Date**: 2026-03-24
**Status**: Implementation complete — E2E verification pending

> Tasks marked `[X]` are complete (implemented in the current branch).
> Tasks marked `[ ]` are outstanding (E2E testing and manual verification required).

---

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Parallelizable (different files, no pending dependencies)
- **[US?]**: User story this task belongs to
- **[X]**: Completed

---

## Phase 1: Setup

**Purpose**: Confirm environment is ready — no new packages or schema changes needed.

- [X] T001 Confirm branch `feature/oauth-google-github` is active (was pre-created)
- [X] T002 Verify no new npm/pip packages required — Better Auth `^1.2.0` has native `socialProviders` support (zero installs)
- [X] T003 Verify no database migration required — `account` table already has `providerId` + `accountId` columns

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Auth server config and environment vars — MUST complete before frontend work.

**⚠️ CRITICAL**: Frontend social buttons cannot work until T004 is complete.

- [X] T004 Add `socialProviders` block (Google + GitHub) to `auth-server/src/auth.js` — registers `/api/auth/sign-in/social`, `/api/auth/callback/google`, `/api/auth/callback/github` automatically
- [X] T005 [P] Create `auth-server/.env.example` with placeholder values for `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`
- [X] T006 Confirm `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET` are set in `auth-server/.env` with real dev credentials

**Checkpoint**: Auth server social routes are live. Verify with:
```
GET http://localhost:3002/api/auth/sign-in/social/google → 302 redirect to Google
GET http://localhost:3002/api/auth/sign-in/social/github → 302 redirect to GitHub
```

---

## Phase 3: User Stories 1 & 2 — Social Signup (Google + GitHub) (Priority: P1) 🎯 MVP

**Goal**: New users can register via Google or GitHub on both login and signup pages.

**Independent Test (US1)**: Click "Continue with Google" on `/auth/signup` → Google consent screen → land on `/auth/onboarding` as a new authenticated user.

**Independent Test (US2)**: Click "Continue with GitHub" on `/auth/signup` → GitHub authorization screen → land on `/auth/onboarding` as a new authenticated user.

### Shared Infrastructure (serves both US1 and US2)

- [X] T007 Add `signInWithSocial: (provider: 'google' | 'github') => Promise<void>` to `AuthContextType` interface in `book/src/context/AuthContext.tsx`
- [X] T008 Implement `signInWithSocial` method in `book/src/context/AuthContext.tsx` — builds PKCE OIDC authorize URL, POSTs to `/api/auth/sign-in/social`, navigates to returned provider redirect URL
- [X] T009 Add `signInWithSocial` to context value object in `book/src/context/AuthContext.tsx`
- [X] T010 [P] Add `.socialButtons`, `.socialButton`, `.divider` CSS classes to `book/src/components/Auth/Auth.module.css` — uses existing `--fm-*` glassmorphism variables

### User Story 1 — Google Signup/Login

- [X] T011 [US1] Add "Continue with Google" and "Continue with GitHub" buttons above email fields in `book/src/components/Auth/LoginForm.tsx` — with `handleSocialSignIn` error handler and loading state
- [ ] T012 [US1] E2E: New user clicks "Continue with Google" on `/auth/login` → Google consent → lands on `/auth/onboarding`
- [ ] T013 [US1] E2E: Returning Google user clicks button → lands on `/dashboard` (no onboarding shown)
- [ ] T014 [US1] E2E: Cancel on Google consent screen → returns to `/auth/login` with cancellation message
- [ ] T015 [US1] DB check: one `user` row, one `account` row with `providerId = "google"` after first signup

### User Story 2 — GitHub Signup/Login

- [X] T016 [US2] Add "Continue with Google" and "Continue with GitHub" buttons above account info fields in `book/src/components/Auth/SignUpForm.tsx` — with `handleSocialSignIn` error handler
- [ ] T017 [US2] E2E: New user clicks "Continue with GitHub" on `/auth/signup` → GitHub authorization → lands on `/auth/onboarding`
- [ ] T018 [US2] E2E: Returning GitHub user clicks button → lands on `/dashboard`
- [ ] T019 [US2] E2E: Cancel on GitHub authorization → returns to login/signup with cancellation message
- [ ] T020 [US2] E2E: GitHub account with private email → user sees friendly error ("make your GitHub email public or use email/password signup")

**Checkpoint**: New social signup (both providers) works end-to-end with onboarding redirect.

---

## Phase 4: User Story 3 — Returning Social User Login (Priority: P2)

**Goal**: Users who previously signed up via Google or GitHub can log back in without any password.

**Independent Test**: Sign up via Google/GitHub in one session → sign out → click same social button again → land on `/dashboard` without onboarding.

> **Note**: No additional code required — `signInWithSocial` and the OIDC relay handle returning users identically to new users. Better Auth detects existing account by email. The `onboardingCompleted = true` flag already prevents re-onboarding.

- [ ] T021 [US3] E2E: Sign out then "Continue with Google" → lands on `/dashboard` (tokens visible in localStorage: `physical_ai_access_token`, `physical_ai_refresh_token`)
- [ ] T022 [US3] E2E: Sign out then "Continue with GitHub" → lands on `/dashboard`
- [ ] T023 [US3] E2E: Refresh page while logged in via social → session persists (token refresh works)

**Checkpoint**: Returning social login works without creating duplicate accounts.

---

## Phase 5: User Story 4 — Email/Password Regression (Priority: P1)

**Goal**: All existing email/password flows work exactly as before — zero regression.

**Independent Test**: Email/password login and signup succeed, profile save works, protected routes work.

> **Note**: `auth.js` changes are purely additive (`socialProviders` key added). No existing config touched.

- [ ] T024 [US4] E2E: Email/password login on `/auth/login` → lands on `/dashboard`
- [ ] T025 [US4] E2E: Email/password signup on `/auth/signup` → creates account → redirects to onboarding
- [ ] T026 [US4] E2E: Profile save (`/api/profile`) works after email/password auth
- [ ] T027 [US4] E2E: Protected backend routes (FastAPI) still validate tokens via OIDC userinfo

**Checkpoint**: Zero regression confirmed — existing users unaffected.

---

## Phase 6: User Story 5 — Onboarding After Social Signup (Priority: P2)

**Goal**: First-time social signup users are directed to `/auth/onboarding`; returning users bypass it.

**Independent Test**: Complete Google/GitHub signup for the first time → verify `/auth/onboarding` redirect. Sign in again → verify `/dashboard` redirect (no onboarding).

> **Note**: No code change required — existing `needsOnboarding = !user.onboardingCompleted` check in `Root.tsx` handles social users automatically (new social user has `onboardingCompleted = false` by default).

- [ ] T028 [US5] E2E: First-time social signup → redirected to `/auth/onboarding` before `/dashboard`
- [ ] T029 [US5] E2E: Complete onboarding → redirected to `/dashboard`
- [ ] T030 [US5] E2E: Return social login (already onboarded) → `/dashboard` directly, no onboarding shown

**Checkpoint**: Onboarding gate works identically for social and email/password users.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [X] T031 [P] Add friendly `no_email` error message in `book/src/pages/auth/callback.tsx` for GitHub private-email case (Risk 3 from plan)
- [ ] T032 Smoke-test auth server social routes: `GET /api/auth/sign-in/social/google` → 302, `GET /api/auth/sign-in/social/github` → 302
- [ ] T033 Smoke-test `POST /api/auth/sign-in/social` with `{ provider: "google", callbackURL: "..." }` → returns `{ url: "https://accounts.google.com/..." }`
- [ ] T034 [P] Verify social login buttons visible and functional at 320px mobile viewport (both `/auth/login` and `/auth/signup`)
- [ ] T035 [P] Account deduplication: sign up with email/password `test@example.com`, sign out, "Continue with Google" (same email) → one user row in DB
- [ ] T036 Confirm no secrets committed: scan committed files for `GOOGLE_CLIENT_SECRET`, `GITHUB_CLIENT_SECRET` — must not appear outside `.env` (which is gitignored)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately ✅
- **Phase 2 (Foundational)**: Depends on Phase 1 ✅ BLOCKS all user story testing
- **Phase 3–6 (User Stories)**: All depend on Phase 2 completion; can proceed in parallel
- **Phase 7 (Polish)**: Can run alongside Phase 3–6 verification tasks

### User Story Dependencies

| Story | Depends On | Can Start When |
|-------|-----------|----------------|
| US1 (Google signup) | Phase 2 | T006 complete |
| US2 (GitHub signup) | Phase 2 | T006 complete |
| US3 (Returning login) | US1 or US2 | T012 or T017 passes |
| US4 (Email regression) | Phase 2 | T004 complete |
| US5 (Onboarding) | US1 or US2 | T012 or T017 passes |

### Within Each Phase

- Implementation tasks (T007–T011, T016, T031): Complete ✅
- E2E verification tasks: Sequential — run one story, validate, proceed

---

## Parallel Opportunities

```
# Phase 2 — run together:
T004: auth.js socialProviders + T005: .env.example + T006: set .env credentials

# Phase 3 implementation — ran in parallel (different files):
T010: Auth.module.css styles
T011: LoginForm.tsx social buttons
T016: SignUpForm.tsx social buttons

# Phase 7 verification — run together:
T032: smoke-test GET routes
T033: smoke-test POST /sign-in/social
T034: mobile viewport check
T035: deduplication check
T036: secrets scan
```

---

## Implementation Strategy

### MVP (Completed ✅)

All implementation tasks (T001–T011, T016, T031) are complete on `feature/oauth-google-github`.

### Remaining: E2E Verification Checklist

1. Start auth server: `cd auth-server && npm start`
2. Start frontend: `cd book && npm start`
3. Run Phase 7 smoke tests (T032, T033) — verify routes exist
4. Run Phase 3 E2E (T012–T020) — Google and GitHub new user signup
5. Run Phase 4 E2E (T021–T023) — returning social user login
6. Run Phase 5 E2E (T024–T027) — email/password regression
7. Run Phase 6 E2E (T028–T030) — onboarding gate
8. Run remaining Phase 7 tasks (T034–T036)
9. All pass → PR ready

---

## Notes

- `[P]` tasks operate on different files — safe to run in parallel
- `[US?]` label maps each task to its user story for traceability
- Implementation is complete; only E2E verification remains before PR
- No new packages, no schema migrations, no new callback pages introduced
- Social auth tokens are identical to email/password tokens — entire app behaves the same post-login
