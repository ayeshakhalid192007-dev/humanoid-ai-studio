---
id: 004
title: Per-Agent Context Grounding Plan
stage: plan
date: 2026-02-17
surface: agent
model: claude-opus-4-6
feature: 003-reusable-intelligence-architecture
branch: 003-reusable-intelligence-architecture
user: architect
command: /sp.plan
labels: ["plan", "grounding", "orchestrator", "agents", "skills", "per-agent-policy"]
links:
  spec: specs/003-reusable-intelligence-architecture/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-reusable-intelligence-architecture/plan.md
  - specs/003-reusable-intelligence-architecture/research.md
  - specs/003-reusable-intelligence-architecture/data-model.md
  - specs/003-reusable-intelligence-architecture/quickstart.md
  - specs/003-reusable-intelligence-architecture/contracts/envelope.yaml
  - specs/003-reusable-intelligence-architecture/contracts/ai-personalize.yaml
  - specs/003-reusable-intelligence-architecture/contracts/ai-translate.yaml
  - specs/003-reusable-intelligence-architecture/contracts/ai-chat.yaml
tests:
  - None (planning phase, no implementation yet)
---

## Prompt

# Implementation Plan: Per-Agent Context Grounding

## Objective
Implement a grounding policy tailored for each agent:
- **RAG Agent**: strict grounding (no fabrication)
- **Personalization Agent**: preserve structure, allow adaptive explanations
- **Translation Agent**: preserve semantic meaning, allow language transformation

---

## Phase 1: Define Policies

- [ ] RAG Agent → strict grounding enforcement
- [ ] Personalization Agent → structural fidelity only
- [ ] Translation Agent → semantic fidelity
- [ ] Document policies for each agent in system spec

---

## Phase 2: AI Prompt Design

- [ ] Create system prompts for each agent type
- [ ] Embed grounding rules explicitly
- [ ] Ensure token/context limits per agent
- [ ] Add instructions to prevent hallucination where needed

---

## Phase 3: Orchestrator Integration

- [ ] Route requests through AI Orchestrator
- [ ] Select agent and apply corresponding grounding policy
- [ ] Log policy applied per request

---

## Phase 4: Validation & Testing

- [ ] Test RAG Agent → verify no fabricated content
- [ ] Test Personalization → verify adaptation while preserving structure
- [ ] Test Translation → verify meaning is preserved
- [ ] Include edge cases (complex chapters, mixed content)

---

## Phase 5: Monitoring & Logging

- [ ] Log per-agent policy enforcement
- [ ] Include status, duration, and errors if grounding fails
- [ ] Ensure debugging visibility for all agents

---

## Deliverables

- Agent-specific grounding enforcement
- Updated AI prompts
- Orchestrator integration
- Logging for policy enforcement
- Verified and tested outputs for all agent types

## Response snapshot

Generated comprehensive implementation plan for Reusable Intelligence Architecture with focus on per-agent context grounding. Produced 8 artifacts:

1. **plan.md** — Full implementation plan with Technical Context, Constitution Check (all gates passed), Project Structure, Complexity Tracking, Architecture section detailing 3 grounding policies (strict_grounding, structural_fidelity, semantic_fidelity), Key Design Decisions (D1-D7), and 4-phase Migration Strategy.

2. **research.md** — 8 research decisions: agent/skill composition pattern (ABC + dict registry), dual-phase skill execution, prompt registry (MD files with SHA-256 versioning), per-agent grounding policies (HallucinationPreventionSkill with policy-based pre/post logic), streaming support, execution logging schema, legacy proxy pattern, singleton lifecycle.

3. **data-model.md** — 6 runtime entities (AgentRequest, AgentResponse, AIEnvelope, SkillContext, PromptTemplate, SkillPhase), 1 new DB table (agent_execution_logs), 2 modified tables (prompt_version column), NeonClient method additions, agent-to-skill mapping.

4. **contracts/** — 4 OpenAPI contract files: envelope.yaml (common AIEnvelope schema), ai-personalize.yaml (FR-019), ai-translate.yaml (FR-020), ai-chat.yaml (FR-021/FR-028 including SSE streaming).

5. **quickstart.md** — Developer setup guide with curl examples for all 4 new endpoints.

Key grounding architecture: HallucinationPreventionSkill is dual-phase (pre: inject grounding directives per agent type; post: validate compliance). RAG=strict (reject fabrication), Personalization=structural fidelity (preserve headings), Translation=semantic fidelity (preserve code blocks + meaning).

## Outcome

- ✅ Impact: Complete implementation plan with per-agent grounding architecture, ready for /sp.tasks
- 🧪 Tests: No tests yet (planning phase). Test strategy defined in plan.md.
- 📁 Files: 8 files created/modified across specs/003-reusable-intelligence-architecture/
- 🔁 Next prompts: /sp.tasks to generate implementation tasks, /sp.adr if architectural decisions need formal recording
- 🧠 Reflection: The per-agent grounding policy maps cleanly to a single configurable skill rather than 3 separate skills. The dual-phase model (pre: inject directives, post: validate) provides the right separation.

## Evaluation notes (flywheel)

- Failure modes observed: None during planning
- Graders run and results (PASS/FAIL): N/A (planning phase)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Implement HallucinationPreventionSkill first to validate the policy-based dual-phase pattern before building other skills
