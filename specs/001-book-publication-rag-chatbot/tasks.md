---
description: "Implementation tasks for Book Publication & RAG Chatbot feature"
---

# Tasks: Book Publication & RAG Chatbot

**Input**: Design documents from `C:\Users\MASTER\Desktop\physical_ai\specs\001-book-publication-rag-chatbot\`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story. Primary focus is User Story 5 (RAG Chatbot) as P0 infrastructure, followed by curriculum content creation phases.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US5 = User Story 5 - RAG Chatbot)
- Include exact file paths in descriptions

## Path Conventions

This is a web application project:
- **Frontend**: `book/` (Docusaurus static site)
- **Backend**: `backend/` (FastAPI API)
- **Specs**: `specs/001-book-publication-rag-chatbot/`
- **CI/CD**: `.github/workflows/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, repository structure, and dependency management

- [X] T001 Create project directory structure per plan.md with book/, backend/, .github/workflows/, scripts/ folders
- [X] T002 [P] Create .env.example template with all required environment variables (OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY, NEON_DATABASE_URL, BACKEND_CORS_ORIGINS)
- [X] T003 [P] Create .gitignore file excluding .env, venv/, node_modules/, build/, __pycache__/, .DS_Store
- [X] T004 Create backend/requirements.txt with FastAPI 0.100+, Uvicorn, OpenAI 1.x, Qdrant-client, asyncpg, Pydantic 2.0+, python-dotenv, httpx, pytest, pytest-asyncio
- [X] T005 Create book/package.json with Docusaurus 3.x, React 18+, clsx, prism-react-renderer dependencies
- [X] T006 [P] Create README.md in project root with quickstart reference and link to specs/001-book-publication-rag-chatbot/quickstart.md
- [X] T007 [P] Configure Python linting and formatting tools (black, flake8, mypy) in backend/.flake8, backend/.mypy.ini

**Checkpoint**: Project structure created, dependencies defined

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story implementation can begin

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database & Storage Setup

- [X] T008 Create Neon Postgres schema initialization script in backend/scripts/setup_db.py implementing chat_sessions, conversation_turns, rate_limit_records tables with indexes per data-model.md
- [X] T009 Create Qdrant collection initialization script in backend/scripts/init_qdrant.py with 1536-dimension HNSW index for curriculum collection
- [X] T010 [P] Create backend/src/db/neon_client.py with asyncpg connection pool, query helpers for session/conversation/rate-limit operations
- [X] T011 [P] Create backend/src/db/qdrant_client.py with Qdrant Cloud connection, vector search method with cosine similarity >0.7 threshold

### Backend Core Infrastructure

- [X] T012 Create backend/main.py with FastAPI app initialization, CORS middleware configuration for localhost:3000 and GitHub Pages domain
- [X] T013 Create backend/src/config.py loading environment variables via python-dotenv with validation for required API keys
- [X] T014 [P] Create backend/src/models/query.py with Pydantic models: ChatRequest (query, session_id, page_context, selection_text), ChatResponse (answer, citations, retrieved_chunks)
- [X] T015 [P] Create backend/src/models/embedding.py with Pydantic models: EmbeddingChunk, VectorSearchResult, Citation per data-model.md

### Frontend Core Infrastructure

- [X] T016 Initialize Docusaurus project in book/ with docusaurus.config.js configured for GitHub Pages deployment (baseUrl, url, organizationName, projectName)
- [X] T017 Create book/sidebars.js with hierarchical structure: Module 1-4 → Lessons → Exercises per plan.md
- [X] T018 Create book/src/css/custom.css with dark/light theme variables, chatbot widget positioning styles
- [X] T019 [P] Create book/static/img/ directory for curriculum images, diagrams, screenshots

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 5 - AI-Assisted Learning via RAG Chatbot (Priority: P0) 🎯 MVP

**Goal**: Enable students to ask questions about curriculum content via embedded chatbot widget with RAG-based answers and citations

**Independent Test**: Open any book page, type question "What are URDF joint limits?", verify chatbot retrieves Module 1 content, generates accurate answer with citations within 3 seconds

### Backend RAG Pipeline Implementation

- [X] T020 [P] [US5] Create backend/src/services/embedder.py with OpenAI text-embedding-3-small integration, batch embedding generation (50 chunks per batch)
- [X] T021 [P] [US5] Create backend/src/services/retriever.py with Qdrant vector search, top-5 chunk retrieval, cosine similarity filtering >0.7 per FR-039
- [X] T022 [P] [US5] Create backend/src/services/generator.py with OpenAI Agents SDK integration, system prompt for curriculum-scoped answers, citation formatting per FR-041, FR-043
- [X] T023 [US5] Create backend/src/services/rag_pipeline.py orchestrating retrieve → augment → generate flow with context window management (<8k tokens per FR-040)
- [X] T024 [US5] Add input sanitization in backend/src/services/rag_pipeline.py stripping special tokens (<|endoftext|>, <|im_sep|>), validating query length 1-500 chars per FR-046

### Backend API Endpoints

- [X] T025 [US5] Implement POST /chat endpoint in backend/src/api/chat.py calling RAG pipeline, logging conversation turn to Neon Postgres per FR-047, returning ChatResponse schema
- [X] T026 [US5] Implement GET /health endpoint in backend/src/api/health.py checking Qdrant, Neon, OpenAI connectivity with 2-second timeout per contracts/health_api.yaml
- [X] T027 [US5] Implement rate limiting middleware in backend/src/api/rate_limit.py checking sliding window (20 queries/hour per session_id) in Neon rate_limit_records table per FR-048
- [X] T028 [US5] Add error handling in backend/src/api/chat.py for 400 (invalid input), 429 (rate limit), 503 (service unavailable) responses per contracts/chat_api.yaml
- [X] T029 [US5] Add CORS exception handling in backend/main.py with detailed logging for cross-origin debugging

### Frontend Chatbot Widget

- [X] T030 [US5] Create React component in book/src/components/ChatbotWidget/index.tsx with collapsed/expanded states, fixed bottom-right positioning per FR-051, FR-057
- [X] T031 [US5] Implement sessionStorage integration in book/src/components/ChatbotWidget/index.tsx generating session_id via crypto.randomUUID(), persisting conversation history per FR-055
- [X] T032 [US5] Add text-selection detection in book/src/components/ChatbotWidget/index.tsx capturing highlighted text, passing as selection_text to POST /chat per FR-052
- [X] T033 [US5] Implement citation rendering in book/src/components/ChatbotWidget/index.tsx with clickable links, smooth scroll to book sections per FR-054 (integrated in main component)
- [X] T034 [US5] Add typing indicators in book/src/components/ChatbotWidget/index.tsx showing animated dots during LLM response generation per FR-053 (integrated in main component)
- [X] T035 [US5] Add "suggested questions" feature in book/src/components/ChatbotWidget/SuggestedQuestions.tsx displaying context-aware prompts based on current page metadata per FR-056
- [X] T036 [US5] Implement copy-to-clipboard button in book/src/components/ChatbotWidget/index.tsx for each chatbot response per FR-060 (integrated in main component)
- [X] T037 [US5] Add error handling in book/src/components/ChatbotWidget/index.tsx showing "Chatbot temporarily offline" message when backend unavailable with retry button per FR-058
- [X] T038 [US5] Add keyboard navigation and ARIA labels in book/src/components/ChatbotWidget/index.tsx for WCAG 2.1 AA accessibility per FR-059

### Curriculum Embedding Pipeline

- [X] T039 [US5] Create curriculum embedding script in backend/scripts/embed_curriculum.py parsing markdown files from book/docs/, extracting metadata (module, lesson, section_title, url)
- [X] T040 [US5] Implement markdown chunking strategy in backend/scripts/embed_curriculum.py splitting at heading boundaries (## and ###), preserving semantic coherence, max 1000 words per chunk per data-model.md
- [X] T041 [US5] Add batch embedding generation in backend/scripts/embed_curriculum.py calling OpenAI text-embedding-3-small with 50 chunks per batch, uploading to Qdrant curriculum collection
- [X] T042 [US5] Add verification step in backend/scripts/embed_curriculum.py testing retrieval on sample queries (e.g., "URDF joints") to confirm HNSW index built correctly

### Database Logging & Rate Limiting

- [X] T043 [US5] Implement conversation logging in backend/src/db/neon_client.py with insert_conversation_turn method storing query, response, retrieved_chunks JSONB, timestamp per data-model.md
- [X] T044 [US5] Implement rate limit checking in backend/src/db/neon_client.py with check_rate_limit method querying rate_limit_records with 1-hour sliding window per FR-048
- [X] T045 [US5] Create scheduled cleanup job in backend/scripts/cleanup_logs.py auto-deleting conversation_turns and rate_limit_records older than retention period (30 days after quarter end per FR-019, FR-047)

**Checkpoint**: At this point, User Story 5 (RAG Chatbot) should be fully functional and testable independently

---

## Phase 4: Book Infrastructure & Deployment (Supporting US5)

**Goal**: Deploy book to GitHub Pages with CI/CD pipeline

**Independent Test**: Push commit to main branch, verify GitHub Actions builds and deploys book to GitHub Pages within 5 minutes

- [X] T046 [P] [US5] Create .github/workflows/deploy-book.yml with Node.js 18 setup, npm install, Docusaurus build, GitHub Pages deployment per plan.md
- [X] T047 [P] [US5] Create .github/workflows/deploy-backend.yml with Railway deployment configuration (or Railway auto-deploy via GitHub integration)
- [X] T048 [US5] Add markdown validation script in scripts/validate_frontmatter.py checking YAML frontmatter syntax across all book/docs/ files per quickstart.md troubleshooting
- [X] T049 [US5] Add link validation script in scripts/check_links.py verifying internal links in markdown files point to existing pages
- [X] T050 [US5] Configure Docusaurus search in book/docusaurus.config.js using @easyops-cn/docusaurus-search-local plugin per FR-030

**Checkpoint**: Book deploys automatically to GitHub Pages, backend deploys to Railway

---

## Phase 5: Curriculum Content Creation - Module 1 (ROS 2 Middleware)

**Goal**: Create curriculum content for Module 1 covering ROS 2 fundamentals

**Independent Test**: Verify Module 1 lessons render correctly in Docusaurus, chatbot retrieves Module 1 content accurately when asked about ROS 2 topics

- [X] T051 [P] Create book/docs/module1/intro.md with module overview, learning objectives (LO-001, LO-002, LO-003 from spec.md)
- [X] T052 [P] Create book/docs/module1/lesson1-ros2-basics.md covering ROS 2 Humble installation, workspace setup, talker/listener example per spec.md User Story 1
- [X] T053 [P] Create book/docs/module1/lesson2-nodes-topics.md explaining pub/sub patterns, QoS policies, ros2 topic CLI commands
- [X] T054 [P] Create book/docs/module1/lesson3-urdf-models.md covering URDF joint types, limits, robot modeling syntax with code examples per spec.md edge cases
- [X] T055 [P] Create book/docs/module1/lesson4-services.md explaining service-based control interfaces, ros2 service CLI commands
- [X] T056 [P] Create book/docs/module1/lesson5-rqt-visualization.md demonstrating RQT graph, topic monitoring, node debugging tools
- [X] T057 Create book/docs/module1/exercises.md with prediction-execution-reflection templates for Module 1 exercises per FR-018
- [ ] T058 Re-run backend/scripts/embed_curriculum.py to embed Module 1 content in Qdrant, verify retrieval accuracy on Module 1 test queries

**Checkpoint**: Module 1 curriculum complete, embedded in Qdrant, chatbot retrieves Module 1 content accurately

---

## Phase 6: Curriculum Content Creation - Module 2 (Simulation)

**Goal**: Create curriculum content for Module 2 covering Gazebo and Unity simulation

**Independent Test**: Verify Module 2 lessons render with physics diagrams, chatbot retrieves simulation content when asked about Gazebo or Unity

- [X] T059 [P] Create book/docs/module2/intro.md with module overview, learning objectives (LO-004, LO-005, LO-006 from spec.md)
- [X] T060 [P] Create book/docs/module2/lesson1-gazebo-setup.md covering Gazebo 11 installation, humanoid URDF spawning, physics configuration per spec.md User Story 2
- [X] T061 [P] Create book/docs/module2/lesson2-physics-engines.md explaining gravity, collisions, friction, joint dynamics with KaTeX equations per FR-028
- [X] T062 [P] Create book/docs/module2/lesson3-sensor-simulation.md covering RGB cameras, depth cameras, lidar, IMU sensor data publishing to ROS topics
- [X] T063 [P] Create book/docs/module2/lesson4-unity-isaac-sim.md (optional advanced track) explaining Unity integration, NVIDIA Isaac Sim setup for students with NVIDIA GPUs per FR-008
- [X] T064 [P] Create book/docs/module2/lesson5-debugging-simulation.md with troubleshooting guide for physics instability, joint explosions, collision issues per spec.md edge cases
- [X] T065 Create book/docs/module2/exercises.md with prediction-execution-reflection templates for Module 2 exercises
- [X] T066 Add downloadable URDF files to book/static/resources/module2/ for students to download and modify per FR-029
- [ ] T067 Re-run backend/scripts/embed_curriculum.py to embed Module 2 content in Qdrant, verify retrieval accuracy on Module 2 test queries

**Checkpoint**: Module 2 curriculum complete, embedded in Qdrant, chatbot retrieves simulation content accurately

---

## Phase 7: Curriculum Content Creation - Module 3 (Perception & Navigation)

**Goal**: Create curriculum content for Module 3 covering VSLAM, Nav2, autonomous navigation

**Independent Test**: Verify Module 3 lessons render with costmap visualizations, chatbot retrieves perception content when asked about VSLAM or Nav2

- [X] T068 [P] Create book/docs/module3/intro.md with module overview, learning objectives (LO-007, LO-008, LO-009 from spec.md)
- [X] T069 [P] Create book/docs/module3/lesson1-vslam-fundamentals.md explaining VSLAM algorithms, feature detection, pose estimation per spec.md User Story 3
- [X] T070 [P] Create book/docs/module3/lesson2-isaac-ros-vslam.md covering NVIDIA Isaac ROS setup for GPU-accelerated VSLAM (preferred path) with nvidia-smi detection per FR-009
- [X] T071 [P] Create book/docs/module3/lesson3-cpu-slam-fallback.md covering ORB-SLAM3 and RTAB-Map CPU-based alternatives for non-NVIDIA systems per FR-009
- [X] T072 [P] Create book/docs/module3/lesson4-nav2-stack.md explaining Nav2 architecture, local/global planners, costmap configuration per spec.md
- [X] T073 [P] Create book/docs/module3/lesson5-obstacle-avoidance.md with Nav2 tuning guide, recovery behaviors, stuck detection per spec.md acceptance scenarios
- [X] T074 [P] Create book/docs/module3/lesson6-rviz-visualization.md demonstrating RViz costmap visualization, planned path display, debugging tools
- [X] T075 Create book/docs/module3/exercises.md with prediction-execution-reflection templates for Module 3 exercises
- [ ] T076 Re-run backend/scripts/embed_curriculum.py to embed Module 3 content in Qdrant, verify retrieval accuracy on Module 3 test queries

**Checkpoint**: Module 3 curriculum complete, embedded in Qdrant, chatbot retrieves perception/navigation content accurately

---

## Phase 8: Curriculum Content Creation - Module 4 (Voice-Language-Action)

**Goal**: Create curriculum content for Module 4 covering VLA pipeline, LLM integration, voice-to-action systems

**Independent Test**: Verify Module 4 lessons render with VLA diagrams, chatbot retrieves VLA content when asked about LLM integration or voice commands

- [X] T077 [P] Create book/docs/module4/intro.md with module overview, learning objectives (LO-010, LO-011, LO-012 from spec.md)
- [X] T078 [P] Create book/docs/module4/lesson1-vla-architecture.md explaining voice-to-action pipeline, speech-to-text, LLM reasoning per spec.md User Story 4
- [X] T079 [P] Create book/docs/module4/lesson2-speech-transcription.md covering Whisper/Google Speech API integration, transcription accuracy per spec.md SC-006
- [X] T080 [P] Create book/docs/module4/lesson3-llm-integration.md explaining OpenAI/Anthropic API setup, prompt engineering for robot control per FR-014
- [X] T081 [P] Create book/docs/module4/lesson4-action-validation.md covering multi-layer safety validation: LLM prompt constraints, parameter bounds, simulation pre-checks per FR-015a, FR-015b
- [X] T082 [P] Create book/docs/module4/lesson5-ros2-action-servers.md explaining ROS 2 action interface, action plan translation from LLM outputs per FR-015, FR-016
- [X] T083 [P] Create book/docs/module4/lesson6-latency-optimization.md with guide to achieving <10s voice-to-action latency per spec.md SC-006a
- [X] T084 [P] Create book/docs/module4/lesson7-debugging-vla.md with troubleshooting guide for LLM failures, invalid commands, ambiguous inputs per spec.md edge cases
- [X] T085 Create book/docs/module4/exercises.md with prediction-execution-reflection templates for Module 4 exercises
- [ ] T086 Re-run backend/scripts/embed_curriculum.py to embed Module 4 content in Qdrant, verify retrieval accuracy on Module 4 test queries

**Checkpoint**: Module 4 curriculum complete, embedded in Qdrant, chatbot retrieves VLA content accurately

---

## Phase 9: Capstone Project & Final Integration

**Goal**: Create capstone project documentation integrating all 4 modules

**Independent Test**: Verify capstone project page renders with all module references, chatbot retrieves cross-module content when asked integration questions

- [X] T087 Create book/docs/capstone/intro.md explaining capstone requirements: voice-commanded autonomous humanoid demonstrating ROS 2, simulation, perception, VLA integration per spec.md User Story 4
- [X] T088 Create book/docs/capstone/project-requirements.md with acceptance criteria, rubric, deliverables per spec.md SC-008, SC-009
- [X] T089 Create book/docs/capstone/implementation-guide.md with step-by-step integration instructions referencing all 4 modules
- [X] T090 Create book/docs/capstone/debugging-checklist.md with common integration issues, diagnostic procedures per spec.md edge cases
- [ ] T091 Re-run backend/scripts/embed_curriculum.py to embed capstone content in Qdrant
- [X] T092 Add landing page in book/src/pages/index.tsx with course overview, module navigation, chatbot introduction per plan.md

**Checkpoint**: All 4 modules + capstone curriculum complete, fully embedded in Qdrant

---

## Phase 10: Testing & Quality Assurance

**Purpose**: Comprehensive testing across all user stories and system components

### Backend Testing

- [X] T093 [P] Create backend/tests/unit/test_embedder.py testing OpenAI embedding generation, batch processing, error handling
- [X] T094 [P] Create backend/tests/unit/test_retriever.py testing Qdrant vector search, cosine similarity filtering, top-5 retrieval per FR-039
- [X] T095 [P] Create backend/tests/unit/test_generator.py testing OpenAI Agents SDK integration, citation formatting, context window management per FR-040
- [X] T096 [P] Create backend/tests/unit/test_rag_pipeline.py testing end-to-end RAG flow: retrieve → augment → generate
- [X] T097 [P] Create backend/tests/unit/test_rate_limiter.py testing sliding window rate limiting (20 queries/hour), session tracking per FR-048
- [X] T098 [P] Create backend/tests/integration/test_chat_api.py testing POST /chat with valid queries (200 response), empty queries (400 error), rate limit exceeded (429 error) per contracts/chat_api.yaml
- [X] T099 [P] Create backend/tests/integration/test_health_api.py testing GET /health with all services up (200), Neon suspended (503), Qdrant unavailable (503) per contracts/health_api.yaml
- [X] T100 Create backend/tests/e2e/test_chatbot_flow.py testing full flow: question → RAG pipeline → database logging → response with citations

### Frontend Testing

- [X] T101 [P] Create book/src/components/ChatbotWidget/__tests__/index.test.tsx testing widget rendering, collapsed/expanded states, sessionStorage persistence
- [X] T102 [P] Create book/src/components/ChatbotWidget/__tests__/CitationList.test.tsx testing citation rendering, clickable links, smooth scroll navigation
- [X] T103 [P] Create book/src/components/ChatbotWidget/__tests__/MessageList.test.tsx testing message display, typing indicators, copy-to-clipboard functionality
- [X] T104 Create book/src/components/ChatbotWidget/__tests__/integration.test.tsx testing text-selection → query submission → response with citations

### Performance Testing

- [ ] T105 Test chatbot latency: measure query submission → first response token, verify <3s for 95th percentile per SC-020
- [ ] T106 Test FastAPI overhead: measure processing time excluding LLM latency, verify <200ms per FR-050
- [ ] T107 Test Qdrant vector search: measure query time for curriculum corpus (~500-800 chunks), verify <100ms per SC-025
- [ ] T108 Test Neon database: insert 1000 conversation turns, measure query time, verify <50ms per SC-024
- [ ] T109 Test Docusaurus build: measure full build time for all 4 modules, verify <5 minutes per SC-013, SC-014
- [ ] T110 Test book page load: measure load time on 50 Mbps connection, verify <2s per SC-016

### Accuracy & Quality Testing

- [ ] T111 Create backend/tests/data/test_queries.json with 100 curriculum questions spanning all 4 modules with instructor-labeled expected answers
- [ ] T112 Run accuracy evaluation: compare chatbot answers against test_queries.json ground truth, verify >85% accuracy per SC-018
- [ ] T113 Test retrieval precision: verify top-3 chunks contain relevant content for 90% of in-scope queries per SC-019
- [ ] T114 Test citation accuracy: verify chatbot provides correct book section links in >90% of answers per SC-023
- [ ] T115 Test off-topic rejection: verify chatbot rejects non-curriculum questions 100% of time per SC-022

### Accessibility Testing

- [ ] T116 Test keyboard navigation: verify chatbot widget operable via Tab, Enter, Escape keys per FR-059
- [ ] T117 Test screen reader compatibility: verify ARIA labels present, chatbot messages read correctly per FR-059
- [ ] T118 Run axe DevTools accessibility audit on book pages, verify WCAG 2.1 AA compliance per FR-059

**Checkpoint**: All tests passing, performance targets met, accuracy validated

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements, documentation, deployment validation

- [ ] T119 [P] Create comprehensive API documentation in backend/docs/api.md referencing contracts/chat_api.yaml and contracts/health_api.yaml
- [ ] T120 [P] Add code comments and docstrings across backend/src/ modules following Google Python Style Guide
- [ ] T121 [P] Add TypeScript JSDoc comments in book/src/components/ for maintainability
- [ ] T122 [P] Create backend/docs/architecture.md documenting RAG pipeline, database schema, service dependencies per plan.md
- [ ] T123 [P] Add monitoring dashboard configuration in backend/monitoring/ for Railway metrics, Neon compute hours, OpenAI API usage per quickstart.md Section 8
- [ ] T124 [P] Create usage alert scripts in backend/scripts/monitor_usage.py checking Railway hours (alert at 400/500), Neon compute, Qdrant storage per quickstart.md troubleshooting
- [ ] T125 Perform security audit: verify no secrets in Git history, .env excluded, API keys rotated, CORS properly configured
- [ ] T126 Test cold start latency: verify Railway backend resumes from sleep within 10s, implement health check pings every 4 minutes to prevent sleep per quickstart.md Issue 6
- [ ] T127 Run quickstart.md validation: follow all setup steps from scratch on fresh Ubuntu 22.04 VM, verify no missing dependencies
- [ ] T128 Create final deployment checklist in specs/001-book-publication-rag-chatbot/deployment-checklist.md covering Railway setup, GitHub Pages configuration, environment variables, monitoring alerts
- [ ] T129 Code cleanup and refactoring: remove debug print statements, standardize error messages, consolidate duplicate code
- [ ] T130 Final end-to-end smoke test: deploy to production, submit 20 test queries across all modules, verify all acceptance scenarios from spec.md User Story 5

**Checkpoint**: Production-ready deployment validated, documentation complete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 5 - RAG Chatbot (Phase 3)**: Depends on Foundational phase completion
- **Book Infrastructure (Phase 4)**: Can proceed in parallel with Phase 3 after Phase 2 completes
- **Curriculum Content Creation (Phases 5-8)**: Depends on Phases 3+4 completion (RAG chatbot must be functional to test content retrieval)
  - Module 1 (Phase 5) → Module 2 (Phase 6) → Module 3 (Phase 7) → Module 4 (Phase 8): Sequential (each builds on previous)
- **Capstone (Phase 9)**: Depends on all 4 module phases completion
- **Testing (Phase 10)**: Can begin unit tests early, integration tests after Phase 3, E2E tests after Phase 9
- **Polish (Phase 11)**: Depends on all desired features complete

### User Story Dependencies

- **User Story 5 (P0)**: RAG Chatbot - No dependencies on other stories, is foundational infrastructure
- **Content Creation (Phases 5-8)**: Depends on User Story 5 completion (chatbot must exist to embed and retrieve content)

### Within Each Phase

- **Phase 2 (Foundational)**: Database setup (T008-T011) must complete before API implementation
- **Phase 3 (RAG Chatbot)**: Backend services (T020-T024) must complete before API endpoints (T025-T029); Frontend widget can develop in parallel with backend
- **Phase 4 (Deployment)**: Independent of other phases after Phase 2
- **Phases 5-8 (Content)**: Each module independent within phase, but must run embed script (final task) after all lessons complete

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002, T003, T006, T007)
- All Foundational DB/client tasks marked [P] can run in parallel (T010, T011, T014, T015, T017, T019)
- Backend RAG services marked [P] can run in parallel (T020, T021, T022)
- All curriculum lesson creation tasks within each module marked [P] can run in parallel
- All testing tasks marked [P] can run in parallel within Phase 10
- All polish/documentation tasks marked [P] can run in parallel within Phase 11

---

## Parallel Example: Phase 3 (User Story 5)

```bash
# Launch backend RAG services together:
Task T020: "Create backend/src/services/embedder.py"
Task T021: "Create backend/src/services/retriever.py"
Task T022: "Create backend/src/services/generator.py"
# Then T023 (rag_pipeline.py) depends on T020-T022

# Launch frontend components together (after widget base created):
Task T033: "Implement citation rendering"
Task T034: "Add typing indicators"
Task T035: "Add suggested questions"
Task T036: "Implement copy-to-clipboard"
```

---

## Implementation Strategy

### MVP First (User Story 5 Only - RAG Chatbot)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 5 (RAG Chatbot)
4. Complete Phase 4: Book Infrastructure (deployment)
5. **STOP and VALIDATE**: Test User Story 5 independently with sample curriculum
6. Deploy to production, demo chatbot functionality

### Incremental Content Delivery

1. Complete Phases 1-4 → RAG Chatbot infrastructure ready
2. Add Module 1 (Phase 5) → Test retrieval → Deploy (students can start learning)
3. Add Module 2 (Phase 6) → Test retrieval → Deploy
4. Add Module 3 (Phase 7) → Test retrieval → Deploy
5. Add Module 4 (Phase 8) → Test retrieval → Deploy
6. Add Capstone (Phase 9) → Test retrieval → Deploy (full curriculum complete)
7. Run comprehensive testing (Phase 10)
8. Final polish (Phase 11) → Production launch

### Parallel Team Strategy

With multiple developers after Phase 2 completion:

**Team Assignment Example**:
- **Developer A**: Phase 3 backend (T020-T029, T039-T045)
- **Developer B**: Phase 3 frontend (T030-T038)
- **Developer C**: Phase 4 deployment + Phase 10 testing setup
- **Content Team**: Phases 5-8 curriculum writing (can start drafting markdown early, embed after chatbot ready)

Stories complete and integrate independently.

---

## Notes

- [P] tasks = different files, no dependencies
- [US5] label maps task to User Story 5 for traceability
- User Story 5 should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Primary focus is User Story 5 (P0 - RAG Chatbot infrastructure) as it is the delivery mechanism for all other user stories
- Curriculum content creation (Modules 1-4) is separate from chatbot infrastructure but depends on chatbot being functional
- All file paths are absolute from project root: C:\Users\MASTER\Desktop\physical_ai\

---

## Success Metrics Mapping

Tasks align with spec.md success criteria:

- **SC-013** (Book deploys <5 min): T046 GitHub Actions workflow
- **SC-018** (Chatbot >85% accuracy): T111-T112 accuracy evaluation
- **SC-020** (Chatbot <3s latency): T105 performance testing
- **SC-023** (Citation accuracy >90%): T114 citation testing
- **SC-024** (Neon >1000 turns): T108 database capacity testing
- **SC-025** (Qdrant <100ms): T107 vector search performance
- **SC-026** (Conversation context persists): T031 sessionStorage implementation + T104 integration test
