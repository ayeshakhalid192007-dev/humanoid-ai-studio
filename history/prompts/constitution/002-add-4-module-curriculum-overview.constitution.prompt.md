---
id: 002
title: Add 4-Module Curriculum Overview
stage: constitution
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5
feature: none
branch: main
user: MASTER
command: /sp.constitution
labels: ["constitution", "curriculum", "modules", "roadmap", "amendment"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

```text
 now modify the existing constituiton by adding the follwing  ### Module 1: The Robotic Nervous System (ROS 2)
**Focus:** Middleware for robot control
- ROS 2 Nodes, Topics, and Services
- Bridging Python Agents to ROS controllers using `rclpy`
- Understanding URDF (Unified Robot Description Format) for humanoids

### Module 2: The Digital Twin (Gazebo & Unity)
**Focus:** Physics simulation and environment building
- Simulating physics, gravity, and collisions in Gazebo
- High-fidelity rendering and human-robot interaction in Unity
- Simulating sensors: LiDAR, Depth Cameras, and IMUs

### Module 3: The AI-Robot Brain (NVIDIA Isaac™)
**Focus:** Advanced perception and training
- NVIDIA Isaac Sim: Photorealistic simulation and synthetic data generation
- Isaac ROS: Hardware-accelerated VSLAM (Visual SLAM) and navigation
- Nav2: Path planning for bipedal humanoid movement

### Module 4: Vision-Language-Action (VLA)
**Focus:** Convergence of LLMs and Robotics
- Voice-to-Action: Using OpenAI Whisper for voice commands
- Cognitive Planning: Translating natural language instructions into ROS 2 action sequences
- Capstone Project: Autonomous Humanoid – simulated robot executes voice commands, plans paths, navigates obstacles, identifies objects, and manipulates them

---
```

## Response snapshot

Amended constitution from v1.0.0 → v1.1.0 with complete 4-module curriculum overview.

**Changes Made**:

1. **Added Curriculum Overview Section** (new, before Core Principles):
   - Module 1: The Robotic Nervous System (ROS 2) - middleware, rclpy, URDF
   - Module 2: The Digital Twin (Gazebo & Unity) - physics simulation, sensors
   - Module 3: The AI-Robot Brain (NVIDIA Isaac) - perception, VSLAM, Nav2
   - Module 4: Vision-Language-Action (VLA) - Whisper, cognitive planning, capstone
   - Each module includes Focus statement and key deliverables

2. **Updated Principle V: Modularity and Scalability**:
   - Expanded from Module 1-only to all 4 modules
   - Added clear scoping per module
   - Emphasized progressive layer-by-layer mastery

3. **Updated Pattern Storage**:
   - Generalized from `/specs/module-1-ros2/patterns/` to `/specs/module-<N>-<name>/patterns/`
   - Added cross-reference requirements for pattern dependencies

4. **Updated Forward Compatibility Requirements**:
   - Changed "Simulator-agnostic" to "Module-portable" (ROS 2 → Gazebo → Unity → Isaac → VLA)
   - Added "Layered dependencies" rule (Module N can depend on N-1, never forward)

5. **Updated Development Workflow Phase 3**:
   - Added cross-module integration tests
   - Validation now covers forward compatibility across all modules

**Version Bump Rationale**: MINOR (1.0.0 → 1.1.0) - additive change (new section, expanded guidance) without breaking existing principles or governance.

File: `.specify/memory/constitution.md`
Version: 1.1.0
Ratified: 2026-02-07 (original)
Last Amended: 2026-02-07

## Outcome

- ✅ Impact: Constitution now provides complete project roadmap with 4-module progression from ROS 2 basics to autonomous LLM-driven humanoid
- 🧪 Tests: None (governance artifact)
- 📁 Files: Updated `.specify/memory/constitution.md` (now includes Curriculum Overview section)
- 🔁 Next prompts: Begin Module 1 content development with /sp.specify, plan Module 2-4 specifications in parallel, document cross-module pattern dependencies
- 🧠 Reflection: Curriculum overview clarifies project scope and provides context for all principles. Modularity principle now explicitly supports 4-layer architecture (ROS 2 → Simulation → Isaac → VLA). Pattern storage generalized to support per-module pattern libraries with clear dependency rules.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual validation - all sections added cleanly, no placeholder tokens remain, version incremented correctly (MINOR), dates preserved
- Prompt variant (if applicable): Standard constitution amendment workflow
- Next experiment (smallest change to try): Create Module 2-4 directories under `/specs/` to mirror pattern storage structure, validate that Module 1 patterns can be referenced from Module 2+ specs
