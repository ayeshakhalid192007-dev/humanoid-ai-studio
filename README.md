# Physical AI & Humanoid Robotics Platform

An interactive learning platform featuring a Docusaurus-based curriculum book with an embedded RAG chatbot for AI-assisted learning.

## Quick Start

For detailed setup instructions, see **[quickstart.md](specs/001-book-publication-rag-chatbot/quickstart.md)**

## Project Overview

This project follows a **Specification-Driven Development with Reusable Intelligence (SDD-RI)** methodology, ensuring every lesson, code pattern, and robot behavior is clearly specified, testable, and reusable across modules.

A comprehensive 4-module educational program that bridges AI, robotics, and physical embodiment, culminating in an autonomous humanoid robot system.

### Constitution

The project is governed by a constitution at `.specify/memory/constitution.md` (v1.2.0) that establishes:
- **6 Core Principles**: Reasoning-First Learning, System-Oriented Architecture, Python-ROS 2 Bridge Patterns, Interactive Verification, Modularity and Scalability, SDD-RI
- **Comprehensive Governance**: Principle hierarchy, enforcement mechanisms, testing standards, stakeholder participation
- **Cross-Module Standards**: Learning outcomes (LO-001 to LO-303), pattern versioning, observable outcome requirements

## Curriculum

### Module 1: The Robotic Nervous System (ROS 2)
**Focus**: Middleware for robot control

- ROS 2 Nodes, Topics, and Services
- Bridging Python Agents to ROS controllers using `rclpy`
- Understanding URDF (Unified Robot Description Format) for humanoids

**Learning Outcomes**:
- LO-001: Predict message flow through ROS 2 graphs
- LO-002: Write Python nodes controlling URDF-defined joints
- LO-003: Debug node communication using CLI tools
- LO-004: Reason about URDF joint limits and workspace constraints
- LO-005: Explain when to use topics vs services vs action servers

**Pattern Library**: `/specs/module-1-ros2/patterns/`

---

### Module 2: The Digital Twin (Gazebo & Unity)
**Focus**: Physics simulation and environment building

- Simulating physics, gravity, and collisions in Gazebo
- High-fidelity rendering and human-robot interaction in Unity
- Simulating sensors: LiDAR, Depth Cameras, and IMUs

**Learning Outcomes**:
- LO-101: Configure sensor plugins and predict sensor output formats
- LO-102: Debug physics simulation failures (collision, gravity, friction)
- LO-103: Transfer Module 1 ROS 2 nodes to simulated environments

**Pattern Library**: `/specs/module-2-simulation/patterns/`

---

### Module 3: The AI-Robot Brain (NVIDIA Isaac™)
**Focus**: Advanced perception and training

- NVIDIA Isaac Sim: Photorealistic simulation and synthetic data generation
- Isaac ROS: Hardware-accelerated VSLAM (Visual SLAM) and navigation
- Nav2: Path planning for bipedal humanoid movement

**Learning Outcomes**:
- LO-201: Generate synthetic training data and validate against real-world distributions
- LO-202: Configure and debug VSLAM pipeline failures
- LO-203: Implement Nav2 path planning for bipedal constraints

**Pattern Library**: `/specs/module-3-isaac/patterns/`

---

### Module 4: Vision-Language-Action (VLA)
**Focus**: Convergence of LLMs and Robotics

- Voice-to-Action: Using OpenAI Whisper for voice commands
- Cognitive Planning: Translating natural language instructions into ROS 2 action sequences
- **Capstone Project**: Autonomous Humanoid – simulated robot executes voice commands, plans paths, navigates obstacles, identifies objects, and manipulates them

**Learning Outcomes**:
- LO-301: Decompose natural language commands into ROS 2 action sequences
- LO-302: Integrate voice → perception → planning → manipulation pipeline
- LO-303: Evaluate end-to-end system performance against voice command accuracy

**Pattern Library**: `/specs/module-4-vla/patterns/`

---

## Pedagogical Approach

### Reasoning-First Learning (NON-NEGOTIABLE)
Every lesson follows the **Prediction → Execution → Reflection** cycle:

1. **Prediction Phase**: "Before running, what will this node publish?"
2. **Execution Phase**: Run code, capture output
3. **Reflection Phase**: "Did output match prediction? Why/why not?"
4. **Extension Challenge**: Modify code to achieve new behavior

**Why?** Passive tutorials fail to build intuition. Active prediction improves retention by 30-50% and engages higher-order thinking (Bloom's Taxonomy: Analysis and Evaluation levels).

### System-Oriented Architecture
ROS 2 is taught as an integrated **nervous system**:
- **Nodes** = neural pathways (message producers/consumers)
- **Topics** = sensory/motor signals
- **Services** = deliberate control actions
- **URDF** = structural blueprint connecting physical and logical layers

### Interactive Verification
All concepts include:
- Executable code snippets (students run them)
- Observable outcomes (terminal output, robot motion, RViz visualization)
- Prediction checkpoints ("What will happen when...")
- Error scenarios and debugging guidance

## Standard Testing Environment

All code is validated against:
- **OS**: Ubuntu 22.04 LTS (Jammy)
- **ROS 2**: Humble Hawksbill (LTS, supported until 2027)
- **Gazebo**: Gazebo 11 (Module 2)
- **Isaac Sim**: NVIDIA Isaac Sim 2023.1.1 (Module 3)
- **Python**: 3.10+
- **Hardware**: NVIDIA GPU with 6GB+ VRAM, 16GB system RAM

**Testing Protocol**:
1. Fresh Docker container: `osrf/ros:humble-desktop-full`
2. Install only documented dependencies
3. Execute all code snippets in lesson order
4. Verify predictions match outcomes (screenshot/log comparison)
5. Document deviations with reproduction steps

## Observable Outcome Standards

Predictions must be verifiable:
- **Quantitative**: Joint position ±2°, execution time ±0.5s, message rate ±10%
- **Visual**: RViz visualization shows expected robot state
- **Logs**: Terminal output matches predicted message structure
- **Failure modes**: Document 2-3 common errors with diagnostic signatures

**Rejected examples** (too vague):
- ❌ "The robot moves"
- ❌ "Check if it works"
- ❌ "Output appears in terminal"

**Acceptable examples**:
- ✅ "Right arm joint 3 rotates to 45° ±2° in 2.0s ±0.5s"
- ✅ "RViz shows gripper open (joint value > 0.08m)"
- ✅ "Terminal prints: `[INFO] [joint_controller]: Target reached` within 3 seconds"

## Project Structure

```
physical_ai/
├── .specify/
│   ├── memory/
│   │   └── constitution.md           # Project governance (v1.2.0)
│   ├── templates/                     # Spec, plan, tasks templates
│   └── scripts/                       # Automation scripts
├── specs/
│   ├── module-1-ros2/
│   │   ├── patterns/                  # Reusable agent patterns
│   │   ├── spec.md                    # Feature specifications
│   │   ├── plan.md                    # Architecture decisions
│   │   └── tasks.md                   # Testable tasks
│   ├── module-2-simulation/
│   ├── module-3-isaac/
│   └── module-4-vla/
├── history/
│   ├── prompts/
│   │   └── constitution/              # Constitution amendment PHRs
│   └── adr/                           # Architecture Decision Records
└── README.md                          # This file
```

## Getting Started

### For Students
1. **Prerequisites**: Ubuntu 22.04, ROS 2 Humble installed
2. **Start with Module 1**: Begin with `specs/module-1-ros2/lesson-01/`
3. **Follow prediction-execution-reflection cycle** for every lesson
4. **Build pattern library** as you progress

### For Instructors
1. **Review constitution**: `.specify/memory/constitution.md`
2. **Use templates**: `/sp.specify` for specs, `/sp.plan` for architecture, `/sp.tasks` for task breakdown
3. **Report issues**: GitHub issue tracker with `pedagogy` label
4. **Quarterly feedback**: Complete student surveys to assess principle effectiveness

### For Contributors
1. **Read governance**: Constitution Section "Enforcement and Accountability"
2. **Follow SDD-RI**: Specify → Plan → Implement → Validate
3. **Document patterns**: All Python-ROS 2 bridges must be reusable
4. **Validate in Standard Testing Environment** before submitting

## Governance

**Review Authority**: Designated curriculum maintainers (minimum 2) with veto power

**Violation Response**:
- **Minor** (formatting, unclear wording): 7-day fix window
- **Major** (missing prediction checkpoints, untested code): Blocked from release
- **Repeat**: Contributor escalation to project governance

**Appeals Process**: Document conflict → Propose alternative → 75% maintainer consensus

**Emergency Authority**: For security/safety/legal issues, single maintainer can fast-track changes (retroactive 14-day review)

## Stakeholder Participation

- **Student Feedback**: Quarterly surveys
- **Industry Advisory**: Annual review (Boston Dynamics, NVIDIA, Tesla practitioners)
- **Instructor Input**: GitHub issue tracker (`pedagogy` label)
- **Amendment Proposals**: Any stakeholder can propose via GitHub issue

## Principle Hierarchy (Conflict Resolution)

When principles conflict:
1. **Reasoning-First Learning (I)** - NON-NEGOTIABLE
2. **Interactive Verification (IV)** - Core pedagogy
3. **System-Oriented Architecture (II)** - Conceptual foundation
4. **Modularity and Scalability (V)** - Structural requirement
5. **Python-ROS 2 Bridge Patterns (III)** - Implementation detail
6. **SDD-RI (VI)** - Documentation standard

Unresolvable conflicts → Escalate to constitution amendment.

## Version History

- **v1.2.0** (2026-02-07): Added comprehensive governance framework (enforcement, testing standards, stakeholder participation)
- **v1.1.0** (2026-02-07): Added 4-module curriculum overview
- **v1.0.0** (2026-02-07): Initial constitution with 6 core principles

## License

[To be determined by project maintainers]

## Contact

[To be added: Maintainer contact information, Discord/Slack community links]

---

**Constitution Version**: 1.2.0 | **Last Updated**: 2026-02-07
