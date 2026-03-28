# Humanoid AI Studio — Agent Architecture

This file documents the multi-agent system powering the Humanoid AI Studio platform. It is consumed by tools like Cursor, GitHub Copilot, and Claude Code to understand agent roles, responsibilities, and boundaries.

---

## Primary Agent: humanoid-ai-studio

**Role:** Orchestrator and main learner-facing AI companion ("Aria").

**Responsibilities:**
- Routes learner questions to the appropriate sub-agent
- Maintains conversational context across a session (up to 50 turns)
- Enforces rate limits and authentication state before delegating to sub-agents
- Produces structured, curriculum-grounded responses

**Entry points:**
- `POST /api/chat` — streaming RAG chat (SSE)
- `POST /api/personalize` — personalized chapter generation
- `POST /api/translate` — Urdu/multi-language translation

---

## Sub-Agent: rag-tutor

**Role:** Retrieval-Augmented Generation tutor

**Trigger:** Any factual question about ROS 2, Gazebo, Isaac Sim, VLA, or the capstone project

**Pipeline:**
1. Embed the learner's question using `sentence-transformers/all-MiniLM-L6-v2`
2. Query Qdrant vector DB (cosine similarity, top-k=5) over the curriculum collection
3. Construct a prompt with retrieved chunks + learner's question
4. Stream response from Google Gemini (primary) → OpenAI gpt-4o-mini (fallback) via SSE

**Constraints:**
- Rate-limited to 20 queries/hour per authenticated user (Redis counter)
- Must not answer if JWT token is invalid or expired
- Chunk retrieval threshold: cosine similarity ≥ 0.75

**Source files:**
- `backend/src/ai/orchestrator.py`
- `backend/src/db/qdrant_client.py`
- `backend/src/api/chat.py`

---

## Sub-Agent: personalization-agent

**Role:** Adaptive chapter generator

**Trigger:** Learner clicks "Personalized Version" in the Docusaurus book

**Pipeline:**
1. Fetch learner profile from Neon Postgres (skill_level: software/hardware/robotics background)
2. Retrieve the requested chapter chunks from Qdrant
3. Construct a personalization prompt with learner profile + chapter content
4. Stream adapted chapter from Gemini

**Supported personalizations:**
- Skill level: beginner / intermediate / advanced
- Background: software_engineer / hardware_engineer / roboticist / student
- Language: English (default) / Urdu

**Constraints:**
- Requires authenticated session (JWT validation via JWKS)
- Unauthenticated requests → redirect to login modal, do not return content
- Chapter personalization is cached per (user_id, chapter_id, profile_hash) in Redis (TTL: 1 hour)

**Source files:**
- `backend/src/api/personalize.py`
- `backend/src/ai/skill_pipeline.py`

---

## Sub-Agent: translation-agent

**Role:** Curriculum content translator (Urdu-first)

**Trigger:** Learner clicks "Translate to Urdu" or selects a target language

**Rules:**
- Code blocks (`\`\`\``) are NEVER translated — always preserved in original English
- ROS 2 package names, topic names, and CLI commands are never translated
- Output must include `dir="rtl"` metadata flag for Urdu (RTL rendering)
- Composition: learner can request personalized + translated simultaneously

**Source files:**
- `backend/src/api/translate.py`

---

## Sub-Agent: auth-agent (Better-Auth OIDC Server)

**Role:** Authentication and authorization

**Capabilities:**
- Issues RS256 JWT access tokens
- Validates Google + GitHub OAuth2 social login
- Exposes JWKS endpoint (`/.well-known/jwks.json`) for token verification
- Manages user profiles in Neon Postgres

**Constraints:**
- Runs as a separate Node.js service (Railway) — not part of the FastAPI backend
- All token verification by the backend is done via the JWKS endpoint (no shared secrets)

**Source files:**
- `auth-server/src/auth.js`
- `auth-server/src/index.js`

---

## Skill Modules (skills/)

| Skill | Purpose |
|---|---|
| `rag-tutor` | Curriculum Q&A via Qdrant + Gemini |
| `personalize-chapter` | Adaptive chapter generation from learner profile |
| `translate-urdu` | RTL Urdu translation preserving code blocks |
| `ros2-guide` | ROS 2 Humble Hawksbill step-by-step guidance |
| `code-explainer` | Robotics Python/YAML code walkthrough and debugging |

---

## Delegation Flow

```
Learner Question
      ↓
humanoid-ai-studio (orchestrator)
      ├── factual / curriculum question  → rag-tutor
      ├── "personalize this chapter"     → personalization-agent
      ├── "translate to Urdu"            → translation-agent
      └── auth / login / session        → auth-agent (Better-Auth)
```
