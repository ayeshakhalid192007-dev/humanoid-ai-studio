---
id: 011
title: Optional Authentication with Protected Advanced Features
stage: green
date: 2026-02-15
surface: agent
model: claude-opus-4-6
feature: 001-book-publication-rag-chatbot
branch: 001-book-publication-rag-chatbot
user: MASTER
command: implement
labels: ["auth", "routing", "chatbot", "ux", "placeholder-pages"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - book/src/pages/index.tsx
  - book/src/theme/Root.tsx
  - book/src/pages/auth/login.tsx
  - book/src/pages/auth/signup.tsx
  - book/src/components/ChatbotWidget/index.tsx
  - book/src/components/ChatbotWidget/styles.module.css
  - book/src/components/Auth/UserMenu.tsx
  - book/src/pages/profile.tsx
  - book/src/pages/notes.tsx
  - book/src/pages/progress.tsx
  - book/src/pages/enroll.tsx
tests:
  - Docusaurus build passed successfully
---

## Prompt

Implement the following plan:

# Plan: Optional Authentication with Protected Advanced Features

## Architecture Summary
This is a Docusaurus site (book/) + Express auth server (auth-server/). Route protection is client-side via Root.tsx (ClientRouteGuard) and per-page redirects.

## Decisions
- Chatbot UX: Locked teaser — show FAB with lock icon, clicking opens AuthModal
- Missing pages: Create placeholder pages for /profile, /notes, /progress, /enroll with "Coming Soon" content, all auth-gated

## Changes (10 steps)
1. Remove forced redirect from homepage
2. Add auth-aware CTA to homepage
3. Expand route protection + save redirect path
4. Add redirect-back after login
5. Add redirect-back after signup
6. Gate chatbot widget (locked teaser)
7. Add locked chatbot styles
8. Create placeholder pages (auth-gated)
9. Add Dashboard link to UserMenu dropdown
10. No auth-server changes needed

## Response snapshot

Implemented all 10 steps of the optional authentication plan:

1. **Homepage** (`index.tsx`): Removed `HomeRedirect` forced redirect. Added auth-aware CTA — authenticated users see "Go to Dashboard", unauthenticated see "Login to Unlock Advanced Features" button opening AuthModal.

2. **Route protection** (`Root.tsx`): Expanded PROTECTED_ROUTES to include `/profile`, `/notes`, `/progress`, `/enroll`. Changed redirect from `/auth/signup` to `/auth/login`. Added `sessionStorage.setItem("auth_redirect", path)` before redirect.

3. **Login redirect-back** (`login.tsx`): `handleSuccess` reads `auth_redirect` from sessionStorage, clears it, redirects there or falls back to `/dashboard`.

4. **Signup redirect-back** (`signup.tsx`): Added `handleSuccess` with same redirect-back logic, passed as `onSuccess` prop to `SignUpForm`.

5. **Chatbot locked teaser** (`ChatbotWidget/index.tsx`): Unauthenticated users see locked FAB (lock icon overlay) that opens AuthModal. Authenticated users get normal chatbot.

6. **Locked styles** (`styles.module.css`): Added `.lockedFab` and `.lockOverlay` styles.

7. **UserMenu** (`UserMenu.tsx`): Added Dashboard link before Sign Out in dropdown.

8. **Placeholder pages**: Created `profile.tsx`, `notes.tsx`, `progress.tsx`, `enroll.tsx` with "Coming Soon" content, auth-gated by ClientRouteGuard.

Build verified: `docusaurus build` compiled successfully with zero errors.

## Outcome

- ✅ Impact: Homepage accessible to all visitors; protected routes gate advanced features behind auth; chatbot shows locked teaser for unauthenticated users
- 🧪 Tests: Docusaurus production build passes successfully
- 📁 Files: 11 files modified/created (7 modified, 4 new placeholder pages)
- 🔁 Next prompts: Manual verification of redirect-back flow; integration testing with auth-server running
- 🧠 Reflection: Clean implementation following existing patterns (BrowserOnly, useAuth, AuthModal). The sessionStorage redirect-back pattern is simple and effective.

## Evaluation notes (flywheel)

- Failure modes observed: None — build passes cleanly
- Graders run and results (PASS/FAIL): Build PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Verify redirect-back flow end-to-end with auth-server running
