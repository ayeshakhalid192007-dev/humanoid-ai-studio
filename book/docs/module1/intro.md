---
sidebar_position: 1
title: Module 1 - The Robotic Nervous System (ROS 2)
description: Master ROS 2 Humble middleware for robot control and coordination
---

# Module 1: The Robotic Nervous System (ROS 2)

## Overview

ROS 2 (Robot Operating System 2) is the **middleware nervous system** that connects sensors, actuators, and decision-making algorithms in modern robots. Just as the human nervous system coordinates signals between the brain and body, ROS 2 coordinates message flow between robot components.

## Learning Objectives

By the end of this module, you will be able to:

- **LO-001**: Predict message flow in pub/sub systems
- **LO-002**: Debug node communication failures using CLI tools
- **LO-003**: Design service-based control interfaces
- **LO-004**: Reason about URDF joint limits and workspace constraints
- **LO-005**: Explain when to use topics vs services vs action servers

## Why ROS 2 Humble?

We use **ROS 2 Humble Hawksbill** because:
- ✅ **LTS Support**: 5-year support until May 2027
- ✅ **Stability**: Mature ecosystem since May 2022
- ✅ **Ubuntu 22.04 Native**: No custom PPAs needed
- ✅ **Nav2 Compatible**: Tested with navigation stack
- ✅ **Isaac ROS Ready**: NVIDIA GPU acceleration support

## Module Structure

### Lesson 1: ROS 2 Fundamentals
Learn nodes, topics, and the publish-subscribe pattern with hands-on talker/listener examples.

### Lesson 2: URDF Robot Modeling
Define humanoid robot structure using URDF (Unified Robot Description Format) with joints, links, and constraints.

### Lesson 3: Services & Actions
Implement request-response patterns for discrete robot control and long-running behaviors.

### Lesson 4: Quality of Service (QoS)
Configure message delivery guarantees for critical control commands vs high-frequency sensor data.

## Hands-On Project

Build a complete ROS 2 workspace with:
1. A talker node publishing velocity commands
2. A listener node consuming commands and logging
3. A service for discrete actions (e.g., "stop robot")
4. RQT visualization of the node graph

## Next Steps

Start with [Lesson 1: ROS 2 Fundamentals](./lesson1-ros2-basics.md) to install ROS 2 Humble and create your first nodes.

---

**💡 Ask the Chatbot**: "What's the difference between ROS 1 and ROS 2?" or "How do I install ROS 2 Humble on Ubuntu 22.04?"
