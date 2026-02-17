# Quickstart: Reusable Intelligence Architecture

**Feature**: 003-reusable-intelligence-architecture
**Date**: 2026-02-17

## Prerequisites

- Python 3.11+
- Node.js 18+ (for auth-server)
- Running Neon Postgres instance
- Running Qdrant Cloud instance with `curriculum` collection
- OpenAI API key

## Environment Setup

1. Copy `.env.example` to `.env` in the repo root (if not already done):
   ```bash
   cp .env.example .env
   ```

2. Ensure the following variables are set:
   ```env
   OPENAI_API_KEY=sk-...
   QDRANT_URL=https://your-cluster.cloud.qdrant.io
   QDRANT_API_KEY=...
   NEON_DATABASE_URL=postgresql://...
   AUTH_SERVER_URL=http://localhost:3000
   ```

## Running the Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will:
- Connect to Neon Postgres and create/verify tables (including new `agent_execution_logs`)
- Add `prompt_version` columns to `personalized_content` and `urdu_translations` if missing
- Load prompt templates from `src/ai/prompts/templates/`
- Initialize the AI Orchestrator with all agents and skills
- Register both new `/api/ai/*` and legacy proxy endpoints

## New Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/ai/personalize` | POST | Required | Personalize chapter content |
| `/api/ai/translate` | POST | No | Translate chapter to Urdu |
| `/api/ai/chat` | POST | Optional | RAG chat (non-streaming) |
| `/api/ai/chat/stream` | POST | Optional | RAG chat (SSE streaming) |

## Testing a Personalization Request

```bash
# Requires valid session cookie
curl -X POST http://localhost:8000/api/ai/personalize \
  -H "Content-Type: application/json" \
  -H "Cookie: physical-ai.session_token=YOUR_SESSION" \
  -d '{"chapter_slug": "module-1-ros2/01-chapter"}'
```

Expected response:
```json
{
  "agent_type": "personalization",
  "skills_used": ["context_boundary", "hallucination_prevention", "knowledge_level", "educational_tone", "markdown_preservation"],
  "cached": false,
  "grounding_policy": "structural_fidelity",
  "generation_metadata": {
    "model": "gpt-4o-mini",
    "token_count": 1250,
    "latency_ms": 3200,
    "prompt_version": "a1b2c3d4e5f6g7h8"
  },
  "data": {
    "personalized_markdown": "# Chapter Title\n...",
    "content_version": "x9y8z7w6...",
    "profile_used": {"software_background": "Python", "robotics_knowledge": "beginner"}
  }
}
```

## Testing a Translation Request

```bash
curl -X POST http://localhost:8000/api/ai/translate \
  -H "Content-Type: application/json" \
  -d '{"chapter_slug": "module-1-ros2/01-chapter"}'
```

## Testing RAG Chat

```bash
curl -X POST http://localhost:8000/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is a ROS 2 node?", "mode": "full_book"}'
```

## Testing SSE Streaming

```bash
curl -N -X POST http://localhost:8000/api/ai/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain URDF", "mode": "full_book"}'
```

## Running Tests

```bash
cd backend
pytest tests/unit/test_orchestrator.py -v
pytest tests/unit/test_agents.py -v
pytest tests/unit/test_skills.py -v
pytest tests/integration/ -v
```

## Verifying Legacy Endpoint Compatibility

Legacy endpoints should still work but return `Deprecation` headers:

```bash
# Should work identically to before, with added Deprecation header
curl -v -X POST http://localhost:8000/api/personalize \
  -H "Content-Type: application/json" \
  -H "Cookie: physical-ai.session_token=YOUR_SESSION" \
  -d '{"chapter_slug": "module-1-ros2/01-chapter"}'

# Check for: Deprecation: true
# Check for: Link: </api/ai/personalize>; rel="successor-version"
```

## Key Files for Development

| File | Purpose |
|------|---------|
| `backend/src/ai/orchestrator.py` | Central routing and execution |
| `backend/src/ai/base.py` | Agent and Skill interfaces |
| `backend/src/ai/agents/*.py` | Agent implementations |
| `backend/src/ai/skills/*.py` | Skill implementations |
| `backend/src/ai/prompts/templates/*.md` | System prompt templates |
| `backend/src/ai/prompts/registry.py` | Prompt loading and versioning |
| `backend/src/api/ai.py` | New `/api/ai/*` API endpoints |
| `backend/src/db/neon_client.py` | DB methods (new logging, modified cache) |
