---
sidebar_position: 1
title: Module 3 - Perception & Navigation (Isaac & Nav2)
description: Implement VSLAM perception and autonomous navigation with NVIDIA Isaac and Nav2
---

# Module 3: Perception & Navigation

## Overview

This module bridges **perception** (how robots see) with **navigation** (how robots move autonomously). You'll implement Visual SLAM (VSLAM) for localization and Nav2 for path planning, creating truly autonomous systems.

## Key Technologies

### NVIDIA Isaac ROS (Preferred - GPU Accelerated)
- **30 FPS VSLAM**: vs 10 FPS CPU-only
- **15% CPU Usage**: vs 80% with ORB-SLAM3
- **Stereo + Lidar Fusion**: Multi-sensor robustness

### ORB-SLAM3 (CPU Fallback)
- **Universal Compatibility**: Intel Core i5+ without GPU
- **10 FPS**: Sufficient for 0.5 m/s navigation
- **Automatic Detection**: `nvidia-smi` check at runtime

### Nav2 Navigation Stack
- **DWB Local Planner**: Dynamic window approach for obstacles
- **NavFn Global Planner**: Dijkstra-based path planning
- **Costmap Layers**: Static + obstacle + inflation
- **Recovery Behaviors**: Spin, backup, wait

## Learning Objectives

- **LO-007**: Understand VSLAM algorithms and pose estimation
- **LO-008**: Configure Nav2 stack for humanoid constraints
- **LO-009**: Tune planners for dynamic environments

## Module Structure

### Lesson 1: VSLAM Fundamentals
Visual odometry, feature detection, loop closure

### Lesson 2: Isaac ROS Setup
GPU-accelerated VSLAM with NVIDIA hardware

### Lesson 3: CPU SLAM Fallback
ORB-SLAM3 and RTAB-Map alternatives

### Lesson 4: Nav2 Integration
Path planning, costmaps, obstacle avoidance

### Lesson 5: Tuning & Debugging
Recovery behaviors, stuck detection, parameter optimization

## Hands-On Project

Build an autonomous navigation system:
1. Implement VSLAM (Isaac ROS or ORB-SLAM3)
2. Generate occupancy grid map
3. Configure Nav2 with DWB + NavFn
4. Set navigation goals
5. Avoid dynamic obstacles in real-time

## Success Criteria

- ✅ VSLAM: under 5cm pose error
- ✅ Path Planning: Collision-free routes
- ✅ Obstacle Avoidance: Real-time replanning
- ✅ Recovery: Unstuck within 30 seconds

## Next Steps

Start with [Lesson 1: VSLAM Fundamentals](./lesson1-vslam-fundamentals.md) to learn how robots perceive and localize.

---

**💡 Ask the Chatbot**: "How does VSLAM differ from wheel odometry?" or "When should I use Nav2 vs manual control?"
