---
name: Fix Chatbot API Error — Google SDK Migration
description: Migrated chatbot backend from openai-compat shim to native google-genai SDK to resolve API errors
type: general
stage: general
date: 2026-03-24
surface: agent
model: claude-sonnet-4-6
feature: none
branch: feature/oauth-google-github
user: ayeshakhalid
labels: ["chatbot", "google-genai", "api-fix", "migration", "backend"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/requirements.txt
  - backend/src/ai/gemini_client.py
  - backend/src/config.py
  - backend/src/chatkit/agent.py
  - backend/src/ai/agents/rag.py
  - backend/src/services/content_translator.py
  - backend/src/services/content_personalizer.py
  - backend/src/services/generator.py
  - docs/superpowers/plans/2026-03-24-fix-chatbot-google-sdk.md
tests: []
---

## Prompt

now use the context7 mcp server and fix the api error of chatbot as it is not responding and gives api error use google sdk for this to solve problem

## Response

### Root Cause

The chatbot backend used `openai` SDK v2.29.0 pointed at Gemini's OpenAI-compatibility shim (`https://generativelanguage.googleapis.com/v1beta/openai/`). The shim does not fully support tool/function calling in the newer major SDK version, causing API errors. The native `google-genai` SDK was not installed.

### Changes Made

1. **`requirements.txt`** — Added `google-genai>=1.0.0` (installed v1.68.0)
2. **`gemini_client.py`** — Replaced `AsyncOpenAI(base_url=...)` shim with `genai.Client(api_key=...)`
3. **`config.py`** — Removed `GEMINI_BASE_URL` field (no longer needed)
4. **`agent.py`** — Full rewrite of message formatting and API calls:
   - System messages → `system_instruction=` config param
   - User/assistant messages → `genai_types.Content` with `Parts`
   - Tool results → `role="user"` with `function_response` Parts
   - `client.chat.completions.create()` → `client.aio.models.generate_content()`
   - Streaming → `client.aio.models.generate_content_stream()`
   - Function calls extracted from `response.candidates[0].content.parts`
5. **`rag.py`** — Fixed streaming call to use native google-genai API
6. **`content_translator.py`**, **`content_personalizer.py`**, **`generator.py`** — Migrated all `chat.completions.create()` calls to `client.aio.models.generate_content()`

### Commits

- `042b3f7` chore(deps): add google-genai native SDK
- `034ddf7` refactor(ai): replace openai-compat client with native google-genai
- `c8c2876` chore(config): remove GEMINI_BASE_URL
- `af9f9ac` fix(chatbot): migrate agent to native google-genai SDK
- `629b7de` fix(rag-agent): migrate streaming call to native google-genai SDK
- `931e675` fix(services): migrate translator, personalizer, generator to native google-genai SDK
