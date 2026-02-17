# Feature Specification: Reusable Intelligence Architecture

**Feature Branch**: `003-reusable-intelligence-architecture`
**Created**: 2026-02-17
**Status**: Draft
**Input**: User description: "Reusable Intelligence Architecture Using Subagents and Agent Skills"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - AI Orchestrator Routes Personalization Requests (Priority: P1)

A learner clicks "Personalize" on a chapter page. The frontend calls
`POST /api/ai/personalize`. The backend AI Orchestrator receives the
request, identifies it as a personalization task, selects the
Personalization Agent, composes the required skills (Markdown
Preservation, Knowledge Level Adjustment, Educational Tone Control,
Hallucination Prevention), executes the agent pipeline, validates the
output, caches the result, and returns personalized markdown to the
frontend.

**Why this priority**: The Orchestrator is the backbone of the
architecture. Personalization is the most profile-dependent feature,
exercising context boundary enforcement, skill composition, and the
full agent lifecycle. Getting this right proves the entire
architecture works.

**Independent Test**: Can be fully tested by sending a personalization
request with a known user profile and chapter slug, then verifying the
returned markdown preserves structure, adapts to the profile, and is
cached in the database.

**Acceptance Scenarios**:

1. **Given** a logged-in user with a known profile and a chapter slug,
   **When** `POST /api/ai/personalize` is called,
   **Then** the Orchestrator selects the Personalization Agent, the
   agent composes Markdown Preservation + Knowledge Level Adjustment +
   Educational Tone Control + Hallucination Prevention skills, and the
   response is structurally valid markdown matching the original chapter
   headings.

2. **Given** a cached personalized chapter for the same user and slug,
   **When** `POST /api/ai/personalize` is called again,
   **Then** the cached version is returned without invoking the AI
   pipeline, and `cached: true` is indicated in the response.

3. **Given** a request with missing or invalid authentication,
   **When** `POST /api/ai/personalize` is called,
   **Then** the system returns HTTP 401 with a clear error message.

---

### User Story 2 - AI Orchestrator Routes Translation Requests (Priority: P2)

A visitor clicks "Translate to Urdu" on a chapter page. The frontend
calls `POST /api/ai/translate`. The Orchestrator identifies it as a
translation task, selects the Translation Agent, composes the required
skills (Markdown Preservation, Code Block Detection, Context Boundary
Enforcement), executes the agent pipeline, validates output, caches,
and returns Urdu markdown.

**Why this priority**: Translation is the second core AI feature and
validates that a different agent can be routed through the same
Orchestrator with a different skill composition, proving the
architecture is genuinely reusable.

**Independent Test**: Can be tested by sending a translation request
with a chapter slug and verifying the returned content is Urdu
markdown with preserved code blocks and formatting.

**Acceptance Scenarios**:

1. **Given** a chapter slug for an existing chapter,
   **When** `POST /api/ai/translate` is called,
   **Then** the Orchestrator selects the Translation Agent, composes
   Markdown Preservation + Code Block Detection skills, and the
   response is valid Urdu markdown with all code blocks unchanged.

2. **Given** a custom `content` field with personalized markdown,
   **When** `POST /api/ai/translate` is called with the content,
   **Then** the Translation Agent translates the provided content
   (personalized-to-Urdu path) without chapter retrieval.

3. **Given** a chapter that has already been translated and cached,
   **When** `POST /api/ai/translate` is called,
   **Then** the cached version is returned without invoking the AI.

---

### User Story 3 - AI Orchestrator Routes Chat/RAG Requests (Priority: P3)

A user types a question in the book chatbot. The frontend calls
`POST /api/ai/chat`. The Orchestrator identifies it as a RAG query,
selects the RAG Reasoning Agent, composes Hallucination Prevention +
Context Boundary Enforcement skills, executes the retrieval and
generation pipeline, and returns a citation-aware answer.

**Why this priority**: The RAG chatbot is the third AI feature.
Routing it through the Orchestrator completes the unification of all
existing AI capabilities under the single intelligence architecture.

**Independent Test**: Can be tested by sending a chat query and
verifying the response contains an answer grounded in retrieved
curriculum context with citations.

**Acceptance Scenarios**:

1. **Given** a user query about curriculum content,
   **When** `POST /api/ai/chat` is called,
   **Then** the Orchestrator selects the RAG Reasoning Agent, the
   agent retrieves relevant chunks from the vector store, generates a
   grounded answer, and the response includes citations referencing
   source chunks.

2. **Given** a query with no relevant curriculum content,
   **When** `POST /api/ai/chat` is called,
   **Then** the agent returns a response indicating insufficient
   context rather than fabricating an answer.

3. **Given** a query containing potential prompt injection tokens,
   **When** `POST /api/ai/chat` is called,
   **Then** the Context Boundary Enforcement skill sanitizes the input
   before processing.

4. **Given** a user query sent to `POST /api/ai/chat/stream`,
   **When** the RAG Reasoning Agent generates a response,
   **Then** the Orchestrator delivers tokens incrementally via SSE,
   preserving the existing streaming UX.

---

### User Story 4 - Centralized Prompt Management (Priority: P4)

A developer needs to update the personalization system prompt. They
edit a single prompt template file in the centralized prompt registry
rather than searching through scattered service classes. The change
applies to all future personalization requests without modifying agent
or orchestrator code.

**Why this priority**: Centralizing prompts eliminates the current
pattern of system prompts embedded in service class constructors,
enabling non-developer prompt iteration and consistent prompt
versioning.

**Independent Test**: Can be tested by modifying a prompt template
file, restarting the server, and verifying the new prompt is used in
the corresponding agent's output.

**Acceptance Scenarios**:

1. **Given** a prompt template file for the Personalization Agent,
   **When** the template content is modified,
   **Then** subsequent personalization requests use the updated prompt
   without code changes.

2. **Given** a prompt template with a skill composition directive,
   **When** the agent processes a request,
   **Then** the directive is applied and traceable in the response
   metadata.

---

### User Story 5 - Extensibility: Adding a New Agent (Priority: P5)

A developer needs to add a new AI capability (e.g., quiz generation).
They create a new agent class following the established agent
interface, register it with the Orchestrator, compose existing skills,
and add a new API endpoint. No changes are needed to the Orchestrator
core, existing agents, or skill modules.

**Why this priority**: Extensibility is the long-term value
proposition. If adding a new agent requires modifying existing code,
the architecture has failed its reusability goal.

**Independent Test**: Can be tested by creating a minimal new agent
that composes existing skills and verifying it can be registered and
invoked through the Orchestrator without modifying any existing files.

**Acceptance Scenarios**:

1. **Given** the agent interface and skill registry,
   **When** a developer creates a new agent class and registers it,
   **Then** the Orchestrator can route requests to the new agent
   without modifications to existing agent or orchestrator code.

2. **Given** existing skills in the registry,
   **When** the new agent composes a subset of skills,
   **Then** the skills function correctly in the new agent context.

---

### Edge Cases

- What happens when the Orchestrator receives a request type that
  matches no registered agent? System MUST return HTTP 400 with an
  error identifying the unrecognized request type.
- How does the system handle an agent that times out during AI
  generation? System MUST enforce a configurable timeout per agent
  type and return HTTP 504 with a descriptive error.
- What happens when a skill fails during composition (e.g., content
  exceeds token limits)? System MUST return HTTP 422 with details
  about which skill failed and why.
- How does the system behave when the AI provider returns an error?
  System MUST propagate a user-friendly error message without
  exposing provider details, and log the full error internally.
- What happens when cached content exists but the underlying chapter
  content has changed? System MUST detect stale cache via content
  version hash and regenerate.

## Clarifications

### Session 2026-02-17

- Q: Should the AI Orchestrator support SSE streaming responses for the chat agent? → A: Orchestrator MUST support streaming for the RAG chat agent, preserving existing SSE behavior. Streaming is specific to the chat agent; personalization and translation remain request/response only.
- Q: Should skills operate as pre-processing, post-processing, or both? → A: Dual-phase. Each skill declares whether it applies pre-processing (before AI call), post-processing (after AI call), or both. The Orchestrator runs skills in the correct phase.
- Q: What happens to legacy endpoints once new /api/ai/* endpoints are live? → A: Legacy endpoints (/api/personalize, /api/translate, /chat/v2) become thin proxies that route through the Orchestrator internally. They are deprecated but not removed, allowing gradual frontend migration.
- Q: How long should agent execution logs be retained? → A: 90 days retention with automatic cleanup. Entries older than 90 days are deleted automatically.
- Q: Should the Orchestrator and agents be singletons or per-request instances? → A: Singleton. Orchestrator and all agents are created once at startup and reused across requests, matching the existing service pattern. Agents are stateless per-request by design.
- Q: Must ALL AI calls go exclusively through the Orchestrator? → A: Strict enforcement. ALL AI provider calls in the entire backend MUST go through the Orchestrator. Zero direct AI provider calls permitted anywhere in the codebase. Existing direct calls in ContentPersonalizer, ContentTranslator, Generator, and ChatKitAgent MUST be migrated.
- Q: Should all agents return a unified response schema or independent shapes? → A: Common envelope + agent-specific payload. All agents return a unified metadata wrapper (agent_type, skills_used, cached, latency, tokens) with a typed `data` field containing agent-specific content (e.g., chat data includes citations, personalization includes profile_used).
- Q: Should individual skill execution be logged? → A: Per-skill status logging. Each skill's success/fail status and duration MUST be logged per request. Full content (input/output) is NOT logged to minimize storage overhead.
- Q: Must all agents enforce strict context grounding? → A: Per-agent grounding policy. RAG agent = strict grounding (only output information present in retrieved context, no fabrication). Personalization agent = structural fidelity (preserve chapter headings and structure, but allowed to adapt explanations and examples). Translation agent = semantic fidelity (preserve meaning accurately, transform language).
- Q: Should cached AI outputs be invalidated when prompt templates change? → A: Dual invalidation. Cache is stale if EITHER the source content version hash OR the prompt template version changes. Both factors MUST be checked during cache lookup.

## Requirements *(mandatory)*

### Functional Requirements

**Orchestrator Module**

- **FR-001**: System MUST provide a central AI Orchestrator module
  that receives all AI feature requests and routes them to the
  appropriate agent based on request type. ALL AI provider calls in
  the backend MUST go through the Orchestrator with zero exceptions.
  Existing direct AI calls MUST be migrated and removed.
- **FR-002**: System MUST enforce strict context boundaries between
  chapter content, user profile data, and system instructions within
  the Orchestrator, preventing cross-contamination.
- **FR-003**: System MUST validate agent output structure before
  returning responses, rejecting malformed output with an appropriate
  error.
- **FR-004**: System MUST log each AI request with: agent type,
  skills composed, token usage, overall latency, cache hit/miss
  status, and per-skill execution detail (each skill's success/fail
  status and individual duration). Full skill input/output content
  MUST NOT be logged.

**Agent Architecture**

- **FR-005**: System MUST define a common agent interface that all
  agents implement, including: execute(request) returning an
  AgentResponse, get_required_skills(), and validate_output(response)
  returning a boolean. The Orchestrator and all agents MUST be
  singleton instances created at startup and reused across requests.
  All per-request state MUST be passed via the request object, not
  stored on the instance.
- **FR-006**: System MUST implement a Personalization Agent that
  accepts chapter content and user profile, adapts content depth and
  examples based on the profile, and outputs structured markdown
  preserving the original chapter heading hierarchy.
- **FR-007**: System MUST implement a Translation Agent that accepts
  markdown content and target language, translates prose while
  preserving code blocks, markdown formatting, and technical
  terminology.
- **FR-008**: System MUST implement a RAG Reasoning Agent that
  accepts a user query, retrieves relevant context from the vector
  store, and generates a citation-aware response strictly grounded
  in the retrieved context.
- **FR-009**: Each agent MUST declare which skills it requires at
  initialization time, and the Orchestrator MUST verify all
  required skills are available before execution.

**Skill System**

- **FR-010**: System MUST define modular, composable skills as
  independent units that can be attached to any agent. Each skill
  MUST implement a common skill interface and declare its execution
  phase: pre-processing (before AI call), post-processing (after AI
  call), or both. The Orchestrator MUST execute pre-processing skills
  before the AI call and post-processing skills after, in declared
  order.
- **FR-011**: System MUST implement a Markdown Preservation skill
  that ensures output retains the input's heading structure,
  formatting, and code block integrity.
- **FR-012**: System MUST implement a Context Boundary Enforcement
  skill that sanitizes inputs by stripping dangerous tokens and
  preventing prompt injection.
- **FR-013**: System MUST implement a Hallucination Prevention skill
  with per-agent grounding policies: RAG agent applies strict
  grounding (only output information present in retrieved context,
  flag any fabricated references); Personalization agent applies
  structural fidelity (preserve chapter heading hierarchy and topic
  scope, but permit adapted explanations and examples);
  Translation agent applies semantic fidelity (preserve meaning
  accurately, flag significant semantic drift).
- **FR-014**: System MUST implement an Educational Tone Control skill
  that adjusts language to be pedagogically appropriate for the
  target audience.
- **FR-015**: System MUST implement a Knowledge Level Adjustment
  skill that adapts content complexity based on a user's declared
  proficiency level (beginner, intermediate, advanced).
- **FR-016**: System MUST implement a Code Block Detection skill
  that identifies and preserves code blocks during content
  transformation operations.

**Prompt Management**

- **FR-017**: System MUST store all system prompts in a centralized
  prompt registry (structured files or configuration), not inline
  in agent code.
- **FR-018**: System MUST support prompt versioning so that prompt
  changes are traceable and previous versions can be referenced.
  Prompt version identifiers MUST be stored alongside cached AI
  outputs to enable dual cache invalidation (FR-023).

**API Layer**

- **FR-019**: System MUST expose `POST /api/ai/personalize` that
  routes through the Orchestrator to the Personalization Agent.
  This endpoint replaces the current direct-call pattern in the
  existing `/api/personalize` endpoint.
- **FR-020**: System MUST expose `POST /api/ai/translate` that
  routes through the Orchestrator to the Translation Agent.
  This endpoint replaces the current direct-call pattern in the
  existing `/api/translate` endpoint.
- **FR-021**: System MUST expose `POST /api/ai/chat` that routes
  through the Orchestrator to the RAG Reasoning Agent. This
  endpoint replaces the current direct-call patterns in the
  existing `/chat/v2` endpoint.
- **FR-022**: All `/api/ai/*` endpoints MUST return a common response
  envelope containing: agent_type, skills_used, cached flag, and
  generation metadata (model, tokens, latency). The envelope MUST
  include a typed `data` field containing agent-specific payload
  (e.g., personalization data includes profile_used; chat data
  includes citations and retrieved_chunks). The envelope schema MUST
  be consistent across all agents.
- **FR-028**: System MUST support SSE streaming for the RAG chat
  agent via `POST /api/ai/chat/stream`, preserving the existing
  Server-Sent Events behavior. The Orchestrator MUST handle both
  streaming and non-streaming agent execution modes.
- **FR-029**: Existing legacy endpoints (`/api/personalize`,
  `/api/translate`, `/chat/v2`, `/chat/stream`) MUST be retained as
  thin proxies that internally route through the Orchestrator. These
  endpoints are deprecated and MUST return a `Deprecation` response
  header indicating the replacement `/api/ai/*` endpoint.

**Caching & Safety**

- **FR-023**: System MUST check cache before invoking any agent and
  return cached responses when available and fresh. Freshness MUST
  be determined by matching BOTH source content version hash AND
  prompt template version. A change to either MUST invalidate the
  cached entry and trigger regeneration.
- **FR-024**: System MUST enforce per-agent rate limits using the
  existing sliding-window pattern.
- **FR-025**: System MUST sanitize all user-provided input at the
  Orchestrator level before passing to any agent.

**Database**

- **FR-026**: System MUST store agent execution metadata (agent type,
  skills used, token count, latency, timestamp) in a dedicated
  table for observability and cost tracking.
- **FR-027**: System MUST retain backward compatibility with existing
  `personalized_content` and `urdu_translations` cache tables.
- **FR-030**: System MUST automatically delete agent execution log
  entries older than 90 days. Cleanup MUST run on a scheduled basis
  without manual intervention.

### Key Entities

- **Agent**: A specialized AI processing unit with a declared skill
  set, prompt template, and output validator. Identified by a unique
  agent type string (e.g., "personalization", "translation", "rag").
- **Skill**: A composable processing unit that transforms or
  constrains agent context. Identified by name, with an apply()
  method.
- **Orchestrator**: The central routing and composition module that
  maps request types to agents, composes skills, and manages the
  execution lifecycle.
- **Prompt Template**: A versioned system prompt stored in the prompt
  registry, referenced by agent type and version.
- **Agent Execution Log**: A record of each AI invocation including
  agent type, skills composed, tokens consumed, latency, cache
  status, and timestamp.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All three existing AI features (personalization,
  translation, RAG chat) function through the Orchestrator with
  identical or better response quality compared to the current
  direct-call implementation.
- **SC-002**: Adding a new agent type requires creating at most 2 new
  files (agent class + prompt template) and modifying 1 registry
  file, with zero changes to existing agent or orchestrator code.
- **SC-003**: All system prompts are stored in the centralized prompt
  registry with zero inline prompt strings remaining in agent or
  service code.
- **SC-004**: The system handles 50 concurrent AI requests without
  error, with response times within 20% of the current direct-call
  latency for cached responses.
- **SC-005**: Every AI request generates an execution log entry
  containing agent type, skills used, token count, and latency,
  queryable for cost analysis.
- **SC-006**: No raw AI provider API calls exist outside the agent
  execution layer. All AI interactions are mediated through agents
  and skills.
- **SC-007**: The system correctly rejects requests containing prompt
  injection patterns with zero false negatives on the standard
  injection test suite.

## Scope & Boundaries

### In Scope

- AI Orchestrator module with agent routing
- Three agents: Personalization, Translation, RAG Reasoning
- Six composable skills
- Centralized prompt registry with versioning
- Structured `/api/ai/*` endpoints
- Agent execution logging table
- Migration of existing AI features to the new architecture
- Backward compatibility with existing cache tables and frontend
- Legacy endpoint deprecation: existing endpoints become thin proxies
  routing through the Orchestrator with `Deprecation` headers

### Out of Scope

- Frontend UI changes (existing ChapterToolbar and chatbot UI remain
  unchanged; they just call new endpoints)
- Changes to the auth server or auth flow
- Changes to the vector store schema or ingestion pipeline
- Real-time agent collaboration (agents operate independently)
- A/B testing framework for prompt variants
- User-facing agent selection or configuration
- Multi-model support (all agents use the configured model)
- Agent memory or cross-request state (each request is stateless)

## Assumptions

- The existing AI model will continue to be used for all agents.
  Model selection is a configuration concern, not an architectural
  one.
- The existing vector store collection schema is stable and sufficient
  for RAG retrieval needs.
- The existing database connection pooling is adequate for the
  additional logging writes.
- Skills operate as synchronous, dual-phase transformations: each
  skill declares whether it runs pre-processing (modifying prompt/
  context before the AI call), post-processing (validating/
  transforming AI output), or both. Skills are not separate AI calls.
- The frontend will be updated to call the new `/api/ai/*` endpoints,
  but the response format will be backward-compatible with the
  existing response shapes.
- Rate limit configuration values remain as currently defined
  (personalization: 10/hr, translation: 20/hr, chat: 20/hr).

## Dependencies

- **AI Provider API**: All agents depend on the AI Chat Completions
  API for generation.
- **Vector Store**: The RAG Reasoning Agent depends on vector search
  for retrieval.
- **Database**: Caching, rate limiting, session management, and agent
  execution logging depend on the database.
- **Auth Server**: The Personalization Agent requires authenticated
  user sessions for profile retrieval.
- **Existing Feature 002**: The current personalization, translation,
  and cache table schemas from Feature 002 must be preserved.

## Risks

- **Risk 1: Latency overhead from Orchestrator routing**. The
  additional routing and skill composition layer adds processing
  time. Mitigation: Skills are lightweight in-process transformations,
  not separate AI calls. Benchmark against current direct-call
  latency.
- **Risk 2: Prompt regression during migration**. Moving prompts from
  inline to centralized registry may introduce subtle prompt changes.
  Mitigation: Extract prompts verbatim from existing code, then
  validate output quality with side-by-side comparison tests.
- **Risk 3: Over-abstraction**. The agent/skill architecture adds
  indirection. Mitigation: Keep the skill interface minimal
  (apply(context) returning context) and avoid premature
  generalization. Only add skills that are actually shared across
  agents.
