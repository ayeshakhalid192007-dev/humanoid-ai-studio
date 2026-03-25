---
id: "018"
title: CI/CD Deployment Plan GitHub Netlify Railway
stage: general
date: 2026-03-25
surface: agent
model: claude-sonnet-4-6
feature: none
branch: feature/oauth-google-github
user: ayeshakhalid
command: "help me create a complete CI/CD deployment plan"
labels: ["cicd","deployment","github-actions","railway","netlify","github-pages","devops"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .github/workflows/ci.yml
  - .github/workflows/deploy-backend.yml
  - .github/workflows/deploy-auth.yml
  - .github/workflows/deploy-staging.yml
  - .github/workflows/preview.yml
tests:
  - ci.yml runs pytest on backend (mock mode)
  - ci.yml runs typecheck + build on frontend
  - ci.yml runs npm audit on auth-server
---

## Prompt

I have successfully completed my project and want to deploy it using a CI/CD pipeline.
My deployment stack includes:
- GitHub Pages (for static frontend hosting)
- Netlify (for frontend with serverless functions / forms / edge)
- Railway (for backend / database / full-stack services)

Please review the project for project type and its framework and single repository is having both backend and frontend and from the review check for the backend and database and when preparing a plan also tell me that which part of the project would you host on which service

## Response snapshot

Performed full codebase exploration to identify:
- 3-service monorepo: Docusaurus frontend, FastAPI backend, Express+Better Auth server
- Databases: Neon Postgres (primary) + Qdrant Cloud (vector) + Redis (optional cache)

Service routing recommendation:
- GitHub Pages → Docusaurus production (static, already configured)
- Netlify → PR preview deploys only (draft per PR, not production)
- Railway → FastAPI backend (port 8000) + Express auth server (port 3002)

Created 4 new/updated workflow files:
- ci.yml: lint + typecheck + tests on every PR
- deploy-backend.yml: Railway production deploy (replaced docs-only stub)
- deploy-auth.yml: Express auth server Railway deploy (new)
- deploy-staging.yml: Both backend services → Railway staging on dev push
- preview.yml: Netlify draft deploy per PR with auto PR comment

Provided full GitHub Secrets table, Railway setup steps, Netlify one-time setup, and pre-launch checklist.

## Outcome

- ✅ Impact: Complete CI/CD pipeline for monorepo with 3 services across 3 hosting platforms
- 🧪 Tests: Backend pytest (mock mode), frontend typecheck + build, auth-server npm audit
- 📁 Files: 5 GitHub Actions workflow files created/updated
- 🔁 Next prompts: Set up Railway project, configure GitHub Secrets, run db:migrate on auth-server, update OAuth redirect URIs
- 🧠 Reflection: Netlify fits as PR preview layer rather than production host given SSG output and existing GitHub Pages setup; Railway handles both persistent Node.js and Python services cleanly in one project

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): n/a
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): Add a smoke-test job after Railway deploys that hits /api/health and fails the workflow if unhealthy
