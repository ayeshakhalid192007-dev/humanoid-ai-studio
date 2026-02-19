---
id: 001
title: Generate Phase 1 Design Artifacts for Book Publication RAG Chatbot
stage: plan
date: 2026-02-09
surface: agent
model: claude-opus-4-5-20251101
feature: 001-book-publication-rag-chatbot
branch: 001-book-publication-rag-chatbot
user: MASTER
command: none
labels: ["phase-1", "design", "data-model", "api-contracts", "quickstart", "rag-chatbot"]
links:
  spec: specs/001-physical-ai-robotics-platform/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-book-publication-rag-chatbot/data-model.md
  - specs/001-book-publication-rag-chatbot/contracts/chat_api.yaml
  - specs/001-book-publication-rag-chatbot/contracts/health_api.yaml
  - specs/001-book-publication-rag-chatbot/quickstart.md
tests:
  - None (design documentation phase, no code implementation)
---

## Prompt

Generate Phase 1 design artifacts for the book publication & RAG chatbot feature based on the comprehensive plan.md at specs/001-book-publication-rag-chatbot/plan.md and research.md at specs/001-book-publication-rag-chatbot/research.md.

Create these files:

1. specs/001-book-publication-rag-chatbot/data-model.md
   - Follow the entity structure outlined in plan.md Phase 1.1
   - Include CurriculumChunk, ChatSession, ConversationTurn, RateLimitRecord
   - Add validation rules and state transitions
   - Include ER diagram in mermaid format

2. specs/001-book-publication-rag-chatbot/contracts/chat_api.yaml
   - OpenAPI 3.0 spec for POST /chat endpoint
   - Follow the request/response schema from plan.md Phase 1.2

3. specs/001-book-publication-rag-chatbot/contracts/health_api.yaml
   - OpenAPI 3.0 spec for GET /health endpoint
   - Follow the response schema from plan.md Phase 1.2

4. specs/001-book-publication-rag-chatbot/quickstart.md
   - Developer onboarding guide with sections from plan.md Phase 1.3
   - Prerequisites, setup, database init, local dev, testing, deployment

Ensure all files are detailed, complete, and reference the relevant requirements from the spec (FR-xxx codes).

## Response snapshot

Successfully generated all four Phase 1 design artifacts:

### 1. data-model.md (Created)
**Location**: `C:\Users\MASTER\Desktop\physical_ai\specs\001-book-publication-rag-chatbot\data-model.md`

**Content Overview**:
- **Entity Definitions**: Comprehensive specifications for CurriculumChunk, ChatSession, ConversationTurn, and RateLimitRecord
- **CurriculumChunk**: UUID-based chunks stored in Qdrant with 1536-dimension embeddings, metadata (module, lesson, section_title, url), 50-1000 word text segments
- **ChatSession**: Browser session tracking with session_id (UUIDv4), timestamps (created_at, last_active_at), metadata JSONB
- **ConversationTurn**: Query-answer exchanges with retrieved chunks (JSONB), page context, 1-500 char query validation, 30-day retention policy
- **RateLimitRecord**: Sliding window tracking (1-hour window, 20 queries/hour per session)
- **ER Diagram**: Mermaid diagram showing relationships (ChatSession 1:N ConversationTurn, ChatSession 1:N RateLimitRecord, ConversationTurn M:N CurriculumChunk)
- **Data Flow Diagrams**: Chatbot query flow and curriculum embedding pipeline
- **Validation Rules**: Comprehensive input validation table with error messages
- **State Transitions**: ChatSession lifecycle and Neon Postgres auto-suspend behavior
- **Database Initialization Script**: Python asyncpg script for schema setup
- **Capacity Planning**: Qdrant 1GB free tier (3.6MB usage for 500 chunks), Neon 500MB (4MB usage for 1000 turns)
- **Testing Checklist**: 10 data model validation tests

**Requirements Coverage**: FR-035 (Qdrant), FR-037 (Neon), FR-039 (Retrieval threshold >0.7), FR-040 (Context window management), FR-047 (Logging), FR-048 (Rate limiting), FR-055 (sessionStorage persistence), FR-019 (Log retention)

### 2. contracts/chat_api.yaml (Created)
**Location**: `C:\Users\MASTER\Desktop\physical_ai\specs\001-book-publication-rag-chatbot\contracts\chat_api.yaml`

**Content Overview**:
- **OpenAPI 3.0.3 Specification** for POST /chat endpoint
- **Request Schema**:
  - `query` (string, 1-500 chars, sanitized for special tokens)
  - `session_id` (UUID, generated client-side)
  - `page_context` (optional URL, current book page)
  - `selection_text` (optional, max 500 chars, highlighted text)
- **Response 200 Schema**:
  - `answer` (string, max 2000 chars, LLM-generated)
  - `citations` (array, max 5, with module/lesson/section/url)
  - `retrieved_chunks` (array, max 5, with text preview + score)
- **Error Responses**:
  - 400: Bad request (invalid query length, malformed session_id, empty query)
  - 429: Rate limit exceeded (20 queries/hour) with Retry-After header
  - 503: Service unavailable (Neon suspended, OpenAI rate limit, Qdrant outage)
- **Examples**: 3 request examples (basic query, with page context, with text selection) and multiple response examples
- **Detailed Descriptions**: RAG pipeline flow (embed → retrieve → generate → log), performance targets (<3s latency, <200ms overhead), cost estimates (~$0.02/query)

**Requirements Coverage**: FR-034 (FastAPI), FR-038 (Embeddings), FR-039 (Retrieval), FR-041 (Answer generation), FR-042 (Text-selection queries), FR-043 (Citations), FR-044 (Rate limit handling), FR-046 (Input sanitization), FR-047 (Logging), FR-048 (Rate limiting), FR-050 (200ms overhead target)

### 3. contracts/health_api.yaml (Created)
**Location**: `C:\Users\MASTER\Desktop\physical_ai\specs\001-book-publication-rag-chatbot\contracts\health_api.yaml`

**Content Overview**:
- **OpenAPI 3.0.3 Specification** for GET /health endpoint
- **Response 200 Schema**:
  - `status` (enum: healthy/degraded/unhealthy)
  - `services` object with `qdrant`, `neon`, `openai` status (each enum: up/down/degraded)
  - `timestamp` (ISO 8601)
  - `version` (semantic versioning)
- **Response 503 Schema**: Same structure with optional `details` object containing error messages for failed services
- **Examples**:
  - All services healthy
  - Neon suspended (compute exhausted)
  - Qdrant outage (HTTP 503)
  - OpenAI rate limit (degraded status)
- **Health Check Logic**: 2-second timeout per service, tests Qdrant collection existence, Neon SELECT 1 query, OpenAI ping (optional if recently used)

**Requirements Coverage**: FR-034 (FastAPI), FR-035 (Qdrant), FR-037 (Neon), FR-058 (Graceful error messaging)

### 4. quickstart.md (Created)
**Location**: `C:\Users\MASTER\Desktop\physical_ai\specs\001-book-publication-rag-chatbot\quickstart.md`

**Content Overview**:
- **8 Main Sections** covering complete developer onboarding flow
- **Section 1 - Prerequisites**:
  - Required software (Python 3.10+, Node.js 18+, Git 2.30+)
  - Required accounts (Qdrant Cloud, Neon, OpenAI, Railway)
  - System requirements (8GB RAM, 2GB disk, modern browser)
- **Section 2 - Environment Setup**:
  - Git clone and branch checkout
  - Complete `.env` template with all API keys and configuration
  - Backend dependencies (FastAPI, OpenAI SDK, Qdrant client, asyncpg)
  - Frontend dependencies (Docusaurus v3, React 18)
- **Section 3 - Database Initialization**:
  - Neon Postgres schema setup (`python scripts/setup_db.py`)
  - Curriculum embedding pipeline (`python scripts/embed_curriculum.py`)
  - Expected outputs and troubleshooting
- **Section 4 - Local Development**:
  - Start backend server (Uvicorn with hot reload on port 8000)
  - Start frontend server (Docusaurus on port 3000)
  - End-to-end testing flow (6 steps: open page → ask question → verify citations → test persistence → test rate limiting)
- **Section 5 - Testing**:
  - Backend unit tests (pytest)
  - Backend integration tests (API contracts)
  - Frontend tests (Jest + React Testing Library)
  - E2E tests (Playwright)
- **Section 6 - Deployment**:
  - Railway backend deployment (auto-deploy from GitHub)
  - GitHub Pages book deployment (GitHub Actions workflow)
  - Production configuration updates
- **Section 7 - Common Issues**: 6 troubleshooting scenarios with solutions
  - CORS errors
  - Database offline (Neon suspended)
  - OpenAI rate limits
  - Docusaurus build failures
  - Low retrieval scores
  - Railway hour exhaustion
- **Section 8 - Next Steps**: Customization guidance and resource links

**Requirements Coverage**: Plan.md Phase 1.3 (Quickstart sections), FR-021 through FR-060 (all book publication and RAG chatbot requirements referenced throughout setup steps)

## Outcome

- ✅ Impact: Complete Phase 1 design documentation created, enabling Phase 2 task generation. All four deliverables reference plan.md and research.md specifications. Data model includes comprehensive entity definitions, validation rules, state transitions, and ER diagrams. API contracts provide OpenAPI 3.0 specifications with detailed request/response schemas and error handling. Quickstart guide provides 30-45 minute developer onboarding flow with troubleshooting.
- 🧪 Tests: No code tests (design documentation phase). Testing checklists included in data-model.md (10 validation tests) and quickstart.md (unit/integration/E2E test commands).
- 📁 Files: Created 4 files (data-model.md, chat_api.yaml, health_api.yaml, quickstart.md) totaling ~1500 lines of documentation
- 🔁 Next prompts: Run `/sp.tasks` command to generate tasks.md with dependency-ordered implementation tasks based on these Phase 1 artifacts
- 🧠 Reflection: All artifacts are comprehensive and detailed, cross-referencing plan.md, research.md, and spec.md requirements. Data model includes Mermaid diagrams for visualization. API contracts follow OpenAPI 3.0 best practices with extensive examples. Quickstart guide is actionable with specific commands, expected outputs, and troubleshooting sections.

## Evaluation notes (flywheel)

- Failure modes observed: None. All files created successfully with no validation errors.
- Graders run and results (PASS/FAIL): N/A (manual review required for design documentation quality)
- Prompt variant (if applicable): N/A (single-shot documentation generation)
- Next experiment (smallest change to try): Consider adding sequence diagrams to quickstart.md for visual flow representation of end-to-end testing steps
