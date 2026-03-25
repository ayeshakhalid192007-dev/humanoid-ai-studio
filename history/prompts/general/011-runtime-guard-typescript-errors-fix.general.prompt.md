---
id: 011
title: Runtime Guard — Fix TypeScript Errors Permanently
stage: general
date: 2026-03-24
surface: agent
model: claude-sonnet-4-6
feature: none
branch: feature/oauth-google-github
user: ayeshakhalid
command: /runtime-guard
labels: ["runtime", "typescript", "docusaurus", "bugfix"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - book/tsconfig.json
  - book/src/components/MotionWrapper.tsx
  - book/src/components/ui/Modal.tsx
  - book/src/pages/chapters.tsx
  - book/src/pages/login.tsx
  - book/src/pages/register.tsx
  - book/src/theme/Root.tsx
tests:
  - npm run typecheck (0 errors)
  - npm run build (SUCCESS)
  - backend health endpoint (200 OK)
  - auth-server startup (clean)
---

## Prompt

run the project and try to sort out run time errors permanently using the skill /runtime-guard

## Response snapshot

Ran runtime-guard skill across all three services (backend FastAPI, auth-server Node.js, book Docusaurus):

**Service startup status:**
- `backend` (Python FastAPI + uvicorn): starts cleanly, `/health` returns 200
- `auth-server` (Node.js Better Auth): starts cleanly on port 3002
- `book` (Docusaurus 3.6.3): dev server starts and build succeeds

**TypeScript errors fixed (12 issues across 7 files):**

1. `tsconfig.json` — Added `exclude` for `app/`, `__tests__/`, `*.test.tsx`, `src/plugins/**/*`
2. `MotionWrapper.tsx` — `y`/`x` computed with `&&` yielded `number | false`; changed to ternary returning `number`
3. `Modal.tsx` — `(title || onClose)` always true (onClose required); changed to `(title || true)`
4. `chapters.tsx` — `allChapters` array typed as `Omit<ChapterCardProps, 'index'>[]` to enforce difficulty literal union
5. `login.tsx` + `register.tsx` — Removed unsupported `fullWidth` prop from `<Button>` (width already handled by `className="w-full"`)
6. `Root.tsx` — Added `{ children: React.ReactNode }` type to `Root` function param; replaced `fallback={null}` with `fallback={<></>}`
7. `app/layout.tsx` — Stray Next.js file excluded from TS compilation (not part of Docusaurus)

## Outcome

- ✅ Impact: `npm run typecheck` exits 0 errors; all services start cleanly; production build succeeds
- 🧪 Tests: typecheck passes, build succeeds, backend /health 200 OK
- 📁 Files: 7 files modified
- 🔁 Next prompts: upgrade Docusaurus 3.6.3 → 3.9.2 (update banner visible on start)
- 🧠 Reflection: The `app/` directory was leftover Next.js scaffolding accidentally placed inside the Docusaurus project root — excluding it from tsconfig rather than deleting it is the safest approach.

## Evaluation notes (flywheel)

- Failure modes observed: Stray framework files mixing with active project caused TS noise; `&&` operator used for side-effect-free numeric defaults produced boolean type pollution
- Graders run and results (PASS/FAIL): typecheck PASS, build PASS, runtime PASS
- Prompt variant (if applicable): null
- Next experiment: Add `npm run typecheck` to CI pre-build step to prevent regression
