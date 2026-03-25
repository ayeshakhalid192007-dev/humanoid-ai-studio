---
id: 021
title: Fix signup 404 and nav active links
stage: general
date: 2026-03-26
surface: agent
model: claude-sonnet-4-6
feature: none
branch: main
user: ayeshakhalid
command: fix signup 404 and page linking issues
labels: ["bug-fix","routing","docusaurus","navigation"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - book/src/components/ui/Button.tsx
  - book/src/components/Navigation/FuturisticNavbar.tsx
tests:
  - null
---

## Prompt

signup:1  Failed to load resource: the server responded with a status of 404 () when i click on the create account it gives me this error which is shown on console and the linking of my pages is also not correct fix these issues

## Response snapshot

Diagnosed two bugs:

1. **Button.tsx 404**: `Button` component rendered internal links with a raw `<motion.a href="/auth/signup">`. This bypasses Docusaurus's `Link` component, so the `baseUrl` (`/humanoid-ai-studio/`) is never prepended. Clicking "Create Account" navigated to `/auth/signup` instead of `/humanoid-ai-studio/auth/signup`.

   Fix: imported `@docusaurus/Link` and used it for internal hrefs (non-http), keeping the raw `motion.a` only for external links.

2. **isActive() hardcoded path**: `FuturisticNavbar.tsx` had `location.pathname === '/humanoid-ai-studio/'` hardcoded and also compared `/chapters` against the actual path `/humanoid-ai-studio/chapters`, causing active link highlighting to never work.

   Fix: used `useDocusaurusContext()` to get `siteConfig.baseUrl` dynamically and prepend it before comparing paths.

## Outcome

- ✅ Impact: "Create Account" button now correctly navigates to `/humanoid-ai-studio/auth/signup`; active nav links now highlight correctly
- 🧪 Tests: none run — manual browser test required
- 📁 Files: Button.tsx, FuturisticNavbar.tsx
- 🔁 Next prompts: verify all other Button usages with href props work correctly; check mobile nav
- 🧠 Reflection: Root cause was Button component not using Docusaurus Link — a common Docusaurus pitfall when wrapping with framer-motion

## Evaluation notes (flywheel)

- Failure modes observed: raw anchor tags in Docusaurus ignore baseUrl; isActive hardcoding breaks on any non-root deployment
- Graders run and results (PASS/FAIL): none
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): add a `useBaseUrl` hook wrapper to Button instead of @docusaurus/Link if framer-motion animation is needed
