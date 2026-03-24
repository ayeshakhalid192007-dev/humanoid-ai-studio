# Tech Stack Compatibility Refactor — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix all 6 confirmed cross-language and cross-layer compatibility issues across auth-server, book (frontend), and backend so the three services are internally consistent and use correct dependency versions.

**Architecture:** Six targeted, self-contained fixes — no new abstractions introduced. Each fix is a config/wiring change. Order: auth-server first (one-line fix), then book tsconfig (config-only), then Python version pin, then backend client wiring (two files).

**Tech Stack:** Node.js 18 + Express 4 + Better Auth (auth-server) · Docusaurus 3.6.3 + React 18 + TypeScript 5.7.3 (book) · FastAPI + Pydantic V2 + Python 3.10+ (backend)

---

## Files Touched

| File | Change |
|------|--------|
| `auth-server/package.json` | `@types/express ^5.0.0` → `^4.17.21` |
| `book/tsconfig.json` | Replace with proper Docusaurus config extending `@docusaurus/tsconfig` |
| `backend/requirements.txt` | Add `# Python >= 3.10 required` header + `python-requires` comment |
| `backend/src/ai/clients.py` | Remove hardcoded `GEMINI_BASE_URL` constant; read from `get_settings()` |
| `backend/src/ai/agents/rag.py` | Promote lazy `get_gemini_client` import to module-level |

---

## Task 1 — Fix Express type/runtime version mismatch

**Files:**
- Modify: `auth-server/package.json:30`

The auth-server uses Express 4.x at runtime (`express ^4.21.0`) but `@types/express ^5.0.0` as dev types. Express 5 types are incompatible with Express 4 runtime — function signatures differ.

- [ ] **Step 1: Verify the mismatch**

```bash
cd auth-server && node -e "const e = require('express'); console.log(e.version)"
```
Expected output: `4.x.x`

- [ ] **Step 2: Change `@types/express` to match Express 4**

In `auth-server/package.json`, change line 30:
```json
"@types/express": "^4.17.21"
```
(was `"^5.0.0"`) — use `^4.17.21` consistently (aligns with Express 4.x latest stable types)

- [ ] **Step 3: Reinstall to update lock file**

```bash
cd auth-server && npm install
```
Expected: `node_modules/@types/express` installs 4.17.x, no resolution errors.

- [ ] **Step 4: Smoke-test the server starts**

```bash
cd auth-server && node --check src/index.js
```
Expected: No syntax/type errors (Node static check passes).

- [ ] **Step 5: Commit**

```bash
cd auth-server
git add package.json package-lock.json
git commit -m "fix(auth-server): align @types/express to Express 4.x runtime"
```

---

## Task 2 — Fix book tsconfig (remove Next.js artifacts, correct target)

**Files:**
- Modify: `book/tsconfig.json`

Current `tsconfig.json` has three problems:
1. `"target": "es5"` — React 18 uses async/await, optional chaining, nullish coalescing; these downcompile poorly to ES5 and cause subtle runtime issues
2. `"plugins": [{"name": "next"}]` — Next.js language server plugin in a Docusaurus project; causes VS Code to use wrong module resolution hints
3. `"include": ["next-env.d.ts", ...]` — references a Next.js generated file that does not exist in this repo

The fix is to extend `@docusaurus/tsconfig` (already installed as a devDep at `3.6.3`) and keep only project-specific overrides.

- [ ] **Step 1: Check `@docusaurus/tsconfig` is installed**

```bash
ls book/node_modules/@docusaurus/tsconfig/tsconfig.json
```
Expected: file exists.

- [ ] **Step 2: Replace `book/tsconfig.json`**

Replace the entire file with:

```json
{
  "extends": "@docusaurus/tsconfig",
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

This inherits Docusaurus-correct settings for `target`, `lib`, `module`, `jsx`, `moduleResolution`, `strict`, and `noEmit`. The `baseUrl` and `paths` override is the only project-specific addition.

- [ ] **Step 3: Run the TypeScript check**

```bash
cd book && npm run typecheck
```
Expected: exits 0 (or only pre-existing type errors, none introduced by this change).

- [ ] **Step 4: Run a Docusaurus build to confirm no regressions**

```bash
cd book && npm run build 2>&1 | tail -20
```
Expected: build completes, no new TS compilation errors.

- [ ] **Step 5: Commit**

```bash
cd book
git add tsconfig.json tsconfig.tsbuildinfo
git commit -m "fix(book): replace Next.js tsconfig with Docusaurus-correct config"
```

---

## Task 3 — Pin Python minimum version in requirements.txt

**Files:**
- Modify: `backend/requirements.txt`

The backend uses `async`/`await`, `match` statements (Python 3.10), Pydantic V2, and `asyncpg 0.29+` — all require Python 3.10+. Without a pinned minimum, a developer on Python 3.8 will get cryptic import errors.

- [ ] **Step 1: Confirm local Python version**

```bash
cd backend && python --version
```
Expected: `Python 3.10.x` or higher.

- [ ] **Step 2: Add version header to `backend/requirements.txt`**

Add these two lines at the very top of the file (before `# Web Framework`):

```text
# ============================================================
# Python >= 3.10 required (Pydantic V2, asyncpg 0.29+, async patterns)
# ============================================================

```

- [ ] **Step 3: Verify pip install is unaffected**

```bash
cd backend && python -m pip install -r requirements.txt --quiet --report /dev/null 2>&1 | tail -5
```
Note: `--dry-run` requires pip ≥ 23.1. Use the above form which works on pip ≥ 22. Or simply verify manually that the comment lines parse: `python -c "open('requirements.txt').read()"`. Either way, expected: no errors (comment lines are ignored by pip).

- [ ] **Step 4: Commit**

```bash
cd backend
git add requirements.txt
git commit -m "fix(backend): document Python >=3.10 minimum requirement"
```

---

## Task 4 — Remove hardcoded GEMINI_BASE_URL from clients.py

**Files:**
- Modify: `backend/src/ai/clients.py:156` and `:164-165`

`clients.py` hardcodes:
```python
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
```

This value is already the canonical default in `config.py` (`Settings.GEMINI_BASE_URL`). Having it in two places means a config change (e.g. pointing at a Gemini proxy) must be made in two files.

The fix: delete the module-level constant and read `base_url` from `get_settings()` inside `get_ai_client_factory`.

- [ ] **Step 1: Read the affected lines**

Open `backend/src/ai/clients.py` lines 153–166 to confirm current state:

```python
# Global factory instance for singleton access        # line 153
_factory_instance: Optional[AIClientFactory] = None   # line 154
                                                       # line 155
GEMINI_BASE_URL = "https://..."                        # line 156
                                                       # line 157
                                                       # line 158
async def get_ai_client_factory() -> AIClientFactory: # line 159
    """Get the global AI client factory instance."""   # line 160
    global _factory_instance                           # line 161
    if _factory_instance is None:                      # line 162
        import os                                      # line 163
        api_key = os.getenv("GEMINI_API_KEY")          # line 164
        _factory_instance = AIClientFactory(           # line 165
            api_key=api_key, base_url=GEMINI_BASE_URL) #
    return _factory_instance                           # line 166
```

The full block to replace is lines 153–166 (inclusive).

- [ ] **Step 2: Add settings import at the top of `clients.py`**

The existing import block ends at line 7 (`from ..utils.logger import get_logger`). Append after that line (before the blank line that precedes `class BaseAIClient`):
```python
from ..config import get_settings
```

- [ ] **Step 3: Remove the `GEMINI_BASE_URL` constant and update `get_ai_client_factory`**

Replace lines 154–167 with:

```python
# Global factory instance for singleton access
_factory_instance: Optional[AIClientFactory] = None


async def get_ai_client_factory() -> AIClientFactory:
    """Get the global AI client factory instance (Gemini-backed)."""
    global _factory_instance
    if _factory_instance is None:
        settings = get_settings()
        _factory_instance = AIClientFactory(
            api_key=settings.GEMINI_API_KEY,
            base_url=settings.GEMINI_BASE_URL,
        )
    return _factory_instance
```

- [ ] **Step 4: Confirm no other file imports `GEMINI_BASE_URL` from `clients.py`**

```bash
grep -r "from.*clients.*import.*GEMINI_BASE_URL\|clients\.GEMINI_BASE_URL" backend/
```
Expected: no matches.

- [ ] **Step 5: Run backend tests**

```bash
cd backend && python -m pytest tests/ -x -q 2>&1 | tail -20
```
Expected: no new failures related to `clients.py`.

- [ ] **Step 6: Commit**

```bash
cd backend
git add src/ai/clients.py
git commit -m "fix(backend): remove duplicate GEMINI_BASE_URL constant, read from settings"
```

---

## Task 5 — Promote lazy gemini_client import in rag.py to module-level

**Files:**
- Modify: `backend/src/ai/agents/rag.py:13` and `:189`

`rag.py` currently has `get_gemini_client` buried as a lazy import inside a method body (line 189). This hides a dependency, makes the file's imports inconsistent, and can mask `ImportError` at runtime instead of at startup.

The non-streaming code path (line 93) correctly uses the top-level `get_openai_client` import. The streaming path needs `get_gemini_client` for raw streaming access — both imports are valid and intentional, but the streaming one must be explicit.

- [ ] **Step 1: Add `get_gemini_client` to the top-level imports**

In `backend/src/ai/agents/rag.py`, the current import block ends at line 13:
```python
from ..clients import get_openai_client
```

Add the following line immediately after it (line 14):
```python
from ..gemini_client import get_gemini_client
```

- [ ] **Step 2: Remove the lazy import inside the method**

Find and remove these two lines (around line 189):
```python
        from ..gemini_client import get_gemini_client
        client = get_gemini_client()
```

Replace with just:
```python
        client = get_gemini_client()
```
(the import is now at the top; only the call line remains)

- [ ] **Step 3: Verify no other lazy imports of `gemini_client` exist in the file**

```bash
grep -n "from.*gemini_client" backend/src/ai/agents/rag.py
```
Expected: exactly one line — the top-level import.

- [ ] **Step 4: Run backend tests**

```bash
cd backend && python -m pytest tests/ -x -q 2>&1 | tail -20
```
Expected: no new failures.

- [ ] **Step 5: Commit**

```bash
cd backend
git add src/ai/agents/rag.py
git commit -m "fix(backend/rag): promote lazy gemini_client import to module-level"
```

---

## Task 6 — Final verification pass

- [ ] **Step 1: Verify all three services parse cleanly**

```bash
# Auth server
cd /home/ayeshakhalid/humanoid-ai-studio/auth-server && node --check src/index.js && echo "auth-server OK"

# Book TypeScript
cd /home/ayeshakhalid/humanoid-ai-studio/book && npm run typecheck && echo "book OK"

# Backend Python imports
cd /home/ayeshakhalid/humanoid-ai-studio/backend && python -c "from src.ai.clients import get_ai_client_factory; from src.ai.agents.rag import RAGReasoningAgent; print('backend OK')"
```

- [ ] **Step 2: Confirm no `GEMINI_BASE_URL` hardcoded outside config.py**

```bash
grep -rn "generativelanguage.googleapis.com" \
  /home/ayeshakhalid/humanoid-ai-studio/backend/src \
  /home/ayeshakhalid/humanoid-ai-studio/auth-server/src \
  /home/ayeshakhalid/humanoid-ai-studio/book/src
```
Expected: zero matches (the URL lives only in `config.py` and `.env.example`).

- [ ] **Step 3: Confirm no Next.js references remain in book tsconfig**

```bash
grep -n "next" /home/ayeshakhalid/humanoid-ai-studio/book/tsconfig.json
```
Expected: zero matches.

- [ ] **Step 4: Final commit summary**

```bash
cd /home/ayeshakhalid/humanoid-ai-studio
git log --oneline -6
```
Expected: 5 clean fix commits (Tasks 1–5) visible.
