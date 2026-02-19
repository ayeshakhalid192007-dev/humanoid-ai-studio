---
title: "Project Requirements & Rubric"
sidebar_position: 2
description: "Acceptance criteria, grading rubric, and deliverables for the capstone project."
---

# Capstone Project Requirements & Rubric

## Overview

Build a **voice-commanded autonomous humanoid robot** that integrates all four course modules into a working system demonstrated in a 90-second video.

## Functional Requirements

### Must Have (Pass/Fail)

- [ ] Robot navigates autonomously to at least 3 waypoints
- [ ] Voice commands are transcribed and executed correctly
- [ ] Multi-layer safety validation prevents dangerous actions
- [ ] System runs in Gazebo simulation with a humanoid URDF
- [ ] All communication uses ROS 2 topics, services, and actions

### Should Have (Graded)

- [ ] VSLAM or pre-built map for localization
- [ ] Dynamic obstacle avoidance during navigation
- [ ] LLM-based command parsing with structured output
- [ ] Action feedback displayed to the user
- [ ] Recovery behaviors when robot gets stuck
- [ ] Pipeline latency under 10 seconds

## Demo Requirements

Create a **90-second video** demonstrating:

1. **[0-15s]** System startup and environment overview
2. **[15-45s]** Voice command → transcription → LLM parsing → action execution
3. **[45-70s]** Autonomous navigation with obstacle avoidance
4. **[70-85s]** Error handling (invalid command or obstacle)
5. **[85-90s]** System summary and key metrics

## Grading Rubric

| Category | Weight | Criteria |
|----------|--------|----------|
| **System Integration** | 30% | All modules connected and working together. Clean ROS 2 architecture. |
| **Voice Command Processing** | 20% | Accurate transcription, reliable LLM parsing, structured output. |
| **Autonomous Navigation** | 20% | VSLAM/map-based localization, Nav2 path planning, goal reaching. |
| **Safety Validation** | 15% | Multi-layer validation working, dangerous commands rejected, bounds checking. |
| **Documentation & Demo** | 15% | Clear 90s video, architecture diagram, README with setup instructions. |

### Grade Scale

| Score | Grade | Description |
|-------|-------|-------------|
| 90-100% | A | All features working, polished demo, excellent documentation |
| 80-89% | B | Core features working, minor issues, good documentation |
| 70-79% | C | Most features working, some failures, adequate documentation |
| 60-69% | D | Basic features working, significant issues, minimal documentation |
| &lt;60% | F | Critical features missing or non-functional |

## Deliverables

1. **Source Code**: Complete ROS 2 workspace on GitHub
2. **Demo Video**: 90-second MP4 showing all required features
3. **Architecture Diagram**: System overview showing all components
4. **README**: Setup instructions, dependencies, running instructions
5. **Performance Report**: Latency measurements for each pipeline stage

## Submission

- Push all code to your GitHub repository
- Upload demo video to the repository or shared drive
- Submit the repository URL by the deadline
