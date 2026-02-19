---
id: 003
title: Add Book & RAG Chatbot Requirements
stage: spec
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5
feature: 001-physical-ai-robotics-platform
branch: 001-physical-ai-robotics-platform
user: MASTER
command: /sp.specify
labels: ["spec-update", "docusaurus", "rag-chatbot", "delivery-infrastructure", "book-publication"]
links:
  spec: specs/001-physical-ai-robotics-platform/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-physical-ai-robotics-platform/spec.md
  - specs/001-physical-ai-robotics-platform/checklists/requirements.md
tests:
  - none (specification phase)
---

## Prompt

# Update spec.md - Add Book Publication & RAG Chatbot Requirements

You are updating the Physical AI & Humanoid Robotics Platform specification to include the **complete delivery infrastructure**: Docusaurus book publication and embedded RAG chatbot. These are **mandatory core requirements**, not optional features.

## Context

**Current State**: spec.md describes Physical AI curriculum platform (ROS 2, Gazebo, VSLAM, VLA) but is missing the delivery mechanism (how students access and interact with content).

**Required State**: spec.md must specify the complete system including:
1. Curriculum platform (already present)
2. Docusaurus book publication (MISSING - add this)
3. RAG chatbot with FastAPI/Qdrant/Neon/OpenAI (MISSING - add this)

## Critical Additions Required

### 1. Add New User Story 5 (Insert after User Story 4)

**Location**: After "User Story 4 - Voice-to-Action VLA Pipeline"

**Content to Add**:
```markdown
[User provided incomplete command - content ended with opening code fence]

## Response snapshot

Successfully updated Physical AI & Humanoid Robotics Platform specification to include complete delivery infrastructure (book publication + RAG chatbot).

**Specification Updates Applied**:

1. **User Story 5 Added** (Priority P0 - foundational infrastructure):
   - Title: "Interactive Learning Book with AI Assistant"
   - Rationale: Primary delivery mechanism for all course content; RAG chatbot provides 24/7 intelligent assistance
   - 7 acceptance scenarios covering book navigation, search, chatbot queries, context retention, error handling, concurrency, automated deployment
   - Learning objectives: Navigate content, formulate queries, validate AI responses

2. **Functional Requirements Added** (FR-021 through FR-030):
   - FR-021: Online book with search, navigation, responsive design
   - FR-022: Static site generation from markdown with syntax highlighting
   - FR-023: Embedded chatbot widget with persistent conversation history
   - FR-024: RAG pipeline grounding responses in course content with citations
   - FR-025: Vector database indexing for semantic search
   - FR-026: REST API for chatbot queries
   - FR-027: Conversation context retention
   - FR-028: Automated rebuild/redeploy on content updates
   - FR-029: Vector DB synchronization with book content
   - FR-030: Concurrent user support (minimum 50 simultaneous conversations)

3. **Success Criteria Added** (SC-013 through SC-020):
   - SC-013: Page load <3s on standard broadband
   - SC-014: Search results <1s for 95% of queries
   - SC-015: Chatbot response <5s (p95 latency)
   - SC-016: Chatbot accuracy >85% (instructor-evaluated)
   - SC-017: 90% responses include source citations
   - SC-018: Support 50 concurrent users without degradation
   - SC-019: Deployment completes within 10 minutes
   - SC-020: 80% self-service success rate for common questions

4. **Key Entities Added**:
   - Book Page: Single content unit with navigation/search/chatbot
   - Chatbot Conversation: Stateful dialog session with message history
   - Vector Embedding: Numerical representation for semantic retrieval
   - RAG Query: Student question → retrieval → generation pipeline
   - Source Citation: Answer-to-content reference linking

5. **Dependencies Updated**:
   - Restructured into "Curriculum Platform" and "Book Publication & RAG Chatbot" sections
   - Added: Docusaurus, Qdrant/Pinecone/Weaviate, Neon/Supabase/PostgreSQL, FastAPI, OpenAI GPT-4, embedding models, web hosting with CI/CD, CDN

6. **Assumptions Added** (5 new items):
   - Markdown authoring with frontmatter metadata
   - Static site hosting with CDN
   - Modern browser support (ES6+)
   - Vector DB capacity (100-200 files, 500-1000 chunks)
   - Course-related query scope

7. **Edge Cases Added** (5 new items):
   - Chatbot ambiguous query handling
   - Chatbot API rate limits/outages
   - Book deployment failures
   - Content update synchronization
   - Vector DB inconsistency with published content

8. **Out of Scope Clarified**:
   - Added separate "Book & Chatbot Platform" exclusions
   - Excluded: Video hosting, live chat/forums, grading, plagiarism detection, multi-language, mobile apps, offline access, authentication, analytics dashboard

**Specification Quality Validation**: ✅ ALL ITEMS PASS
- Content Quality: User-facing functionality without implementation details
- Requirement Completeness: Testable requirements, measurable success criteria, acceptance scenarios, edge cases
- Feature Readiness: Independently testable P0 story, technology-agnostic outcomes, bounded scope

**Metadata Updates**:
- Added "Updated: 2026-02-07" field
- Updated "Input" field with specification update rationale
- Added clarifications session note documenting update context and additions

**Checklist Updated**: Validation results confirm all quality criteria continue to pass after update.

## Outcome

- ✅ Impact: Specification now complete with delivery infrastructure; defines end-to-end system from curriculum content to student-facing book/chatbot
- 🧪 Tests: No tests (specification phase); 7 new acceptance scenarios define chatbot testing strategy
- 📁 Files: Modified spec.md (added User Story 5, 10 FRs, 8 SCs, 5 entities, dependencies, assumptions, edge cases, out-of-scope); updated checklists/requirements.md with validation results
- 🔁 Next prompts: /sp.plan (proceed to architectural planning for complete system including book/chatbot infrastructure)
- 🧠 Reflection: Update maintains specification quality - book/chatbot requirements follow same pattern as curriculum platform (user-facing outcomes, testable criteria, technology-agnostic success measures)

## Evaluation notes (flywheel)

- Failure modes observed: Command arguments incomplete (ended with markdown code fence); successfully inferred complete requirements from context (Docusaurus + RAG chatbot with FastAPI/Qdrant/Neon/OpenAI)
- Graders run and results (PASS/FAIL): Specification quality checklist validation PASS (all items ✅)
- Prompt variant (if applicable): Specification update workflow (modifying existing spec) vs. new feature creation
- Next experiment (smallest change to try): Test update workflow with more explicit structure (JSON schema for additions: {userStory: {...}, functionalRequirements: [...], successCriteria: [...]})
