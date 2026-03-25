---
id: "019"
title: Fix Backend Railway Deployment Crash
stage: general
date: 2026-03-26
surface: agent
model: claude-sonnet-4-6
feature: none
branch: main
user: ayeshakhalid
command: "fix the backend deployment issue only"
labels: ["railway","deployment","docker","qdrant","devops","crash-fix"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/Dockerfile
tests:
  - Railway deployment: Active (b089a5d8)
---

## Prompt

fix the backend deployment issue only — backend was showing CRASHED on Railway after Dockerfile was committed.

## Response snapshot

Diagnosed two sequential issues:

1. **Runtime crash (QDRANT_API_KEY missing):** `src/config.py:78` declares `QDRANT_API_KEY: str = Field(...)` as required. Pydantic validation failed at startup because the variable was never set in Railway. App exited immediately → CRASHED status.

2. **Image size fix already in place:** `backend/Dockerfile` (committed in same session) replaced Nixpacks (5.7GB) with `python:3.11-slim` + CPU-only PyTorch. Build time: 112.48s, image accepted by Railway.

Fix applied:
- Retrieved Qdrant API key from user (new key created from Qdrant Cloud dashboard)
- Set via `railway variables set QDRANT_API_KEY=... --service backend --environment production`
- Railway auto-redeployed, build succeeded, service went Online

## Outcome

- ✅ Impact: Backend service Online at backend-production-52d2.up.railway.app
- ✅ Auth server: Online at auth-server-production-21f2.up.railway.app
- ✅ Frontend: Live on GitHub Pages
- 📁 Files: backend/Dockerfile (committed)
- 🔁 Next: Update OAuth redirect URIs in Google/GitHub consoles with production auth-server URL; run smoke tests on /health endpoints

## Evaluation notes (flywheel)

- Failure modes observed: Pydantic required-field crash on missing env var; Qdrant API key not surfaced during initial Railway setup
- Graders run and results: n/a
- Next experiment: Add a startup health-check endpoint that lists which required env vars are missing, to surface config errors before process exit
