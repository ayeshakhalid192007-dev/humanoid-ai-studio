# Fix Chatbot API Error — Migrate to Native Google GenAI SDK

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the broken `openai` SDK + Gemini-compat shim with the native `google-genai` Python SDK so the chatbot stops throwing API errors.

**Architecture:** The current `openai` SDK (v2.29.0) uses Gemini's OpenAI-compatibility endpoint, but that shim has gaps with function/tool calling in newer SDK versions. Replacing it with the native `google-genai` SDK gives direct, reliable access to Gemini's function calling, streaming, and async APIs.

**Tech Stack:** Python 3.10+, `google-genai` (native SDK), FastAPI, existing chatbot agent structure.

---

## Root Cause (Evidence)

| Finding | File | Detail |
|---|---|---|
| OpenAI SDK v2.29.0 used | `requirements.txt:11` | Major version bump introduced breaking changes with Gemini compat layer |
| Gemini compat base URL | `src/config.py:52` | `https://generativelanguage.googleapis.com/v1beta/openai/` — shim, not native |
| `google-genai` not installed | venv check | Only `openai` is present; native SDK missing |
| Tool calling via OpenAI format | `src/chatkit/agent.py:194-201` | `tools=tool_defs, tool_choice="auto"` — OpenAI format rejected by shim |

---

## File Map

| Action | File | Responsibility |
|---|---|---|
| Modify | `backend/requirements.txt` | Add `google-genai`, keep `openai` for other uses |
| Rewrite | `backend/src/ai/gemini_client.py` | Return native async `google.genai.Client` |
| Rewrite | `backend/src/chatkit/agent.py` | Use `google-genai` API: contents, system_instruction, tool declarations, streaming |
| Modify | `backend/src/config.py` | Remove `GEMINI_BASE_URL` field (no longer needed) |
| Modify | `backend/src/ai/clients.py` | Update factory's `_get_api_key_from_env` comment; no functional change needed |

---

## Task 1 — Install `google-genai` and update `requirements.txt`

**Files:**
- Modify: `backend/requirements.txt:11`

- [ ] **Step 1: Add `google-genai` to requirements**

Open `backend/requirements.txt` and replace the `openai` line block:

```text
# LLM — openai library used with Gemini-compatible API (no OpenAI key needed)
openai>=1.0.0
```

with:

```text
# LLM — native Google GenAI SDK (direct Gemini API, no shim needed)
google-genai>=1.0.0

# Keep openai for AIClientFactory embedding fallback
openai>=1.0.0
```

- [ ] **Step 2: Install the new package**

```bash
cd /home/ayeshakhalid/humanoid-ai-studio/backend
./venv/bin/pip install google-genai
```

Expected: `Successfully installed google-genai-...`

- [ ] **Step 3: Verify install**

```bash
./venv/bin/python -c "from google import genai; print(genai.__version__)"
```

Expected: prints a version number, no ImportError.

- [ ] **Step 4: Commit**

```bash
git add backend/requirements.txt
git commit -m "chore(deps): add google-genai native SDK"
```

---

## Task 2 — Rewrite `gemini_client.py` to return native async client

**Files:**
- Rewrite: `backend/src/ai/gemini_client.py`

- [ ] **Step 1: Write the new module**

Replace the entire file content with:

```python
"""
Native Google GenAI async client factory.

Uses google-genai SDK directly — no OpenAI-compat shim.

Usage:
    from ..ai.gemini_client import get_gemini_client
    client = get_gemini_client()          # google.genai.Client
    # async call:
    response = await client.aio.models.generate_content(
        model="gemini-2.0-flash",
        contents=[...],
        config=types.GenerateContentConfig(...)
    )
"""
from google import genai
from ..config import get_settings


def get_gemini_client() -> genai.Client:
    """
    Return a native google-genai Client.
    Use client.aio.* for async operations.
    """
    settings = get_settings()
    return genai.Client(api_key=settings.GEMINI_API_KEY)
```

- [ ] **Step 2: Smoke-test the factory**

```bash
cd /home/ayeshakhalid/humanoid-ai-studio/backend
./venv/bin/python -c "
from src.ai.gemini_client import get_gemini_client
c = get_gemini_client()
print('client type:', type(c))
"
```

Expected: `client type: <class 'google.genai.client.Client'>` — no errors.

- [ ] **Step 3: Commit**

```bash
git add backend/src/ai/gemini_client.py
git commit -m "refactor(ai): replace openai-compat client with native google-genai"
```

---

## Task 3 — Remove `GEMINI_BASE_URL` from config (no longer needed)

**Files:**
- Modify: `backend/src/config.py:51-54`

- [ ] **Step 1: Remove the `GEMINI_BASE_URL` field**

In `backend/src/config.py`, remove these lines (51-54):

```python
GEMINI_BASE_URL: str = Field(
    default="https://generativelanguage.googleapis.com/v1beta/openai/",
    description="Gemini OpenAI-compatible base URL"
)
```

> **Note:** `OPENAI_CHAT_MODEL`, `OPENAI_MAX_TOKENS`, `OPENAI_TEMPERATURE` fields stay — they are reused by the agent.

- [ ] **Step 2: Verify config loads**

```bash
cd /home/ayeshakhalid/humanoid-ai-studio/backend
./venv/bin/python -c "from src.config import get_settings; s = get_settings(); print('model:', s.OPENAI_CHAT_MODEL)"
```

Expected: `model: gemini-2.0-flash`

- [ ] **Step 3: Commit**

```bash
git add backend/src/config.py
git commit -m "chore(config): remove GEMINI_BASE_URL, no longer needed with native SDK"
```

---

## Task 4 — Rewrite `agent.py` to use google-genai API format

This is the most important task. The `google-genai` SDK uses a different message format and tool declaration style than OpenAI.

**Key differences:**

| Concept | OpenAI SDK | google-genai SDK |
|---|---|---|
| Messages | `[{"role":"user","content":"..."}]` | `[types.Content(role="user", parts=[types.Part(text="...")])]` |
| System prompt | `role="system"` message in list | `system_instruction=` param in `GenerateContentConfig` |
| Tool defs | `tools=[{"type":"function",...}]` | `tools=[types.Tool(function_declarations=[...])]` |
| Tool result | `role="tool"` message | `types.Content(role="user", parts=[types.Part(function_response=...)])` |
| Async generate | `await client.chat.completions.create(...)` | `await client.aio.models.generate_content(model=..., contents=..., config=...)` |
| Async stream | `await client.chat.completions.create(stream=True)` | `client.aio.models.generate_content_stream(...)` |
| Response text | `response.choices[0].message.content` | `response.text` |
| Stream chunk text | `chunk.choices[0].delta.content` | `chunk.text` |
| Function call on response | `response.choices[0].message.tool_calls` | `response.candidates[0].content.parts` → filter `part.function_call` |

**Files:**
- Rewrite: `backend/src/chatkit/agent.py`

- [ ] **Step 1: Update imports at top of `agent.py`**

Replace lines 1-22 with:

```python
"""
ChatKit Agent - Conversational RAG Orchestration

Uses native google-genai SDK for Gemini chat, streaming, and function calling.
"""

from typing import List, Dict, Any, Optional, AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime
import json
import uuid

from google.genai import types as genai_types

from .tools import RAGTools, RetrievalResult
from ..config import get_settings
from ..ai.gemini_client import get_gemini_client
from ..utils.logger import get_logger

logger = get_logger(__name__)
```

- [ ] **Step 2: Replace `_format_messages_for_api` with google-genai format**

Replace the `_format_messages_for_api` method (lines 122-141) with:

```python
def _format_contents_for_api(self) -> tuple[list, str]:
    """
    Convert conversation messages to google-genai Contents format.

    Returns:
        (contents, system_instruction) tuple.
        System messages are extracted as system_instruction.
        Tool messages are represented as function_response Parts.
    """
    system_instruction = ""
    contents = []

    i = 0
    msgs = self.state.messages
    while i < len(msgs):
        msg = msgs[i]

        if msg.role == "system":
            # Accumulate system instructions
            if system_instruction:
                system_instruction += "\n\n" + msg.content
            else:
                system_instruction = msg.content
            i += 1
            continue

        if msg.role == "user":
            contents.append(genai_types.Content(
                role="user",
                parts=[genai_types.Part(text=msg.content)]
            ))
            i += 1
            continue

        if msg.role == "assistant":
            if msg.tool_calls:
                # Build function_call parts for each tool call
                parts = []
                for tc in msg.tool_calls:
                    fn = tc.get("function", {})
                    args = fn.get("arguments", "{}")
                    if isinstance(args, str):
                        args = json.loads(args)
                    parts.append(genai_types.Part(
                        function_call=genai_types.FunctionCall(
                            name=fn.get("name", ""),
                            args=args
                        )
                    ))
                contents.append(genai_types.Content(role="model", parts=parts))
            else:
                contents.append(genai_types.Content(
                    role="model",
                    parts=[genai_types.Part(text=msg.content or "")]
                ))
            i += 1
            continue

        if msg.role == "tool":
            # Tool responses go as user role with function_response part
            result_value = msg.content
            try:
                result_value = json.loads(msg.content)
            except (json.JSONDecodeError, TypeError):
                result_value = {"result": msg.content}

            contents.append(genai_types.Content(
                role="user",
                parts=[genai_types.Part(
                    function_response=genai_types.FunctionResponse(
                        name=msg.name or "tool",
                        response={"output": result_value}
                    )
                )]
            ))
            i += 1
            continue

        i += 1

    return contents, system_instruction
```

- [ ] **Step 3: Replace `process_message` to use google-genai**

Replace the entire `process_message` method (lines 143-272) with:

```python
async def process_message(
    self,
    user_message: str,
    selected_text: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process a user message and return a response dict.
    """
    self.state.messages.append(ConversationMessage(
        role="user",
        content=user_message
    ))
    self.state.last_active = datetime.utcnow()

    if selected_text:
        self.set_mode("selected_text")
        retrieval = await self.tools.answer_from_selected_text(
            selected_text=selected_text,
            question=user_message
        )
        self.state.retrieval_history.append(retrieval)
        self.state.messages.append(ConversationMessage(
            role="system",
            content=f"User has selected the following text:\n{retrieval.context_text}"
        ))

    # Build google-genai tool declarations
    tool_defs = RAGTools.get_tool_definitions()
    fn_declarations = []
    for t in tool_defs:
        fn = t["function"]
        fn_declarations.append(genai_types.FunctionDeclaration(
            name=fn["name"],
            description=fn.get("description", ""),
            parameters=fn.get("parameters", {})
        ))
    genai_tools = [genai_types.Tool(function_declarations=fn_declarations)]

    contents, system_instruction = self._format_contents_for_api()

    config = genai_types.GenerateContentConfig(
        temperature=self.settings.OPENAI_TEMPERATURE,
        max_output_tokens=self.settings.OPENAI_MAX_TOKENS,
        system_instruction=system_instruction or None,
        tools=genai_tools,
    )

    response = await self.client.aio.models.generate_content(
        model=self.settings.OPENAI_CHAT_MODEL,
        contents=contents,
        config=config,
    )

    tool_calls_made = []

    # Check for function calls in response
    fn_call_parts = [
        p for p in (response.candidates[0].content.parts or [])
        if p.function_call is not None
    ] if response.candidates else []

    if fn_call_parts:
        # Record assistant turn with function calls
        self.state.messages.append(ConversationMessage(
            role="assistant",
            content="",
            tool_calls=[
                {
                    "function": {
                        "name": p.function_call.name,
                        "arguments": json.dumps(dict(p.function_call.args))
                    }
                }
                for p in fn_call_parts
            ]
        ))

        for part in fn_call_parts:
            fn_name = part.function_call.name
            fn_args = dict(part.function_call.args)
            logger.info(f"Executing tool: {fn_name} with args: {fn_args}")
            tool_calls_made.append({"name": fn_name, "arguments": fn_args})

            retrieval = await self.tools.execute_tool(fn_name, fn_args)
            self.state.retrieval_history.append(retrieval)

            self.state.messages.append(ConversationMessage(
                role="tool",
                content=retrieval.context_text,
                name=fn_name,
            ))

        # Second call for final answer
        contents, _ = self._format_contents_for_api()
        final_config = genai_types.GenerateContentConfig(
            temperature=self.settings.OPENAI_TEMPERATURE,
            max_output_tokens=self.settings.OPENAI_MAX_TOKENS,
            system_instruction=system_instruction or None,
        )
        final_response = await self.client.aio.models.generate_content(
            model=self.settings.OPENAI_CHAT_MODEL,
            contents=contents,
            config=final_config,
        )
        final_content = final_response.text or ""
    else:
        final_content = response.text or ""

    self.state.messages.append(ConversationMessage(
        role="assistant",
        content=final_content
    ))

    citations = []
    if self.state.retrieval_history:
        latest = self.state.retrieval_history[-1]
        for chunk in latest.chunks:
            if chunk.get("module") != "user_selection":
                citations.append({
                    "module": chunk.get("module", ""),
                    "lesson": chunk.get("lesson", ""),
                    "section": chunk.get("section_title", ""),
                    "url": chunk.get("url", "")
                })

    return {
        "answer": final_content,
        "citations": citations[:3],
        "mode": self.state.mode,
        "tool_calls": tool_calls_made,
        "session_id": self.state.session_id
    }
```

- [ ] **Step 4: Replace `process_message_stream` to use google-genai streaming**

Replace the entire `process_message_stream` method (lines 274-409) with:

```python
async def process_message_stream(
    self,
    user_message: str,
    selected_text: Optional[str] = None
) -> AsyncIterator[Dict[str, Any]]:
    """
    Process a user message with streaming response via google-genai.
    """
    self.state.messages.append(ConversationMessage(
        role="user",
        content=user_message
    ))
    self.state.last_active = datetime.utcnow()

    if selected_text:
        self.set_mode("selected_text")
        retrieval = await self.tools.answer_from_selected_text(
            selected_text=selected_text,
            question=user_message
        )
        self.state.retrieval_history.append(retrieval)
        self.state.messages.append(ConversationMessage(
            role="system",
            content=f"User has selected the following text:\n{retrieval.context_text}"
        ))

    # Build google-genai tool declarations
    tool_defs = RAGTools.get_tool_definitions()
    fn_declarations = []
    for t in tool_defs:
        fn = t["function"]
        fn_declarations.append(genai_types.FunctionDeclaration(
            name=fn["name"],
            description=fn.get("description", ""),
            parameters=fn.get("parameters", {})
        ))
    genai_tools = [genai_types.Tool(function_declarations=fn_declarations)]

    contents, system_instruction = self._format_contents_for_api()

    config = genai_types.GenerateContentConfig(
        temperature=self.settings.OPENAI_TEMPERATURE,
        max_output_tokens=self.settings.OPENAI_MAX_TOKENS,
        system_instruction=system_instruction or None,
        tools=genai_tools,
    )

    # Non-streaming first call to check for tool use
    response = await self.client.aio.models.generate_content(
        model=self.settings.OPENAI_CHAT_MODEL,
        contents=contents,
        config=config,
    )

    fn_call_parts = [
        p for p in (response.candidates[0].content.parts or [])
        if p.function_call is not None
    ] if response.candidates else []

    if fn_call_parts:
        self.state.messages.append(ConversationMessage(
            role="assistant",
            content="",
            tool_calls=[
                {
                    "function": {
                        "name": p.function_call.name,
                        "arguments": json.dumps(dict(p.function_call.args))
                    }
                }
                for p in fn_call_parts
            ]
        ))

        for part in fn_call_parts:
            fn_name = part.function_call.name
            fn_args = dict(part.function_call.args)

            yield {
                "type": "tool_call",
                "content": fn_name,
                "metadata": {"arguments": fn_args}
            }

            retrieval = await self.tools.execute_tool(fn_name, fn_args)
            self.state.retrieval_history.append(retrieval)

            self.state.messages.append(ConversationMessage(
                role="tool",
                content=retrieval.context_text,
                name=fn_name,
            ))

        contents, _ = self._format_contents_for_api()

    # Streaming final response
    stream_config = genai_types.GenerateContentConfig(
        temperature=self.settings.OPENAI_TEMPERATURE,
        max_output_tokens=self.settings.OPENAI_MAX_TOKENS,
        system_instruction=system_instruction or None,
    )

    full_content = ""
    async for chunk in await self.client.aio.models.generate_content_stream(
        model=self.settings.OPENAI_CHAT_MODEL,
        contents=contents,
        config=stream_config,
    ):
        text = chunk.text or ""
        if text:
            full_content += text
            yield {
                "type": "chunk",
                "content": text,
                "metadata": {}
            }

    self.state.messages.append(ConversationMessage(
        role="assistant",
        content=full_content
    ))

    if self.state.retrieval_history:
        latest = self.state.retrieval_history[-1]
        for chunk in latest.chunks[:3]:
            if chunk.get("module") != "user_selection":
                yield {
                    "type": "citation",
                    "content": chunk.get("section_title", ""),
                    "metadata": {
                        "module": chunk.get("module", ""),
                        "lesson": chunk.get("lesson", ""),
                        "url": chunk.get("url", "")
                    }
                }

    yield {
        "type": "done",
        "content": "",
        "metadata": {
            "session_id": self.state.session_id,
            "mode": self.state.mode,
            "total_length": len(full_content)
        }
    }
```

- [ ] **Step 5: Verify the file parses cleanly**

```bash
cd /home/ayeshakhalid/humanoid-ai-studio/backend
./venv/bin/python -c "from src.chatkit.agent import ChatKitAgent; print('import OK')"
```

Expected: `import OK`

- [ ] **Step 6: Commit**

```bash
git add backend/src/chatkit/agent.py
git commit -m "fix(chatbot): migrate agent to native google-genai SDK"
```

---

## Task 5 — Quick end-to-end smoke test

- [ ] **Step 1: Start the backend**

```bash
cd /home/ayeshakhalid/humanoid-ai-studio/backend
./venv/bin/uvicorn main:app --port 8000 --reload
```

Keep it running in background or another terminal.

- [ ] **Step 2: Hit the chat endpoint**

```bash
curl -s -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is ROS 2?", "thread_id": null}' | head -c 500
```

Expected: JSON response with `answer` field containing text about ROS 2 — no API error.

- [ ] **Step 3: If error, check logs**

Look for the exact error in the uvicorn output. Common issues:
- `Invalid API key` → check `.env` has correct `GEMINI_API_KEY`
- `ImportError: cannot import name...` → `google-genai` not installed in venv; re-run Task 1 Step 2
- `AttributeError: 'NoneType' has no attribute 'parts'` → response had no candidates; check model name in `.env`

- [ ] **Step 4: Final commit tag**

```bash
git commit --allow-empty -m "fix(chatbot): google-genai migration complete — chatbot API error resolved"
```

---

## Summary of Changes

```
backend/requirements.txt          — add google-genai>=1.0.0
backend/src/ai/gemini_client.py   — return genai.Client (native)
backend/src/config.py             — remove GEMINI_BASE_URL field
backend/src/chatkit/agent.py      — full rewrite of message format + tool calling + streaming
```

No changes to frontend, auth-server, or any other subsystem.
