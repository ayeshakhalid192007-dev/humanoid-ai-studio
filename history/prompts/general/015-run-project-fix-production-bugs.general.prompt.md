---
name: Run project with real credentials and fix all production bugs
description: Full production verification run — identified and fixed 7 bugs across backend services
type: general
stage: general
id: "015"
date: "2026-03-25"
surface: agent
model: claude-sonnet-4-6
feature: none
branch: feature/oauth-google-github
labels: ["production", "debugging", "rag", "personalization", "translation", "streaming", "auth"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
---

## Prompt

> now run the project with all real credentials for all features which are present in a project and make sure all features work properly as these are on production level.

## Response

Ran full production verification. All 3 services were already running (ports 3000, 3002, 8000). Identified and fixed 7 bugs:

### Bugs Fixed

1. **RAG similarity threshold too high** (`retriever.py:46`)
   - Was 0.7, but all-MiniLM-L6-v2 top scores are ~0.59 → lowered to 0.4

2. **Retrieved chunk key mismatch** (`chat.py:302-308`)
   - Was using `chunk.get("content")`, `chunk.get("id")`, `chunk.get("title")`, `chunk.get("source")`
   - Fixed to use correct Qdrant payload keys: `text`, `chunk_id`, `section_title`, `url`

3. **Streaming endpoint wrong request type** (`chat.py:522-523`)
   - `chat_stream()` had `request: StreamChatRequest` but passed it to `get_orchestrator(request)` which expects FastAPI `Request`
   - Fixed by adding `http_request: Request` parameter

4. **chat/v2 endpoint same bug** (`chat.py:377`)
   - Same fix applied to `chat_v2()` endpoint

5. **Personalization/Translation agents not migrated to Gemini SDK**
   - Both still used `get_openai_client()` from old clients.py (no base_url configured → went to OpenAI endpoint)
   - Migrated both to use native `get_gemini_client()` + `google.genai.types`
   - Also fixed `chapter_data["markdown"]` → `chapter_data.get("content", ...)` key mismatch

6. **`AuthenticatedUser` is a dataclass, not a dict** (`ai.py:97-98`)
   - `user.get("id")` raised AttributeError → fixed to `user.user_id if hasattr(user, 'user_id') else user.get("id")`

7. **Session metadata is a JSON string, not dict** (`sessions.py:213`)
   - Fixed with `isinstance(..., dict)` guard before calling `.get()`

### Final Feature Test Results

| Feature | Status |
|---|---|
| Backend health (Qdrant/Neon/Gemini) | ✓ |
| Auth server health | ✓ |
| Frontend (Docusaurus) | ✓ HTTP 200 |
| Google OAuth redirect | ✓ |
| GitHub OAuth redirect | ✓ |
| RAG chat full_book (5 chunks) | ✓ |
| SSE Streaming | ✓ |
| Session CRUD | ✓ |
| Translation to Urdu | ✓ |
| Personalization (Gemini SDK) | ✓ |
| JWKS endpoint | ✓ |
| Email sign-up/sign-in | ✓ |

## Files Modified

- `backend/src/services/retriever.py` — threshold 0.7 → 0.4
- `backend/src/api/chat.py` — chunk keys, streaming fix, chat/v2 fix
- `backend/src/api/ai.py` — markdown key, AuthenticatedUser compat
- `backend/src/api/sessions.py` — metadata string guard
- `backend/src/ai/agents/personalization.py` — Gemini SDK migration
- `backend/src/ai/agents/translation.py` — Gemini SDK migration
