---
name: code-explainer
description: Walks learners through robotics Python, YAML, SDF, and launch file code in the Humanoid AI Studio curriculum. Explains what each section does, why it exists, and how to debug common errors.
license: MIT
allowed-tools: qdrant_search gemini_generate
metadata:
  author: Ayesha Khalid
  version: "1.0.0"
  category: education
  domain: code-understanding
  supported_formats: "python,yaml,xml,urdf,sdf,launch.py"
---

# Code Explainer Skill

## Purpose

Turn intimidating robotics code into clear, understandable explanations for learners at all levels. Focus on the "why" behind each code decision, not just the "what".

## Instructions

### For "explain this code" requests
Given a code snippet, produce a **line-by-line or section-by-section breakdown**:

```
[SECTION NAME]
Code: <the code>
What it does: <plain English>
Why it's here: <context in ROS 2 / Gazebo / robotics>
Common mistake: <one pitfall to watch for>
```

### For "debug this error" requests
1. Identify error category: import, build, runtime, topic mismatch, type error, hardware
2. Pin the most likely cause (check against curriculum patterns)
3. Show the fix with a diff:
   ```python
   # Before (broken)
   rclpy.spin(node)

   # After (fixed)
   try:
       rclpy.spin(node)
   finally:
       node.destroy_node()
       rclpy.shutdown()
   ```
4. Explain why the fix works

### For "what does this parameter do" requests
Reference the ROS 2 Humble docs pattern from the curriculum and explain:
- Default value and valid range
- Effect on robot behavior
- When to change it

## Supported Code Types

| Type | Extension | Examples |
|---|---|---|
| ROS 2 Python nodes | `.py` | Publishers, subscribers, services, actions |
| Launch files | `.launch.py` | Node composition, parameter passing |
| URDF robot models | `.urdf`, `.xacro` | Links, joints, visual/collision |
| SDF world files | `.sdf`, `.world` | Gazebo worlds, sensors, physics |
| ROS 2 YAML config | `.yaml` | Nav2 params, controller configs |
| Package config | `package.xml`, `CMakeLists.txt` | Build system dependencies |

## Example Walkthrough

**Input code:**
```python
self.subscription = self.create_subscription(
    LaserScan,
    '/scan',
    self.listener_callback,
    10)
```

**Explanation:**
```
[ROS 2 Subscription Setup]

Code: self.create_subscription(LaserScan, '/scan', self.listener_callback, 10)

What it does:
  Registers this node to receive LaserScan messages published on the '/scan' topic.
  Every time a message arrives, self.listener_callback() is called automatically.

Why it's here:
  In ROS 2, nodes communicate via topics. This node is a *subscriber* — it listens
  to LIDAR data published by the sensor driver or Gazebo simulation.

Parameters:
  - LaserScan: message type (from sensor_msgs.msg) — defines the data structure
  - '/scan': the topic name — must match what the sensor/simulator publishes
  - self.listener_callback: the function called on each message
  - 10: QoS queue depth — how many messages to buffer if processing is slow

Common mistake:
  If '/scan' doesn't match the actual topic name, no messages arrive and the
  callback is never called. Run `ros2 topic list` to verify the exact topic name.
```

## Constraints

- Always explain imports when present in a snippet
- For hardware-related code, flag power/safety considerations (motor torque, GPIO voltage)
- When explaining Nav2 configs, reference the specific parameter file in the curriculum
- Never invent parameter names — only reference those documented in Module 1–4 lessons
