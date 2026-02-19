---
sidebar_position: 1
title: Module 2 - The Digital Twin (Simulation)
description: Master Gazebo and Unity for physics-based robot simulation
---

# Module 2: The Digital Twin (Gazebo & Unity)

## Overview

Before deploying to physical hardware, we test in **simulation** - a digital twin where physics, sensors, and environments are realistically modeled. This module teaches you to build and validate robot behaviors in Gazebo (mandatory) and Unity (optional advanced track).

## Why Simulation First?

✅ **Safety**: No risk of hardware damage
✅ **Speed**: Faster iteration cycles
✅ **Repeatability**: Exact same conditions every test
✅ **Cost**: Zero hardware required
✅ **Scale**: Test 20+ scenarios in parallel

## Learning Objectives

- **LO-004**: Understand URDF robot modeling and spawning
- **LO-005**: Configure physics engines (ODE, Bullet)
- **LO-006**: Generate and interpret simulated sensor data

## Tools

### Gazebo 11+ (Mandatory)
- **Open-source**: Zero licensing cost
- **ROS 2 Native**: Direct topic integration via `ros_gz_bridge`
- **Physics**: ODE/Bullet engines for humanoid stability
- **Sensors**: RGB/depth cameras, lidar, IMU

### Unity + Isaac Sim (Optional)
- **Advanced Track**: Requires NVIDIA GPU (RTX 2060+)
- **Photorealistic**: Computer vision research quality
- **Isaac Integration**: NVIDIA Omniverse pathway

## Module Structure

### Lesson 1: Gazebo Fundamentals
Install Gazebo, spawn URDF robots, configure worlds

### Lesson 2: Physics Engines
Tune gravity, friction, collision parameters for stability

### Lesson 3: Sensor Simulation
RGB cameras, depth maps, lidar point clouds, IMU data

### Lesson 4: Unity Integration (Advanced)
Photorealistic rendering, Isaac Sim connection

## Hands-On Project

Build a complete simulation environment:
1. Spawn humanoid robot from URDF
2. Configure realistic physics (gravity, collisions)
3. Add lidar and depth camera sensors
4. Publish sensor data to ROS 2 topics
5. Visualize in RViz

## Next Steps

Start with [Lesson 1: Gazebo Setup](./lesson1-gazebo-setup.md) to install and configure your simulation environment.

---

**💡 Ask the Chatbot**: "How do I fix physics instability in Gazebo?" or "What's the difference between Gazebo and Unity for robotics?"
