---
id: "002"
title: OAuth Social Login Clarifications
stage: spec
date: 2026-03-24
surface: agent
model: claude-sonnet-4-6
feature: 1-oauth-social-login
branch: feature/oauth-google-github
user: ayeshakhalid
command: /sp.clarify
labels: ["oauth", "clarify", "security", "better-auth", "social-login"]
links:
  spec: specs/1-oauth-social-login/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/1-oauth-social-login/spec.md
tests:
  - "null"
---

## Prompt

Before implementing anything, I need you to ask me all the necessary clarifying questions about adding Google and GitHub OAuth login/signup to my existing project.
Specifically, clarify the following areas:
1. Tech Stack & Framework

What frontend framework am I using? (React, Next.js, Vue, etc.)
What backend am I using? (Node/Express, Django, Laravel, etc.)
What auth library is already in place, if any? (Passport.js, NextAuth, Auth.js, Lucia, etc.)

2. Database & User Model

What database and ORM am I using? (PostgreSQL + Prisma, MongoDB + Mongoose, etc.)
Does my current User model/table have fields to store OAuth provider info?

3. Session & Token Strategy

Am I using sessions (express-session, etc.) or JWT tokens for auth?
Should OAuth users get the same token/session as email users?

4. Existing Auth Flow

Is there an existing login/signup page I should add OAuth buttons to, or should new pages be created?
Should a user be able to link both Google and GitHub to the same account?

5. Git & Branch

Should I create a new branch before starting? What should it be named?
Are there any branch naming conventions I should follow?

6. Environment & Config

Do I already have a .env file set up? Should I add to it or create .env.example?

Ask me all questions before writing a single line of code. Wait for my answers, then proceed with the implementation plan.

## Response snapshot

3 clarification questions asked and answered. Spec updated with each answer incrementally.

Ambiguity scan found most areas Clear from prior codebase exploration. 3 Partial areas addressed:

Q1 (Security): Auto-link behavior for email/password users logging in via OAuth with same email → A: Silent auto-link (Option A). Provider email trusted as proof of ownership.

Q2 (Profile data): What provider data to store on new user record → A: All available — name (username as fallback), email, profile picture URL in `image` field.

Q3 (Architecture): Social login initiation pattern — reuse frontend PKCE vs Better Auth server-side → A: Better Auth server-side (Option A). Frontend calls Better Auth social sign-in API; provider OAuth exchange handled internally.

Spec sections updated: FR-002, FR-003, FR-004, FR-005, Key Entities, Edge Cases, Assumptions, new Clarifications section added.

## Outcome

- ✅ Impact: 3 high-impact ambiguities resolved. Spec now ready for `/sp.plan`.
- 🧪 Tests: No tests at clarification stage.
- 📁 Files: specs/1-oauth-social-login/spec.md updated (Clarifications section + 5 section updates)
- 🔁 Next prompts: Run `/sp.plan` to generate architecture plan and implementation tasks.
- 🧠 Reflection: The most important clarification was Q3 (Better Auth server-side). The original spec incorrectly assumed the frontend PKCE pattern could be reused for social providers — this would have led to significant implementation rework if not caught here.

## Evaluation notes (flywheel)

- Failure modes observed: Original spec incorrectly assumed social login reuses frontend PKCE pattern (spec assumption was wrong — Better Auth social providers work server-side)
- Graders run and results (PASS/FAIL): Spec quality checklist — PASS after clarifications
- Prompt variant (if applicable): sp.clarify v1
- Next experiment: Run /sp.plan to see if Better Auth socialProviders plugin config covers all requirements without custom middleware
