---
description: "Task list for Reusable Intelligence Architecture feature"
---

# Tasks: Reusable Intelligence Architecture

**Input**: Design documents from `/specs/003-reusable-intelligence-architecture/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included where required for validation of the new architecture.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- All paths follow the structure defined in plan.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create AI module structure `backend/src/ai/__init__.py`
- [X] T002 [P] Create AI module structure `backend/src/ai/orchestrator.py`
- [X] T003 [P] Create AI module structure `backend/src/ai/base.py`
- [X] T004 [P] Create AI module structure `backend/src/ai/registry.py`
- [X] T005 [P] Create AI module structure `backend/src/ai/envelope.py`
- [X] T006 [P] Create agents directory `backend/src/ai/agents/__init__.py`
- [X] T007 [P] Create skills directory `backend/src/ai/skills/__init__.py`
- [X] T008 [P] Create prompts directory `backend/src/ai/prompts/__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T009 Create base abstract interfaces in `backend/src/ai/base.py`
- [X] T010 Create common response envelope in `backend/src/ai/envelope.py`
- [X] T011 Create agent and skill registries in `backend/src/ai/registry.py`
- [X] T012 Create AI Orchestrator interface in `backend/src/ai/orchestrator.py`
- [X] T013 Create database migration for `agent_execution_logs` table
- [X] T014 Add methods to `NeonClient` for `agent_execution_logs`
- [X] T015 Add methods to `NeonClient` for modified cache lookups with prompt_version
- [X] T016 Create new API endpoints file `backend/src/api/ai.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - AI Orchestrator Routes Personalization Requests (Priority: P1) 🎯 MVP

**Goal**: Build the AI Orchestrator that routes personalization requests to the Personalization Agent with required skills and validates output

**Independent Test**: Can be fully tested by sending a personalization request with a known user profile and chapter slug, then verifying the returned markdown preserves structure, adapts to the profile, and is cached in the database.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T017 [P] [US1] Contract test for `POST /api/ai/personalize` in `backend/tests/integration/test_ai_personalize.py`
- [ ] T018 [P] [US1] Unit test for Personalization Agent in `backend/tests/unit/test_agents.py`

### Implementation for User Story 1

- [X] T019 [P] [US1] Create Personalization Agent base class in `backend/src/ai/agents/personalization.py`
- [X] T020 [US1] Implement Markdown Preservation skill in `backend/src/ai/skills/markdown_preservation.py`
- [X] T021 [US1] Implement Context Boundary skill in `backend/src/ai/skills/context_boundary.py`
- [X] T022 [US1] Implement Hallucination Prevention skill in `backend/src/ai/skills/hallucination_prevention.py`
- [X] T023 [US1] Implement Educational Tone Control skill in `backend/src/ai/skills/educational_tone.py`
- [X] T024 [US1] Implement Knowledge Level Adjustment skill in `backend/src/ai/skills/knowledge_level.py`
- [X] T025 [US1] Update Personalization Agent to compose required skills
- [X] T026 [US1] Implement AI Orchestrator core logic in `backend/src/ai/orchestrator.py`
- [X] T027 [US1] Create prompt template for personalization agent at `backend/src/ai/prompts/templates/personalization.md`
- [X] T028 [US1] Create prompt registry in `backend/src/ai/prompts/registry.py`
- [ ] T029 [US1] Implement new `/api/ai/personalize` endpoint in `backend/src/api/ai.py`
- [ ] T030 [US1] Add rate limiting to personalization endpoint
- [ ] T031 [US1] Add authentication requirement to personalization endpoint

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - AI Orchestrator Routes Translation Requests (Priority: P2)

**Goal**: Extend the AI Orchestrator to route translation requests to the Translation Agent with required skills

**Independent Test**: Can be tested by sending a translation request with a chapter slug and verifying the returned content is Urdu markdown with preserved code blocks and formatting.

### Tests for User Story 2 ⚠️

- [ ] T032 [P] [US2] Contract test for `POST /api/ai/translate` in `backend/tests/integration/test_ai_translate.py`
- [ ] T033 [P] [US2] Unit test for Translation Agent in `backend/tests/unit/test_agents.py`

### Implementation for User Story 2

- [X] T034 [P] [US2] Create Translation Agent base class in `backend/src/ai/agents/translation.py`
- [X] T035 [US2] Implement Code Block Detection skill in `backend/src/ai/skills/code_block_detection.py`
- [X] T036 [US2] Update Translation Agent to compose required skills (context boundary, hallucination prevention, code block detection, markdown preservation)
- [X] T037 [US2] Create prompt template for translation agent at `backend/src/ai/prompts/templates/translation.md`
- [ ] T038 [US2] Implement new `/api/ai/translate` endpoint in `backend/src/api/ai.py`
- [ ] T039 [US2] Add rate limiting to translation endpoint
- [ ] T040 [US2] Add IP-based rate limiting for translation requests

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - AI Orchestrator Routes Chat/RAG Requests (Priority: P3)

**Goal**: Extend the AI Orchestrator to route RAG chat requests to the RAG Reasoning Agent with strict grounding enforcement

**Independent Test**: Can be tested by sending a chat query and verifying the response contains an answer grounded in retrieved curriculum context with citations.

### Tests for User Story 3 ⚠️

- [ ] T041 [P] [US3] Contract test for `POST /api/ai/chat` in `backend/tests/integration/test_ai_chat.py`
- [ ] T042 [P] [US3] Unit test for RAG Reasoning Agent in `backend/src/ai/agents/rag.py`

### Implementation for User Story 3

- [X] T043 [P] [US3] Create RAG Reasoning Agent base class in `backend/src/ai/agents/rag.py`
- [X] T044 [US3] Update Hallucination Prevention skill to handle strict grounding for RAG agent
- [X] T045 [US3] Update RAG Reasoning Agent to compose required skills (context boundary, hallucination prevention)
- [X] T046 [US3] Create prompt template for RAG chat agent at `backend/src/ai/prompts/templates/rag_chat.md`
- [ ] T047 [US3] Implement new `/api/ai/chat` endpoint in `backend/src/api/ai.py`
- [ ] T048 [US3] Implement streaming support in Orchestrator and endpoint
- [ ] T049 [US3] Implement `/api/ai/chat/stream` endpoint with SSE support
- [ ] T050 [US3] Add rate limiting to chat endpoint

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Centralized Prompt Management (Priority: P4)

**Goal**: Replace inline system prompts with centralized prompt templates from the registry

**Independent Test**: Can be tested by modifying a prompt template file, restarting the server, and verifying the new prompt is used in the corresponding agent's output.

### Tests for User Story 4 ⚠️

- [ ] T051 [P] [US4] Test for prompt versioning and cache invalidation in `backend/tests/unit/test_prompts.py`
- [ ] T052 [P] [US4] Integration test for prompt changes affecting output in `backend/tests/integration/test_ai_personalize.py`

### Implementation for User Story 4

- [X] T053 [US4] Complete prompt registry implementation with versioning
- [ ] T054 [US4] Update all agents to load prompts from registry instead of inline strings
- [X] T055 [US4] Extract existing system prompts verbatim from current services to templates (completed for personalization, translation, rag_chat)
- [X] T056 [US4] Add prompt_version to cache lookups in NeonClient
- [X] T057 [US4] Add dual invalidation (content + prompt) to cache logic
- [ ] T058 [US4] Update agents to pass prompt_version in responses

**Checkpoint**: All agents now use centralized prompts with versioning

---

## Phase 7: User Story 5 - Extensibility: Adding a New Agent (Priority: P5)

**Goal**: Demonstrate the extensibility by quickly adding a new agent without modifying existing code

**Independent Test**: Can be tested by creating a minimal new agent that composes existing skills and verifying it can be registered and invoked through the Orchestrator without modifying any existing files.

### Tests for User Story 5 ⚠️

- [ ] T059 [P] [US5] Test for new agent registration pattern in `backend/tests/unit/test_agents.py`
- [ ] T060 [P] [US5] Integration test for new agent through orchestrator in `backend/tests/integration/test_ai_quiz.py`

### Implementation for User Story 5

- [ ] T061 [P] [US5] Create minimal Quiz Agent as demonstration in `backend/src/ai/agents/quiz.py`
- [ ] T062 [US5] Verify that Quiz Agent requires no changes to existing agents or orchestrator
- [ ] T063 [US5] Add `/api/ai/quiz` endpoint as demonstration
- [ ] T064 [US5] Document the extensibility process in quickstart documentation

---

## Phase 8: Legacy Endpoint Migration (FR-029)

**Goal**: Convert existing endpoints to thin proxies routing through the new orchestrator

**Independent Test**: Legacy endpoints should continue to work but return deprecation headers, with identical output to new endpoints.

### Tests for Legacy Migration ⚠️

- [ ] T065 [P] Test legacy `/api/personalize` proxy functionality in `backend/tests/integration/test_legacy_personalize.py`
- [ ] T066 [P] Test legacy `/api/translate` proxy functionality in `backend/tests/integration/test_legacy_translate.py`

### Implementation for Legacy Migration

- [ ] T067 Update `/api/personalize` to route through Orchestrator and add deprecation headers
- [ ] T068 Update `/api/translate` to route through Orchestrator and add deprecation headers
- [ ] T069 Update `/chat/v2` to route through Orchestrator and add deprecation headers
- [ ] T070 Update `/chat/stream` to route through Orchestrator and add deprecation headers
- [ ] T071 Verify backward compatibility and identical output for legacy endpoints

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T072 [P] Add comprehensive logging to Orchestrator for skill execution and grounding policy enforcement
- [ ] T073 [P] Add 90-day cleanup job for agent execution logs in NeonClient
- [ ] T074 [P] Documentation updates in `specs/003-reusable-intelligence-architecture/`
- [ ] T075 Code cleanup and refactoring
- [ ] T076 Performance optimization across all stories
- [ ] T077 [P] Additional unit tests in `backend/tests/unit/`
- [ ] T078 Security hardening
- [ ] T079 Run quickstart.md validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Legacy Migration (Phase 8)**: Depends on all core user stories being complete
- **Polish (Final Phase)**: Depends on all desired user stories and legacy migration being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) but requires US1/2/3 to be implemented for testing
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) but requires US1/2/3/4 to be implemented for testing

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services (SkillContext, AgentRequest, etc.)
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Skills within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all skills for User Story 1 together:
Task: "Implement Markdown Preservation skill in `backend/src/ai/skills/markdown_preservation.py`"
Task: "Implement Context Boundary skill in `backend/src/ai/skills/context_boundary.py`"
Task: "Implement Hallucination Prevention skill in `backend/src/ai/skills/hallucination_prevention.py`"
Task: "Implement Educational Tone Control skill in `backend/src/ai/skills/educational_tone.py`"
Task: "Implement Knowledge Level Adjustment skill in `backend/src/ai/skills/knowledge_level.py`"

# Launch all agents and infrastructure for User Story 1 together:
Task: "Create Personalization Agent base class in `backend/src/ai/agents/personalization.py`"
Task: "Create prompt template for personalization agent at `backend/src/ai/prompts/templates/personalization.md`"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Add Legacy Migration → Test independently → Deploy/Demo
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
   - Developer D: User Story 4
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence