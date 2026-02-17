# Implementation Plan: Reusable Intelligence Architecture

**Branch**: `003-reusable-intelligence-architecture` | **Date**: 2026-02-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-reusable-intelligence-architecture/spec.md`

## Summary

Unify all AI features (personalization, translation, RAG chat) under a single AI Orchestrator with composable agents and skills. The Orchestrator routes requests to specialized agents (Personalization, Translation, RAG Reasoning), each agent composes dual-phase skills (pre/post-processing), and all system prompts are centralized in a versioned prompt registry. Per-agent context grounding policies enforce strict grounding for RAG, structural fidelity for personalization, and semantic fidelity for translation. Legacy endpoints become thin proxies. A new `agent_execution_logs` table provides observability.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, asyncpg (raw SQL), OpenAI SDK (AsyncOpenAI), Qdrant Cloud, pydantic/pydantic-settings
**Storage**: Neon Postgres (asyncpg pool, min=5/max=20), Qdrant Cloud (collection: `curriculum`, 1536-dim cosine)
**Testing**: pytest + httpx (AsyncClient) for API tests, pytest-asyncio for async service tests
**Target Platform**: Linux server (deployed), Windows dev (local)
**Project Type**: Web application (backend-only changes for this feature; frontend out of scope)
**Performance Goals**: Cached responses within 20% of current direct-call latency (SC-004); 50 concurrent requests without error
**Constraints**: Skills are in-process transformations (not separate AI calls); agents are stateless singletons; all AI calls through Orchestrator
**Scale/Scope**: 3 agents, 6 skills, 4 new API endpoints, 1 new DB table, migration of 4 existing services

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

> Note: The project constitution (`.specify/memory/constitution.md`) is an unpopulated template. Gates are evaluated against the project's established patterns and CLAUDE.md principles.

| Gate | Status | Notes |
|------|--------|-------|
| Smallest viable diff | PASS | Refactors existing code into new architecture; no unrelated changes |
| No hardcoded secrets | PASS | All API keys via pydantic-settings / `.env`; no changes to secret handling |
| No invented APIs | PASS | All endpoints derived from spec FR-019 through FR-029 |
| Clarify before implement | PASS | 10 clarifications resolved in spec; per-agent grounding policy explicitly defined |
| Test-first capability | PASS | Each agent/skill has testable interfaces; acceptance scenarios defined per user story |
| Code reference citations | PASS | All existing code paths documented with file:line references |

**Pre-Phase 0 Gate: PASSED**

## Project Structure

### Documentation (this feature)

```text
specs/003-reusable-intelligence-architecture/
├── plan.md              # This file
├── research.md          # Phase 0: technology decisions and patterns
├── data-model.md        # Phase 1: entity schemas and DB migrations
├── quickstart.md        # Phase 1: developer setup guide
├── contracts/           # Phase 1: OpenAPI endpoint contracts
│   ├── ai-personalize.yaml
│   ├── ai-translate.yaml
│   ├── ai-chat.yaml
│   └── envelope.yaml    # Common response envelope schema
├── checklists/
│   └── requirements.md  # Spec quality checklist (existing)
└── tasks.md             # Phase 2 output (via /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── ai/                          # NEW: Intelligence architecture module
│   │   ├── __init__.py
│   │   ├── orchestrator.py          # AI Orchestrator (FR-001, FR-002, FR-003)
│   │   ├── base.py                  # Agent/Skill abstract interfaces (FR-005, FR-010)
│   │   ├── registry.py              # Agent + Skill registries
│   │   ├── envelope.py              # Common response envelope (FR-022)
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── personalization.py   # Personalization Agent (FR-006)
│   │   │   ├── translation.py       # Translation Agent (FR-007)
│   │   │   └── rag.py               # RAG Reasoning Agent (FR-008)
│   │   ├── skills/
│   │   │   ├── __init__.py
│   │   │   ├── markdown_preservation.py    # FR-011
│   │   │   ├── context_boundary.py         # FR-012
│   │   │   ├── hallucination_prevention.py # FR-013
│   │   │   ├── educational_tone.py         # FR-014
│   │   │   ├── knowledge_level.py          # FR-015
│   │   │   └── code_block_detection.py     # FR-016
│   │   └── prompts/
│   │       ├── __init__.py
│   │       ├── registry.py          # Prompt registry with versioning (FR-017, FR-018)
│   │       └── templates/           # Prompt template files
│   │           ├── personalization.md
│   │           ├── translation.md
│   │           ├── rag_chat.md
│   │           └── rag_chatkit.md
│   ├── api/
│   │   ├── ai.py                    # NEW: /api/ai/* endpoints (FR-019–FR-022, FR-028, FR-029)
│   │   ├── personalize.py           # MODIFIED: becomes thin proxy
│   │   ├── translate.py             # MODIFIED: becomes thin proxy
│   │   ├── chat.py                  # MODIFIED: /chat/v2 and /chat/stream become thin proxies
│   │   └── ...                      # Unchanged: auth, health, sessions, rate_limit, validators
│   ├── services/                    # Existing services (preserved, used by agents internally)
│   │   ├── embedder.py              # Used by RAG agent
│   │   ├── retriever.py             # Used by RAG agent
│   │   ├── chapter_retriever.py     # Used by Personalization/Translation agents
│   │   ├── content_personalizer.py  # DEPRECATED: logic migrated to agent
│   │   ├── content_translator.py    # DEPRECATED: logic migrated to agent
│   │   ├── generator.py             # DEPRECATED: logic migrated to RAG agent
│   │   └── rag_pipeline.py          # DEPRECATED: logic migrated to RAG agent
│   ├── chatkit/                     # DEPRECATED: logic migrated to RAG agent
│   │   ├── agent.py                 # Becomes thin wrapper
│   │   ├── tools.py                 # Tool definitions reused by RAG agent
│   │   └── streaming.py             # StreamingHandler reused by Orchestrator
│   └── db/
│       └── neon_client.py           # MODIFIED: add agent_execution_logs methods
└── tests/
    ├── unit/
    │   ├── test_orchestrator.py
    │   ├── test_agents.py
    │   └── test_skills.py
    └── integration/
        ├── test_ai_personalize.py
        ├── test_ai_translate.py
        └── test_ai_chat.py
```

**Structure Decision**: Web application, backend-only. New `backend/src/ai/` module contains all intelligence architecture. Existing `services/` and `chatkit/` are preserved during migration but deprecated. Frontend (`book/`) is out of scope — it continues calling the same endpoint shapes.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| New `ai/` module alongside existing `services/` | Clean separation of intelligence architecture from utility services | Merging into `services/` would bloat the module and conflate orchestration with individual utilities |
| Dual-phase skill execution | Spec FR-010 requires pre/post-processing phases | Single-phase would not support input sanitization (pre) + output validation (post) in the same skill |
| Prompt template files on disk | Spec FR-017/FR-018 requires centralized, versionable prompts | Inline prompts (current pattern) can't be versioned independently of code deployments |

---

## Architecture: Per-Agent Context Grounding (User-Requested Focus)

The user specifically requested the plan focus on **per-agent context grounding**. This section details the grounding policies, their implementation in the skill system, and how the Orchestrator enforces them.

### Grounding Policy Definitions

| Agent | Policy Name | Enforcement Level | Description |
|-------|------------|-------------------|-------------|
| RAG Reasoning | `strict_grounding` | HARD — reject if violated | Output MUST contain ONLY information present in retrieved context. Any claim not traceable to a source chunk is a violation. Unknown answers MUST return "not available" rather than fabricate. |
| Personalization | `structural_fidelity` | SOFT — warn + flag | Chapter heading hierarchy, section ordering, and topic scope MUST be preserved. Explanations and examples MAY be adapted to user profile. No new sections or concepts added. |
| Translation | `semantic_fidelity` | SOFT — warn + flag | Meaning MUST be preserved accurately across languages. Code blocks MUST remain untouched. Significant semantic drift is flagged. |

### Grounding Implementation via Hallucination Prevention Skill (FR-013)

The `HallucinationPreventionSkill` is a **dual-phase** skill:

**Pre-processing phase** (before AI call):
- Injects grounding instructions into the system prompt based on agent type
- For RAG: adds explicit "ONLY use retrieved context" directive + citation requirement
- For Personalization: adds "preserve heading structure" + "do not add new sections" directive
- For Translation: adds "preserve meaning" + "do not translate code" directive

**Post-processing phase** (after AI call):
- For RAG: validates that all claims reference source chunks; flags unsupported claims
- For Personalization: validates heading structure matches original; flags structural drift
- For Translation: validates code blocks unchanged; flags if Markdown structure differs

### Grounding in System Prompts

Each prompt template in `backend/src/ai/prompts/templates/` embeds grounding rules explicitly. The Hallucination Prevention skill **augments** these prompts at runtime with context-specific enforcement (e.g., the actual retrieved chunks for RAG, the original heading list for Personalization).

**RAG prompt grounding block** (embedded in `rag_chat.md`):
```
GROUNDING RULES (STRICT):
- Answer ONLY from the provided context chunks below
- If the answer is not in the context, respond: "The answer is not available in this textbook."
- NEVER use general knowledge to supplement context
- Cite every claim with "According to Module X, Lesson Y: [content]"
```

**Personalization prompt grounding block** (embedded in `personalization.md`):
```
STRUCTURAL FIDELITY RULES:
- PRESERVE the exact heading hierarchy from the original chapter
- PRESERVE section ordering — do not rearrange
- You MAY adapt explanations, examples, and analogies to the student profile
- You MUST NOT add new sections, headings, or concepts not in the original
- You MUST NOT remove any existing sections
- Code blocks must remain exactly as-is
```

**Translation prompt grounding block** (embedded in `translation.md`):
```
SEMANTIC FIDELITY RULES:
- Translate all prose text to Urdu faithfully
- PRESERVE exact meaning — no additions, omissions, or reinterpretation
- DO NOT translate code blocks, file paths, variable names, or CLI commands
- KEEP technical terms in English with Urdu transliteration where helpful
- PRESERVE all Markdown formatting and structure exactly
```

### Orchestrator Grounding Enforcement Flow

```
Request arrives at Orchestrator
    │
    ├─ 1. Select agent by request type
    ├─ 2. Verify agent's required skills are registered
    ├─ 3. Execute PRE-PROCESSING skills (in order):
    │      ├─ Context Boundary Enforcement: sanitize input
    │      ├─ Hallucination Prevention (pre): inject grounding directives
    │      ├─ Knowledge Level Adjustment (pre): adjust complexity directive
    │      └─ ... other pre-skills per agent
    │
    ├─ 4. Agent executes AI call with grounded prompt
    │
    ├─ 5. Execute POST-PROCESSING skills (in order):
    │      ├─ Hallucination Prevention (post): validate grounding compliance
    │      ├─ Markdown Preservation: verify structure integrity
    │      ├─ Code Block Detection: verify code blocks unchanged
    │      └─ ... other post-skills per agent
    │
    ├─ 6. Log execution: agent_type, skills_used, grounding_policy, token_count, latency
    └─ 7. Return response in common envelope
```

### Grounding Logging

Each request log entry in `agent_execution_logs` includes:
- `grounding_policy`: The policy name applied (e.g., `strict_grounding`)
- Per-skill status including whether grounding validation passed/failed
- Duration of grounding checks (part of skill durations)

---

## Key Design Decisions

### D1: Agent Interface

```python
# backend/src/ai/base.py
class BaseAgent(ABC):
    """Abstract base for all AI agents. Singleton, stateless per-request."""

    @abstractmethod
    def get_agent_type(self) -> str: ...

    @abstractmethod
    def get_required_skills(self) -> list[str]: ...

    @abstractmethod
    def get_grounding_policy(self) -> str: ...

    @abstractmethod
    async def execute(self, request: AgentRequest) -> AgentResponse: ...

    @abstractmethod
    def validate_output(self, response: AgentResponse) -> bool: ...
```

### D2: Skill Interface

```python
# backend/src/ai/base.py
class BaseSkill(ABC):
    """Abstract base for composable skills. Declares execution phase."""

    @abstractmethod
    def get_name(self) -> str: ...

    @abstractmethod
    def get_phase(self) -> SkillPhase: ...  # PRE, POST, or BOTH

    async def pre_process(self, context: SkillContext) -> SkillContext:
        """Override for pre-processing. Default: passthrough."""
        return context

    async def post_process(self, context: SkillContext) -> SkillContext:
        """Override for post-processing. Default: passthrough."""
        return context
```

### D3: Orchestrator Routing

```python
# backend/src/ai/orchestrator.py
class AIOrchestrator:
    """Singleton. Routes requests to agents, composes skills, logs execution."""

    def __init__(self, agent_registry, skill_registry, prompt_registry, neon_client):
        # Registries injected at startup
        ...

    async def execute(self, request_type: str, payload: dict) -> EnvelopeResponse:
        # 1. Look up agent by request_type
        # 2. Verify required skills
        # 3. Run pre-processing skills
        # 4. Agent.execute()
        # 5. Run post-processing skills
        # 6. Log execution
        # 7. Return envelope
        ...

    async def execute_stream(self, request_type: str, payload: dict) -> AsyncGenerator:
        # Same as execute but yields SSE tokens for streaming agents
        ...
```

### D4: Prompt Registry

```python
# backend/src/ai/prompts/registry.py
class PromptRegistry:
    """Loads prompt templates from disk. Computes version hash for cache invalidation."""

    def __init__(self, templates_dir: Path):
        self._templates: dict[str, PromptTemplate] = {}
        self._load_templates(templates_dir)

    def get_template(self, agent_type: str) -> PromptTemplate:
        """Returns template with content and version hash."""
        ...

    def get_version(self, agent_type: str) -> str:
        """SHA-256 hash of template content (first 16 hex chars)."""
        ...
```

### D5: Common Response Envelope (FR-022)

```python
# backend/src/ai/envelope.py
class AIEnvelope(BaseModel):
    agent_type: str
    skills_used: list[str]
    cached: bool
    grounding_policy: str
    generation_metadata: GenerationMetadata  # model, tokens, latency
    data: dict  # Agent-specific payload
```

### D6: Cache Invalidation Strategy (FR-023)

Dual invalidation: cache is stale if EITHER:
1. `content_version` (SHA-256 of chapter content) differs from cached version
2. `prompt_version` (SHA-256 of prompt template) differs from cached version

Both versions are stored alongside cached content. The existing `personalized_content` and `urdu_translations` tables get a new `prompt_version` column via ALTER TABLE.

### D7: Legacy Endpoint Migration (FR-029)

Existing endpoints become thin proxies:
```python
# backend/src/api/personalize.py (modified)
@router.post("/api/personalize")
async def personalize_legacy(request, ...):
    response = Response(...)
    response.headers["Deprecation"] = "true"
    response.headers["Link"] = '</api/ai/personalize>; rel="successor-version"'
    # Internally call orchestrator
    result = await orchestrator.execute("personalization", payload)
    # Transform envelope to legacy response shape
    return legacy_shape(result)
```

---

## Migration Strategy

### Phase A: Build new architecture alongside existing code
1. Create `backend/src/ai/` module with interfaces, orchestrator, agents, skills, prompt registry
2. Extract current system prompts verbatim into prompt templates
3. Agents internally delegate to existing services (Embedder, Retriever, ChapterRetriever) for non-AI operations
4. New `/api/ai/*` endpoints registered in `main.py`

### Phase B: Wire up and validate
5. Add `agent_execution_logs` table and NeonClient methods
6. Add `prompt_version` column to existing cache tables
7. Test new endpoints produce identical output to current endpoints
8. Side-by-side comparison tests for prompt regression (Risk 2)

### Phase C: Migrate legacy endpoints
9. Convert existing endpoints to thin proxies through Orchestrator
10. Verify existing frontend works unchanged against proxy endpoints
11. Mark `ContentPersonalizer`, `ContentTranslator`, `Generator`, `RAGPipeline`, `ChatKitAgent` as deprecated

### Phase D: Cleanup and observability
12. Add 90-day auto-cleanup for `agent_execution_logs`
13. Verify all direct AI provider calls are eliminated (SC-006)
14. Performance benchmark: cached response latency within 20% (SC-004)
