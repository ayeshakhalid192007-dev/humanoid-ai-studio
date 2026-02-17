# Data Model: Reusable Intelligence Architecture

**Feature**: 003-reusable-intelligence-architecture
**Date**: 2026-02-17

## Entities

### 1. AgentRequest

Runtime request object passed to agents. Not persisted.

```python
@dataclass
class AgentRequest:
    """Immutable request passed to agent.execute()."""
    request_type: str               # "personalization" | "translation" | "rag_chat"
    chapter_slug: str | None        # For personalization/translation
    content: str | None             # Pre-fetched chapter content or custom content
    query: str | None               # For RAG chat
    user_id: str | None             # Authenticated user (personalization)
    user_profile: dict | None       # Profile data (personalization)
    target_language: str | None     # For translation (default: "urdu")
    conversation_history: list[dict] | None  # For RAG chat
    session_id: str | None          # For RAG chat session tracking
    mode: str | None                # "full_book" | "selected_text" (RAG chat)
    selected_text: str | None       # For selected-text mode (RAG chat)
    stream: bool = False            # Whether to stream response
```

### 2. AgentResponse

Runtime response returned by agents. Not persisted directly.

```python
@dataclass
class AgentResponse:
    """Response from agent.execute()."""
    agent_type: str
    content: str                    # The AI-generated content (markdown, answer, etc.)
    cached: bool = False
    model: str = ""
    token_count: int = 0
    latency_ms: int = 0
    skills_used: list[str] = field(default_factory=list)
    skills_detail: list[dict] = field(default_factory=list)
    grounding_policy: str = ""
    agent_data: dict = field(default_factory=dict)
    # Agent-specific data:
    # - personalization: {"profile_used": dict}
    # - translation: {"target_language": str, "source_language": str}
    # - rag_chat: {"citations": list, "retrieved_chunks": list, "query": str}
```

### 3. AIEnvelope

API response wrapper. Serialized to JSON.

```python
class GenerationMetadata(BaseModel):
    model: str
    token_count: int
    latency_ms: int
    prompt_version: str

class AIEnvelope(BaseModel):
    agent_type: str
    skills_used: list[str]
    cached: bool
    grounding_policy: str
    generation_metadata: GenerationMetadata
    data: dict  # Agent-specific payload (from AgentResponse.agent_data + content)
```

### 4. SkillContext

Mutable context passed through the skill chain.

```python
@dataclass
class SkillContext:
    agent_type: str
    grounding_policy: str
    system_prompt: str
    user_message: str
    original_content: str           # Immutable reference for validation
    original_headings: list[str]    # Extracted heading hierarchy (for structure validation)
    original_code_blocks: list[str] # Extracted code blocks (for preservation validation)
    ai_response: str | None = None  # Set after AI call
    metadata: dict = field(default_factory=dict)
    skill_results: list[dict] = field(default_factory=list)
    # Each: {"skill": str, "phase": str, "status": str, "duration_ms": int, "details": str}
```

### 5. PromptTemplate

Loaded from disk at startup.

```python
@dataclass
class PromptTemplate:
    agent_type: str
    content: str                    # The system prompt text
    version: str                    # SHA-256 hash (first 16 hex chars)
    model: str                      # e.g., "gpt-4o-mini"
    temperature: float              # e.g., 0.3
    max_tokens: int                 # e.g., 16000
```

### 6. SkillPhase

Enum for skill execution phase.

```python
class SkillPhase(str, Enum):
    PRE = "pre"
    POST = "post"
    BOTH = "both"
```

---

## Database Schema Changes

### New Table: agent_execution_logs (FR-004, FR-026)

```sql
CREATE TABLE IF NOT EXISTS agent_execution_logs (
    id SERIAL PRIMARY KEY,
    agent_type TEXT NOT NULL,
    grounding_policy TEXT NOT NULL,
    skills_used TEXT[] NOT NULL,
    skills_detail JSONB NOT NULL DEFAULT '[]'::jsonb,
    token_count INTEGER,
    model TEXT NOT NULL,
    latency_ms INTEGER NOT NULL,
    cached BOOLEAN NOT NULL DEFAULT FALSE,
    request_metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_logs_created
    ON agent_execution_logs (created_at);
CREATE INDEX IF NOT EXISTS idx_agent_logs_type
    ON agent_execution_logs (agent_type);
```

**skills_detail JSONB format:**
```json
[
  {
    "skill": "context_boundary",
    "phase": "pre",
    "status": "success",
    "duration_ms": 2
  },
  {
    "skill": "hallucination_prevention",
    "phase": "pre",
    "status": "success",
    "duration_ms": 1
  },
  {
    "skill": "hallucination_prevention",
    "phase": "post",
    "status": "success",
    "duration_ms": 5,
    "details": "grounding_validated: true"
  }
]
```

**request_metadata JSONB format:**
```json
{
  "user_id": "usr_abc123",
  "chapter_slug": "module-1/lesson-1",
  "request_type": "personalization",
  "ip_address": "192.168.1.1"
}
```

### Modified Table: personalized_content

Add `prompt_version` column for dual cache invalidation (FR-023):

```sql
ALTER TABLE personalized_content
    ADD COLUMN IF NOT EXISTS prompt_version TEXT NOT NULL DEFAULT '';
```

Cache lookup changes from:
```sql
-- Current
SELECT ... FROM personalized_content
WHERE user_id = $1 AND chapter_slug = $2
-- Check content_version in application code
```
To:
```sql
-- New: check both versions in query
SELECT ... FROM personalized_content
WHERE user_id = $1
  AND chapter_slug = $2
  AND content_version = $3
  AND prompt_version = $4
```

### Modified Table: urdu_translations

Add `prompt_version` column:

```sql
ALTER TABLE urdu_translations
    ADD COLUMN IF NOT EXISTS prompt_version TEXT NOT NULL DEFAULT '';
```

Cache lookup changes similarly:
```sql
SELECT ... FROM urdu_translations
WHERE chapter_slug = $1
  AND content_version = $2
  AND prompt_version = $3
```

---

## NeonClient Method Additions

### New Methods

```python
# Insert agent execution log
async def insert_agent_execution_log(
    self,
    agent_type: str,
    grounding_policy: str,
    skills_used: list[str],
    skills_detail: list[dict],
    token_count: int | None,
    model: str,
    latency_ms: int,
    cached: bool,
    request_metadata: dict,
) -> int:
    """Insert execution log. Returns log ID. Triggers cleanup if due."""

# Cleanup old logs
async def cleanup_agent_execution_logs(self, retention_days: int = 90) -> int:
    """Delete logs older than retention_days. Returns deleted count."""

# Modified cache lookups (add prompt_version parameter)
async def get_personalized_content(
    self, user_id: str, chapter_slug: str,
    content_version: str, prompt_version: str
) -> dict | None:
    """Returns cached personalization if both versions match."""

async def upsert_personalized_content(
    self, user_id: str, chapter_slug: str,
    personalized_markdown: str, user_profile_snapshot: dict,
    content_version: str, prompt_version: str
) -> None:
    """Upsert with prompt_version."""

async def get_urdu_translation(
    self, chapter_slug: str,
    content_version: str, prompt_version: str
) -> dict | None:
    """Returns cached translation if both versions match."""

async def upsert_urdu_translation(
    self, chapter_slug: str, urdu_markdown: str,
    content_version: str, prompt_version: str
) -> None:
    """Upsert with prompt_version."""
```

---

## Agent-to-Skill Mapping

| Agent | Required Skills | Skill Phases |
|-------|----------------|--------------|
| Personalization | `context_boundary`, `hallucination_prevention`, `knowledge_level`, `educational_tone`, `markdown_preservation` | Pre: context_boundary, hallucination_prevention, knowledge_level, educational_tone / Post: hallucination_prevention, markdown_preservation |
| Translation | `context_boundary`, `hallucination_prevention`, `code_block_detection`, `markdown_preservation` | Pre: context_boundary, hallucination_prevention / Post: hallucination_prevention, code_block_detection, markdown_preservation |
| RAG Reasoning | `context_boundary`, `hallucination_prevention` | Pre: context_boundary, hallucination_prevention / Post: hallucination_prevention |

---

## State Transitions

### Cache Lifecycle

```
Request → Cache Check (content_version + prompt_version)
  ├─ HIT: Return cached → Log (cached=true) → Envelope
  └─ MISS: Pre-skills → AI Call → Post-skills → Cache Upsert → Log (cached=false) → Envelope
```

### Agent Execution Lifecycle

```
Orchestrator.execute()
  ├─ 1. Resolve agent from registry
  ├─ 2. Verify required skills in skill registry
  ├─ 3. Load prompt template + version
  ├─ 4. Build SkillContext
  ├─ 5. Run pre-processing skills (ordered)
  ├─ 6. Agent.execute(request) → AI call
  ├─ 7. Run post-processing skills (ordered)
  ├─ 8. Agent.validate_output()
  ├─ 9. Insert execution log
  └─ 10. Build and return AIEnvelope
```
