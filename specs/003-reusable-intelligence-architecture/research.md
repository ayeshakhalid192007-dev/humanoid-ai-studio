# Research: Reusable Intelligence Architecture

**Feature**: 003-reusable-intelligence-architecture
**Date**: 2026-02-17
**Status**: Complete

## R1: Agent/Skill Composition Pattern in Python/FastAPI

### Decision
Use abstract base classes (`ABC`) with Protocol-style interfaces. Agents and skills are registered in dictionaries keyed by type string. No framework dependency — plain Python classes.

### Rationale
- FastAPI already uses dependency injection via `Depends()`. Adding a DI framework (e.g., `dependency-injector`) adds complexity for no gain since agents/skills are singletons created at startup.
- ABC provides clear contracts with `@abstractmethod`. Mypy and IDE tooling fully support it.
- Registry pattern (dict lookup) is the simplest routing mechanism and matches the existing pattern in the codebase (e.g., `chat_modes` dict in `chat.py`).

### Alternatives Considered
1. **Plugin framework (pluggy, stevedore)**: Over-engineered for 3 agents and 6 skills. Would add external dependency.
2. **OpenAI Agents SDK**: The codebase already moved away from the Agents SDK in the ChatKit migration. The spec explicitly requires custom orchestration with skill composition, which the Agents SDK doesn't natively support.
3. **LangChain/LangGraph**: Heavy dependency with opinionated abstractions. The feature needs lightweight composition, not a full framework.

---

## R2: Dual-Phase Skill Execution Model

### Decision
Each skill declares its phase via `get_phase() -> SkillPhase` (enum: `PRE`, `POST`, `BOTH`). The Orchestrator iterates skills twice: once for pre-processing, once for post-processing. Skills with `BOTH` participate in both passes.

### Rationale
- The spec (FR-010) explicitly requires dual-phase. Context Boundary Enforcement is pre-only (sanitize input). Markdown Preservation is post-only (validate output). Hallucination Prevention needs both (inject grounding directives pre, validate compliance post).
- Two-pass iteration is O(n) where n = number of skills per agent (max ~4). No performance concern.
- `SkillContext` is a dataclass passed through the chain, accumulating modifications. Each skill receives the output of the previous skill.

### Alternatives Considered
1. **Middleware chain (like FastAPI middleware)**: Overkill. Skills are synchronous transformations within a single request, not independent middleware layers.
2. **Event-driven (pre/post hooks)**: More complex wiring. The linear chain is sufficient and more debuggable.

### Implementation Detail
```python
class SkillPhase(str, Enum):
    PRE = "pre"
    POST = "post"
    BOTH = "both"

@dataclass
class SkillContext:
    agent_type: str
    grounding_policy: str
    system_prompt: str          # Modified by pre-skills
    user_message: str           # Modified by pre-skills
    original_content: str       # Immutable reference (for post-validation)
    ai_response: str | None     # Set after AI call, validated by post-skills
    metadata: dict              # Accumulated skill metadata
    skill_results: list[dict]   # Per-skill execution status
```

---

## R3: Prompt Registry and Versioning Pattern

### Decision
Prompt templates stored as `.md` files in `backend/src/ai/prompts/templates/`. Loaded at startup by `PromptRegistry`. Version is SHA-256 hash of file content (first 16 hex chars), matching the existing `content_version` pattern in `ChapterRetriever`.

### Rationale
- Markdown files are human-readable and diff-friendly in git. Developers can iterate on prompts without touching Python code (spec FR-017).
- SHA-256 hash versioning is already used for `content_version` in the caching layer (`ChapterRetriever._compute_version_hash()`). Reusing the same pattern reduces cognitive load.
- Templates are loaded once at startup (not per-request). No filesystem I/O during request handling.
- Hot-reload is NOT supported (spec doesn't require it). Server restart applies new prompts.

### Alternatives Considered
1. **Database-stored prompts**: Adds complexity. Would require admin UI for editing. Not needed for a dev team of this size.
2. **YAML/JSON prompt configs**: Less readable for long prompts. Markdown is the natural format since prompts contain formatting instructions.
3. **Python string constants**: The current pattern (inline in classes). Rejected because it violates FR-017 (centralized) and FR-018 (versioning independent of code).

### Template Format
Each `.md` template file contains:
```markdown
---
agent_type: personalization
version: auto  # Computed at load time via SHA-256
model: gpt-4o-mini
temperature: 0.3
max_tokens: 16000
---

You are an expert educational content personalizer...
[full system prompt text]
```

The YAML frontmatter contains model configuration. The body is the system prompt. This separates configuration from prompt content.

---

## R4: Per-Agent Context Grounding Policies

### Decision
Three grounding policies implemented as configurations within the `HallucinationPreventionSkill`. The skill reads the agent's `grounding_policy` from `SkillContext` and applies the corresponding pre/post logic.

### Rationale
- Grounding is a cross-cutting concern that should not be duplicated in each agent. A single skill with policy-based behavior keeps the logic centralized.
- The three policies map directly to spec FR-013: strict grounding (RAG), structural fidelity (personalization), semantic fidelity (translation).
- Post-processing validation is best-effort for structural/semantic fidelity (soft enforcement). For strict grounding, failure to validate causes the response to include a warning flag, not rejection (to avoid blocking legitimate responses that are hard to validate programmatically).

### Implementation Detail

**Strict Grounding (RAG) — Pre-processing:**
- Append to system prompt: "Answer ONLY from the provided context. If not found, say 'not available'."
- No modification to retrieved chunks (they're already the grounding source).

**Strict Grounding (RAG) — Post-processing:**
- Check if response contains "not available in this textbook" when retrieved chunks are empty or low-relevance.
- Check if response references modules/lessons (citation format present).
- Flag `grounding_validated: true/false` in skill results.

**Structural Fidelity (Personalization) — Pre-processing:**
- Extract heading hierarchy from original content (regex for `#` lines).
- Append heading list to system prompt: "You MUST preserve these headings in order: [list]"

**Structural Fidelity (Personalization) — Post-processing:**
- Extract heading hierarchy from AI output.
- Compare against original hierarchy. Flag discrepancies.

**Semantic Fidelity (Translation) — Pre-processing:**
- Extract code blocks from original content (regex for fenced blocks).
- Append code block count to system prompt: "The original contains N code blocks. Your output MUST contain exactly N code blocks."

**Semantic Fidelity (Translation) — Post-processing:**
- Extract code blocks from AI output.
- Compare against original code blocks. Flag if any changed or were removed.

### Alternatives Considered
1. **Separate grounding skills per agent**: Would create 3 skills instead of 1, with duplicated scaffolding. The policy pattern is simpler.
2. **LLM-as-judge validation**: Using a second AI call to validate grounding. Too expensive and slow for per-request validation. Reserved for offline quality evaluation.
3. **Embedding similarity validation**: Compare embedding similarity between input and output. Unreliable for translation (language changes) and overkill for structure checks.

---

## R5: Streaming Support in Orchestrator (FR-028)

### Decision
The Orchestrator exposes `execute_stream()` that returns an `AsyncGenerator[str, None]`. Only the RAG agent supports streaming. The Orchestrator runs pre-processing skills synchronously, then delegates to the agent's streaming method, and runs post-processing skills on the accumulated response after streaming completes.

### Rationale
- Pre-skills MUST run before the AI call (they modify the prompt). Post-skills MUST run after the full response is available (they validate output). Streaming happens in between.
- The existing `StreamingHandler` in `chatkit/streaming.py` converts async generators to SSE format. This is reused, not duplicated.
- Post-processing on streamed responses means the client sees tokens in real-time, but validation happens after the stream ends. Any grounding violations are logged but not communicated to the client mid-stream (same UX as current behavior).

### Alternatives Considered
1. **Token-level post-processing**: Validate each token as it streams. Impractical — validation requires the full response.
2. **Skip post-processing for streams**: Would bypass grounding validation. Unacceptable per FR-013.

---

## R6: Agent Execution Logging Table Schema

### Decision
New `agent_execution_logs` table with automatic 90-day cleanup.

### Rationale
- Spec FR-004 and FR-026 require per-request logging with agent type, skills, tokens, latency.
- JSONB for `skills_detail` avoids needing a separate junction table for skill-level data.
- 90-day retention (FR-030) via scheduled cleanup (checked on each write, or periodic background task).

### Schema
```sql
CREATE TABLE agent_execution_logs (
    id SERIAL PRIMARY KEY,
    agent_type TEXT NOT NULL,
    grounding_policy TEXT NOT NULL,
    skills_used TEXT[] NOT NULL,
    skills_detail JSONB NOT NULL DEFAULT '[]'::jsonb,
    -- Each element: {"skill": "name", "phase": "pre|post", "status": "success|fail", "duration_ms": int}
    token_count INTEGER,
    model TEXT NOT NULL,
    latency_ms INTEGER NOT NULL,
    cached BOOLEAN NOT NULL DEFAULT FALSE,
    request_metadata JSONB DEFAULT '{}'::jsonb,
    -- Contains: user_id (nullable), chapter_slug (nullable), request_type
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_agent_logs_created ON agent_execution_logs (created_at);
CREATE INDEX idx_agent_logs_type ON agent_execution_logs (agent_type);
```

### Cleanup Strategy
- On each log insert, check if last cleanup was >24 hours ago (tracked via a simple flag or last-delete timestamp).
- If due, `DELETE FROM agent_execution_logs WHERE created_at < NOW() - INTERVAL '90 days'`.
- Lightweight check, no background scheduler needed.

---

## R7: Legacy Endpoint Proxy Pattern

### Decision
Existing endpoints import the orchestrator singleton and delegate. Response is transformed from the unified envelope to the legacy shape. `Deprecation` and `Link` headers are added per RFC 8594.

### Rationale
- Spec FR-029 requires backward compatibility. The frontend currently calls `/api/personalize`, `/api/translate`, `/chat/v2`, `/chat/stream`.
- Thin proxies mean zero frontend changes needed immediately.
- The `Deprecation` header signals to API consumers that migration is expected.

### Alternatives Considered
1. **URL rewriting middleware**: Would require a separate middleware layer. Overkill for 4 endpoints.
2. **Immediate removal**: Breaks frontend. Rejected.

---

## R8: Singleton Lifecycle and Startup Wiring

### Decision
All agents, skills, registries, and the orchestrator are created in `main.py` lifespan handler and stored on `app.state`. API endpoints access them via `request.app.state`.

### Rationale
- Matches existing pattern: `app.state.neon_pool` is already set in lifespan.
- Agents are stateless singletons (spec FR-005). No per-request instantiation needed.
- Skills are stateless. Prompt registry reads files once at startup.
- The orchestrator holds references to all registries. Single point of creation ensures correct wiring.

### Startup Order
```python
# main.py lifespan handler
1. NeonClient connect (existing)
2. PromptRegistry load templates
3. SkillRegistry register all 6 skills
4. AgentRegistry register 3 agents (each receives required services)
5. AIOrchestrator(agent_registry, skill_registry, prompt_registry, neon_client)
6. app.state.orchestrator = orchestrator
```
