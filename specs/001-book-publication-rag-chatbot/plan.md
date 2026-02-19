# Implementation Plan: Physical AI & Humanoid Robotics Platform - Book Publication & RAG Chatbot

**Branch**: `001-book-publication-rag-chatbot` | **Date**: 2026-02-09 | **Spec**: [../001-physical-ai-robotics-platform/spec.md](../001-physical-ai-robotics-platform/spec.md)
**Input**: Feature specification from `/specs/001-physical-ai-robotics-platform/spec.md`

**Note**: This plan focuses on the book publication infrastructure and RAG chatbot system (FR-021 through FR-060, User Story 5) as the foundational delivery mechanism for the Physical AI curriculum.

## Summary

Build an interactive learning platform consisting of a Docusaurus-based curriculum book deployed to GitHub Pages with an embedded RAG chatbot assistant. The chatbot uses FastAPI backend with Qdrant vector DB for curriculum embeddings, Neon Postgres for conversation logging, and OpenAI Agents SDK for question answering. Students can ask questions about course content, get instant clarifications with citations, and maintain conversation context across page navigation. This is P0 (highest priority) infrastructure enabling self-service learning and reducing instructor bottlenecks.

## Technical Context

**Language/Version**:


- Backend: Python 3.10+ (FastAPI async framework)
- Frontend: JavaScript/React 18+ (Docusaurus v3.0+, chatbot widget)
- Build: Node.js v18+ (Docusaurus build process)

**Primary Dependencies**:
- **Book**: Docusaurus v3.0+, React 18+, Algolia DocSearch, KaTeX (equations), Mermaid (diagrams)
- **Backend**: FastAPI v0.100+, OpenAI Agents SDK, Qdrant Python client, Neon Postgres client (asyncpg), Pydantic v2.0+, Uvicorn (ASGI server)
- **Infrastructure**: GitHub Actions (CI/CD), GitHub Pages (hosting), Railway (backend deployment)

**Storage**:
- **Vector DB**: Qdrant Cloud free tier (1GB) for curriculum embeddings (~500-800 chunks, 1536 dimensions)
- **Relational DB**: Neon Serverless Postgres free tier (500MB storage, 1 compute hour/month) for conversation history and rate limiting
- **Static Assets**: GitHub Pages CDN for book content, images, downloadable resources

**Testing**:
- **Backend**: pytest (unit + integration), FastAPI TestClient (API contracts)
- **Frontend**: Jest + React Testing Library (chatbot widget), Docusaurus build validation
- **E2E**: Playwright (book navigation, chatbot interaction flows)

**Target Platform**:
- **Book**: Modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+) with JavaScript enabled
- **Backend**: Linux server (Railway deployment, Ubuntu-based containers)
- **Development**: Cross-platform (Windows/Mac/Linux for local development)

**Project Type**: Web application (frontend static site + backend API)

**Performance Goals**:
- Book page load: <2s on 50 Mbps broadband (SC-016)
- Chatbot query latency: <3s for 95th percentile (SC-020), <200ms overhead excluding LLM
- Build time: <5 minutes for full Docusaurus build + deployment (SC-013)
- Vector search: <100ms for curriculum corpus (SC-025)
- Concurrent users: 20 students simultaneously without degradation

**Constraints**:
- **Cost**: <$10 per student per quarter (OpenAI API costs: ~$0.50 embeddings + ~$4.50 chat for 200 queries)
- **Free Tier Limits**: Qdrant 1GB, Neon 500MB + 1 compute hour/month, Railway 500 hours/month + $5 credit
- **Rate Limiting**: 20 queries/hour per browser session (FR-048) to manage API costs
- **Data Retention**: Logs auto-delete 30 days after quarter end (FR-019, FR-047) for privacy compliance
- **Accessibility**: WCAG 2.1 AA compliance for chatbot widget (FR-059)

**Scale/Scope**:
- **Content**: 4 modules, 20-32 lessons, ~500-800 curriculum chunks
- **Users**: 20 students per quarter, ~200 queries per student
- **Conversations**: >1000 conversation turns stored without degradation (SC-024)
- **Deployment**: Single production environment (GitHub Pages + Railway), dev/staging optional

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: PASS (Constitution file is currently a template, no project-specific principles defined yet)

**Note**: The constitution.md file at `.specify/memory/constitution.md` contains only template placeholders. Once project principles are established, this section will be updated with specific gate checks for:
- Code quality standards (testing requirements, documentation)
- Architectural constraints (service limits, abstraction boundaries)
- Security policies (API key management, input sanitization)
- Performance budgets (latency targets, resource limits)

**Assumed Principles** (based on common best practices):
- ✅ Test coverage required for critical paths (RAG pipeline, rate limiting, data persistence)
- ✅ No secrets in source control (API keys via environment variables)
- ✅ Graceful degradation for external service failures (Qdrant, Neon, OpenAI)
- ✅ Accessibility standards (WCAG 2.1 AA for chatbot widget)
- ✅ Cost constraints respected (free tier limits, usage monitoring)

## Project Structure

### Documentation (this feature)

```text
specs/001-book-publication-rag-chatbot/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command) - COMPLETED
├── data-model.md        # Phase 1 output (/sp.plan command) - TO BE GENERATED
├── quickstart.md        # Phase 1 output (/sp.plan command) - TO BE GENERATED
├── contracts/           # Phase 1 output (/sp.plan command) - TO BE GENERATED
│   ├── chat_api.yaml   # OpenAPI spec for POST /chat endpoint
│   └── health_api.yaml # OpenAPI spec for GET /health endpoint
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Web application structure: Docusaurus frontend + FastAPI backend

book/                           # Docusaurus curriculum book
├── docs/                       # Curriculum markdown content
│   ├── module1-ros2/          # Module 1: ROS 2 Middleware
│   ├── module2-simulation/    # Module 2: Gazebo/Unity simulation
│   ├── module3-perception/    # Module 3: VSLAM + Nav2
│   └── module4-vla/           # Module 4: Voice-to-action pipeline
├── src/
│   ├── components/            # React components
│   │   └── ChatbotWidget/    # Embedded RAG chatbot component
│   ├── css/                   # Custom styling
│   └── pages/                 # Custom pages (landing, about)
├── static/
│   ├── img/                   # Images, diagrams, screenshots
│   └── resources/             # Downloadable files (URDF, launch scripts)
├── docusaurus.config.js       # Docusaurus configuration
├── sidebars.js                # Navigation structure
└── package.json               # Node.js dependencies

backend/                        # FastAPI chatbot backend
├── src/
│   ├── api/                   # API endpoints
│   │   ├── chat.py           # POST /chat (main RAG pipeline)
│   │   ├── health.py         # GET /health (service status)
│   │   └── rate_limit.py     # Rate limiting middleware
│   ├── models/                # Pydantic data models
│   │   ├── query.py          # ChatQuery, ChatResponse schemas
│   │   └── embedding.py      # EmbeddingChunk, VectorSearchResult
│   ├── services/              # Business logic
│   │   ├── rag_pipeline.py   # Retrieve → Augment → Generate
│   │   ├── embedder.py       # OpenAI embedding generation
│   │   ├── retriever.py      # Qdrant vector search
│   │   └── generator.py      # OpenAI Agents SDK integration
│   ├── db/                    # Database clients
│   │   ├── qdrant_client.py  # Qdrant connection + operations
│   │   └── neon_client.py    # Postgres connection + queries
│   └── config.py              # Environment variables, settings
├── tests/
│   ├── unit/                  # Unit tests for services
│   ├── integration/           # API contract tests
│   └── e2e/                   # End-to-end RAG pipeline tests
├── scripts/
│   ├── embed_curriculum.py    # One-time: embed docs → Qdrant
│   └── setup_db.py            # Initialize Neon Postgres schema
├── requirements.txt           # Python dependencies
└── main.py                    # FastAPI app entry point

.github/
└── workflows/
    ├── deploy-book.yml        # CI/CD: build + deploy to GitHub Pages
    └── deploy-backend.yml     # CI/CD: deploy FastAPI to Railway

scripts/                        # Utility scripts
├── validate_frontmatter.py    # Pre-commit: check markdown YAML
└── check_links.py             # Pre-commit: validate internal links
```

**Structure Decision**: Web application with separated frontend (Docusaurus static site) and backend (FastAPI API). This separation enables:
- **Independent Deployment**: Book deploys to GitHub Pages (free, CDN), backend to Railway (auto-scaling)
- **Technology Alignment**: Docusaurus optimized for docs, FastAPI for async Python APIs
- **Development Workflow**: Curriculum authors work in `book/docs/` markdown, engineers maintain `backend/` Python
- **Testing Isolation**: Frontend tests (Docusaurus build, React components) separate from backend tests (RAG pipeline, API contracts)

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: No violations detected. All complexity justified by functional requirements:

| Component | Complexity | Justification |
|-----------|------------|---------------|
| Two-tier architecture (static + API) | Docusaurus (frontend) + FastAPI (backend) | Required: Static site cannot perform vector search or call OpenAI API (FR-035, FR-036, FR-038). Backend needed for RAG pipeline, rate limiting, logging |
| Three external services | Qdrant + Neon + OpenAI | Required: Vector DB (FR-035), relational DB (FR-037, FR-047), LLM API (FR-041). Free tier constraints prevent single-service solution |
| OpenAI Agents SDK | Structured LLM orchestration | Required: Native streaming (FR-053), function calling for citations (FR-043), context window management (FR-040). Simpler alternatives (raw API calls) lack these features |
| sessionStorage + Postgres persistence | Dual persistence layer | Required: Frontend needs cross-page context (FR-055), backend needs logging for analytics (FR-047). Single-layer insufficient for both requirements |

**Rejected Simplifications**:
- ❌ Single-page static site (no backend): Cannot perform RAG retrieval or rate limiting
- ❌ Single database (only Postgres): No vector search capability, would require pgvector extension with worse performance than Qdrant
- ❌ LangChain instead of OpenAI SDK: Adds abstraction complexity, slower for educational use case per research findings
- ❌ Client-side only persistence (sessionStorage): Loses analytics data needed for curriculum gap analysis (FR-047)

---

## Phase 0: Research & Clarifications



**Status**: ✅ COMPLETED (see research.md)

All technology decisions have been researched and documented in `research.md`. Key findings:
- ROS 2 Humble selected (LTS until 2027)
- Docusaurus v3 + GitHub Pages for book publishing
- FastAPI + Qdrant + Neon + OpenAI Agents SDK for RAG chatbot
- Railway free tier for backend deployment
- sessionStorage + Postgres for conversation persistence
- All "NEEDS CLARIFICATION" items from spec resolved

**No further research required**. Proceeding to Phase 1.

---

## Phase 1: Design & Contracts

**Deliverables**:
1. `data-model.md` - Entity definitions and relationships
2. `contracts/` - API specifications (OpenAPI YAML)
3. `quickstart.md` - Developer onboarding guide
4. Updated agent context file

### 1.1 Data Model (`data-model.md`)

**Entities to Define**:

**Book Content Entities**:
- **CurriculumChunk**: Embedded text segment with metadata
  - Fields: chunk_id (UUID), text (string, max 1000 words), module (string), lesson (string), section_title (string), url (string), embedding (vector[1536])
  - Relationships: Stored in Qdrant, referenced by RAG queries

**Chatbot Entities**:
- **ChatSession**: Browser session for rate limiting and conversation tracking
  - Fields: session_id (UUID), created_at (timestamp), last_active_at (timestamp)
  - Relationships: Has many ConversationTurns

- **ConversationTurn**: Single question-answer exchange
  - Fields: turn_id (serial), session_id (UUID FK), query (text, max 500 chars), response (text), retrieved_chunks (JSONB array of chunk IDs + scores), timestamp (timestamptz), page_context (text, current book page URL), metadata (JSONB: user-agent, selection text if any)
  - Relationships: Belongs to ChatSession

- **RateLimitRecord**: Query count tracking for rate limiting
  - Fields: session_id (UUID FK), query_timestamp (timestamptz)
  - Relationships: Belongs to ChatSession
  - Note: Uses sliding window (1 hour), old records auto-deleted

**Validation Rules**:
- ChatQuery: 1-500 chars, no special tokens (`<|endoftext|>`, etc.)
- ChunkRetrieval: Minimum cosine similarity > 0.7 (FR-039)
- SessionStorage: Max 500 message pairs before cleanup
- Rate Limit: 20 queries/hour per session_id (FR-048)

**State Transitions**:
- ChatSession: created → active (on first query) → idle (after 5 min) → expired (on tab close, sessionStorage cleared)
- Neon Database: active → auto-suspended (after 5 min idle) → resumed (on next query, <1s)

### 1.2 API Contracts (`contracts/`)

**File: `chat_api.yaml`** (OpenAPI 3.0 spec)
- **Endpoint**: `POST /chat`
- **Request Body**:
  ```json
  {
    "query": "string (1-500 chars)",
    "session_id": "UUID",
    "page_context": "string (current book page URL, optional)",
    "selection_text": "string (highlighted text, optional, max 500 chars)"
  }
  ```
- **Response 200**:
  ```json
  {
    "answer": "string",
    "citations": [
      {
        "module": "string",
        "lesson": "string",
        "section": "string",
        "url": "string (clickable link)"
      }
    ],
    "retrieved_chunks": [
      {
        "text": "string (preview, max 200 chars)",
        "score": "float (cosine similarity)"
      }
    ]
  }
  ```
- **Response 429**: `{"detail": "Rate limit: 20 queries/hour. Try again later."}`
- **Response 503**: `{"detail": "Chatbot temporarily offline (database maintenance)."}`

**File: `health_api.yaml`** (OpenAPI 3.0 spec)
- **Endpoint**: `GET /health`
- **Response 200**:
  ```json
  {
    "status": "healthy",
    "services": {
      "qdrant": "up",
      "neon": "up",
      "openai": "up"
    },
    "timestamp": "ISO 8601 string"
  }
  ```
- **Response 503**: Service unavailable with failed service details

### 1.3 Developer Quickstart (`quickstart.md`)

**Sections**:
1. **Prerequisites**: Python 3.10+, Node.js 18+, accounts (Qdrant Cloud, Neon, OpenAI, Railway)
2. **Environment Setup**:
   - Clone repo
   - Create `.env` file with API keys (template provided)
   - Install dependencies: `pip install -r backend/requirements.txt`, `cd book && npm install`
3. **Database Initialization**:
   - Run `python backend/scripts/setup_db.py` (creates Neon schema)
   - Run `python backend/scripts/embed_curriculum.py` (embeds docs → Qdrant)
4. **Local Development**:
   - Start backend: `cd backend && uvicorn main:app --reload`
   - Start book: `cd book && npm start`
   - Access: http://localhost:3000 (book), http://localhost:8000/docs (API docs)
5. **Testing**:
   - Backend: `cd backend && pytest`
   - Frontend: `cd book && npm test`
   - E2E: `cd backend && pytest tests/e2e`
6. **Deployment**:
   - Backend: Push to Railway (auto-deploys from main branch)
   - Book: GitHub Actions auto-deploys to GitHub Pages on push to main
7. **Common Issues**: Troubleshooting guide (API keys, CORS, cold start latency)

### 1.4 Agent Context Update

Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude` to update the agent context file with:
- **Technologies**: Docusaurus v3, FastAPI v0.100+, Qdrant Cloud, Neon Postgres, OpenAI Agents SDK, Railway
- **Project Structure**: book/, backend/, specs/001-book-publication-rag-chatbot/
- **Key Files**: plan.md, research.md, data-model.md, quickstart.md
- **API Endpoints**: POST /chat, GET /health

---

## Phase 2: Tasks Generation (Out of Scope for /sp.plan)

**Note**: Task generation is handled by the separate `/sp.tasks` command, NOT by `/sp.plan`.

The `/sp.tasks` command will:
1. Read spec.md, plan.md, data-model.md, contracts/
2. Generate tasks.md with dependency-ordered implementation tasks
3. Each task will include:
   - Acceptance criteria
   - Test cases
   - File references (specific paths from Project Structure above)
   - Dependencies (which tasks must complete first)

**Estimated Task Categories** (for reference, not generated here):
- Setup tasks (repo structure, dependencies, CI/CD)
- Backend tasks (FastAPI endpoints, RAG pipeline, database clients)
- Frontend tasks (Docusaurus setup, chatbot widget, styling)
- Integration tasks (CORS, error handling, end-to-end flows)
- Testing tasks (unit, integration, E2E)
- Deployment tasks (Railway, GitHub Pages, monitoring)

**Command ends after Phase 1 completion**. User must run `/sp.tasks` separately to generate tasks.md.

---

## Follow-Up Actions

After this command completes:

1. ✅ **Phase 0 Complete**: research.md already exists with all technology decisions
2. ⏳ **Phase 1 Pending**: Generate data-model.md, contracts/, quickstart.md (next steps below)
3. ⏳ **Phase 2 Pending**: Run `/sp.tasks` command separately to generate tasks.md

**Next Steps** (after Phase 1 artifacts generated):
- Review data-model.md for entity definitions
- Validate API contracts in contracts/ directory
- Test quickstart.md by following setup steps
- Run `/sp.tasks` to generate implementation tasks
- Consider creating ADR for significant architectural decisions (use `/sp.adr <title>`)

**Risks & Open Questions**:
- ⚠️ Free tier exhaustion: Implement usage monitoring early (Railway hours, Qdrant storage, Neon compute)
- ⚠️ Cold start latency: Railway 10s cold start may frustrate users; consider health check pings
- ⚠️ Constitution undefined: No project-specific principles yet; may need retroactive ADRs for decisions made

**Success Metrics from Spec**:
- SC-013: Book deploys in <5 min ✅ (GitHub Actions workflow)
- SC-018: Chatbot >85% accuracy ⚠️ (requires test set creation + validation)
- SC-020: Chatbot <3s latency ⚠️ (requires performance testing)
- SC-026: Conversation context persists ✅ (sessionStorage implementation)
