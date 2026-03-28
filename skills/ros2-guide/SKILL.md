---
name: ros2-guide
description: Step-by-step ROS 2 Humble Hawksbill guidance for the Humanoid AI Studio curriculum. Covers nodes, topics, services, actions, launch files, tf2, Nav2, and ros_gz_bridge integration with Gazebo simulation.
license: MIT
allowed-tools: qdrant_search gemini_generate
metadata:
  author: Ayesha Khalid
  version: "1.0.0"
  category: education
  domain: robotics
  ros_distro: humble
  python_version: "3.10+"
  platform: ubuntu-22.04
---

# ROS 2 Guide Skill

## Purpose

Provide accurate, runnable ROS 2 Humble guidance grounded in the Humanoid AI Studio curriculum. Every code example must be executable in the Standard Testing Environment (Ubuntu 22.04 + ROS 2 Humble Hawksbill).

## Instructions

### For "How do I..." questions
1. Retrieve the relevant curriculum lesson from Qdrant
2. Provide a **3-part answer**:
   - Concept explanation (2–3 sentences)
   - Minimal runnable code example
   - How to verify it works (expected terminal output or `ros2 topic echo` command)

### For error/debugging questions
1. Identify the error type (import error, build error, runtime error, topic mismatch)
2. State the most common cause
3. Provide the fix with before/after code
4. Add one verification step

### For setup/installation questions
Always prefix with:
```bash
source /opt/ros/humble/setup.bash
```

## Curriculum Coverage

| Topic | Module | Lessons |
|---|---|---|
| ROS 2 workspace setup | Module 1 | Lesson 1 |
| Publishers & Subscribers | Module 1 | Lesson 2 |
| Services & Clients | Module 1 | Lesson 3 |
| Launch files | Module 1 | Lesson 4 |
| tf2 transforms | Module 1 | Lesson 5 |
| Nav2 navigation stack | Module 1 | Lesson 6+ |
| Gazebo world creation | Module 2 | Lesson 1 |
| SDF robot models | Module 2 | Lesson 2 |
| ros_gz_bridge setup | Module 2 | Lesson 3 |
| Sensor simulation | Module 2 | Lesson 4 |
| Isaac Sim + Isaac ROS | Module 3 | All lessons |
| VLA model integration | Module 4 | All lessons |

## Standard Commands Reference

```bash
# Source ROS 2
source /opt/ros/humble/setup.bash

# Create a package
ros2 pkg create --build-type ament_python <package_name>

# Build
cd ~/ros2_ws && colcon build --symlink-install

# Run a node
ros2 run <package_name> <node_name>

# List topics
ros2 topic list

# Echo a topic
ros2 topic echo /topic_name

# Launch file
ros2 launch <package_name> <launch_file.py>
```

## Constraints

- Always specify `source /opt/ros/humble/setup.bash` before any ROS 2 command
- Never recommend deprecated ROS 1 (catkin) patterns
- Distinguish between Gazebo Classic (Gazebo 11) and Ignition/Gz — Module 2 uses Gazebo 11
- For GPU-dependent features (Module 3+), note the NVIDIA 6GB+ VRAM requirement
