---
id: "006"
title: Remove hardcoded GEMINI_BASE_URL from clients.py
stage: green
date: 2026-03-24
surface: agent
model: claude-sonnet-4-6
feature: none
branch: main
user: Claude Code
command: Task 4 - Remove hardcoded GEMINI_BASE_URL from clients.py
labels: ["fix","backend","config","refactor"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/ai/clients.py
tests:
  - python3 -c "from src.ai.clients import get_ai_client_factory; print('Import OK')"
---

## Prompt

You are implementing Task 4: Remove hardcoded GEMINI_BASE_URL from clients.py

`clients.py` hardcodes:
```python
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
```

This value is already the canonical default in `config.py` (`Settings.GEMINI_BASE_URL`). Having it in two places means a config change (e.g. pointing at a Gemini proxy) must be made in two files.

The fix: delete the module-level constant and read `base_url` from `get_settings()` inside `get_ai_client_factory`.

## Response snapshot

Implemented the following changes to `backend/src/ai/clients.py`:

1. Added `from ..config import get_settings` import after line 7.
2. Removed the module-level `GEMINI_BASE_URL` constant (previously line 156).
3. Replaced `get_ai_client_factory` to use `get_settings()` for both `api_key` and `base_url`, eliminating the `import os` / `os.getenv("GEMINI_API_KEY")` inline call.

Grep confirmed no other files reference `GEMINI_BASE_URL` from `clients`. Import test returned `Import OK`. Committed as `bfc048e`.

## Outcome

- Impact: Eliminated a duplicated configuration constant; config changes to GEMINI_BASE_URL now only need to be made in `config.py`.
- Tests: Import smoke test passed — `from src.ai.clients import get_ai_client_factory` prints `Import OK`.
- Files: backend/src/ai/clients.py (1 file changed, 11 insertions, 10 deletions)
- Next prompts: Task 5 — Promote lazy gemini_client import in rag.py to module-level.
- Reflection: Straightforward removal of a duplicated constant; the fix follows the same pattern already used in `gemini_client.py`.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): import smoke test PASS
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Task 5 lazy import promotion in rag.py
