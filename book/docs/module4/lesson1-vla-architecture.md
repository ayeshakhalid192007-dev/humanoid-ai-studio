---
title: "Lesson 1: VLA Pipeline Architecture"
sidebar_position: 2
description: "Understanding the Voice-Language-Action pipeline for robot command and control."
---

# Lesson 1: Voice-Language-Action Pipeline Architecture

## Prediction Phase

- What steps are needed between a spoken command and a robot action?
- Where are the biggest latency bottlenecks in a voice-controlled robot?
- How do you ensure a robot doesn't execute dangerous commands?

---

## Pipeline Overview

The Voice-Language-Action (VLA) pipeline transforms human speech into robot actions through five stages:

```
Voice Input → Speech-to-Text → Language Understanding → Action Planning → Robot Execution
   (Mic)       (Whisper)          (LLM)                  (Planner)        (ROS 2)
```

### Stage 1: Speech Capture
- Microphone captures audio
- Noise filtering and voice activity detection
- Audio buffered for transcription

### Stage 2: Speech-to-Text
- Whisper or Google Speech API transcribes audio
- Outputs text with confidence score
- Handles accents, noise, domain vocabulary

### Stage 3: Language Understanding
- LLM parses the command intent
- Extracts parameters (target, speed, distance)
- Maps to available robot actions

### Stage 4: Action Planning
- Validates command against safety constraints
- Plans execution sequence (joint trajectories, navigation goals)
- Simulation pre-check for safety-critical actions

### Stage 5: Robot Execution
- Sends commands via ROS 2 action servers
- Monitors execution progress (feedback)
- Reports completion or failure to user

## Real-World VLA Systems

| System | Developer | Approach |
|--------|-----------|----------|
| **RT-2** | Google DeepMind | Vision-Language-Action model (end-to-end) |
| **PaLM-E** | Google | Multimodal LLM with embodied reasoning |
| **SayCan** | Google | LLM grounds language in robot affordances |
| **Code as Policies** | Google | LLM generates robot control code |
| **ChatGPT + ROS** | Community | LLM API with ROS 2 integration |

:::info Our Approach
In this course, we use a **modular pipeline** (separate components for each stage) rather than an end-to-end model. This is more practical for learning, debugging, and deployment on standard hardware.
:::

## Data Flow Example

Command: *"Walk to the kitchen table and pick up the red cup"*

```
Speech-to-Text: "walk to the kitchen table and pick up the red cup"
         ↓
LLM Parsing: {
  actions: [
    {type: "navigate", target: "kitchen_table"},
    {type: "grasp", object: "red_cup"}
  ]
}
         ↓
Validation: ✓ navigate - valid waypoint
            ✓ grasp - object in known inventory
         ↓
Execution: 1. Nav2 goal → kitchen_table coordinates
           2. Arm action → grasp sequence for cup
```

## Latency Budget

Target: **under 10 seconds** from voice command to action start

| Stage | Target | Technology |
|-------|--------|-----------|
| Speech capture | 0.5-2s | Voice activity detection |
| Transcription | 1-3s | Whisper (streaming) |
| LLM parsing | 1-3s | GPT-4o-mini |
| Validation | &lt;0.1s | Local checks |
| Action start | &lt;0.5s | ROS 2 action client |
| **Total** | **3-9s** | |

---

## Execution Phase

1. Diagram the VLA pipeline for a specific robot task
2. Identify the latency contribution of each stage
3. Consider what safety checks each stage should perform
4. Map which ROS 2 communication pattern (topic/service/action) fits each stage

---

## Reflection

- Which pipeline stage is the biggest bottleneck?
- What are the advantages of a modular pipeline vs. end-to-end?
- How would you handle ambiguous commands like "go there"?
