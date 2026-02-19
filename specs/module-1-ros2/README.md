# Module 1: The Robotic Nervous System (ROS 2)

**Focus**: Middleware for robot control

## Overview

This module teaches students how ROS 2 acts as the **nervous system** of a robot, coordinating communication between sensors, controllers, and actuators. Students learn to bridge Python AI agents to physical robot controllers, understand URDF robot descriptions, and master the prediction-execution-reflection learning cycle.

## Learning Outcomes

By completing Module 1, students will be able to:

- **LO-001**: Predict message flow through a 3-node ROS 2 graph before execution
- **LO-002**: Write a Python node that controls a URDF-defined joint
- **LO-003**: Debug node communication failures using ROS 2 CLI tools (`ros2 topic echo`, `ros2 node info`)
- **LO-004**: Reason about URDF joint limits and workspace constraints
- **LO-005**: Explain when to use topics vs services vs action servers

## Prerequisites

### Required Knowledge
- Basic Python programming (functions, classes, imports)
- Command-line familiarity (cd, ls, running scripts)
- Basic understanding of robotics concepts (joints, sensors, actuators)

### System Requirements
- **OS**: Ubuntu 22.04 LTS (Jammy Jellyfish)
- **ROS 2**: Humble Hawksbill (LTS)
- **Python**: 3.10+
- **RAM**: 8GB minimum (16GB recommended)
- **Disk**: 20GB free space

### Installation

```bash
# Install ROS 2 Humble (if not already installed)
sudo apt update
sudo apt install ros-humble-desktop-full

# Install Python dependencies
sudo apt install python3-pip python3-colcon-common-extensions

# Source ROS 2 environment
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc

# Verify installation
ros2 --version
```

## Module Structure

### Lesson 1: ROS 2 Nodes and Topics
**Objective**: Understand nodes as computational units and topics as communication channels

**Key Concepts**:
- What is a node? (Python process running ROS 2 code)
- What is a topic? (Named bus for messages)
- Publisher-Subscriber pattern

**Prediction Exercise**: Before running code, predict message flow

**Files**: `lesson-01/`

---

### Lesson 2: Message Types and QoS
**Objective**: Understand message schemas and Quality of Service profiles

**Key Concepts**:
- Standard message types (`std_msgs`, `geometry_msgs`)
- QoS profiles (Reliable vs Best Effort)
- Type safety and schema validation

**Prediction Exercise**: Predict QoS mismatch failures

**Files**: `lesson-02/`

---

### Lesson 3: URDF - Robot Description
**Objective**: Parse URDF files to understand robot structure

**Key Concepts**:
- Links and joints
- Joint types (revolute, prismatic, fixed)
- Joint limits and constraints
- Coordinate frames

**Prediction Exercise**: Predict workspace from URDF limits

**Files**: `lesson-03/`

---

### Lesson 4: Controlling Joints with Python
**Objective**: Write Python nodes that command robot joints

**Key Concepts**:
- `rclpy` basics (node initialization, spin, shutdown)
- Publishing joint commands
- Reading URDF-defined limits
- Rate limiting (Hz)

**Prediction Exercise**: Predict joint motion from command sequence

**Files**: `lesson-04/`

---

### Lesson 5: Services - Request-Response
**Objective**: Understand services for deliberate actions

**Key Concepts**:
- When to use services vs topics
- Service definitions (`.srv` files)
- Client-server pattern
- Synchronous vs asynchronous calls

**Prediction Exercise**: Predict service call latency

**Files**: `lesson-05/`

---

### Lesson 6: Action Servers - Long-Running Tasks
**Objective**: Use action servers for tasks with feedback

**Key Concepts**:
- Action definitions (goal, result, feedback)
- Preemption and cancellation
- Progress reporting
- When to use actions vs services

**Prediction Exercise**: Predict action execution timeline

**Files**: `lesson-06/`

---

### Lesson 7: Debugging with CLI Tools
**Objective**: Master ROS 2 command-line debugging

**Key Concepts**:
- `ros2 node list`, `ros2 node info`
- `ros2 topic echo`, `ros2 topic hz`
- `ros2 service call`
- `ros2 param` commands

**Prediction Exercise**: Predict output of CLI commands

**Files**: `lesson-07/`

---

### Lesson 8: Capstone - Humanoid Arm Controller
**Objective**: Build a complete arm controller integrating all concepts

**Requirements**:
- Read URDF for 6-DOF humanoid arm
- Accept voice commands (placeholder: keyboard input)
- Validate commands against joint limits
- Publish joint trajectories
- Provide feedback on progress

**Prediction Exercise**: Predict full command → motion pipeline

**Files**: `lesson-08-capstone/`

---

## Reusable Patterns

All Python-ROS 2 bridge code is documented as reusable patterns in `/patterns/`:

- **Node Controller Pattern**: How AI agents instantiate and manage ROS 2 nodes
- **Topic Monitor Pattern**: How agents subscribe to sensor topics and reason about data
- **Service Caller Pattern**: How agents invoke ROS 2 services with validated requests
- **URDF Parser Pattern**: How agents extract joint limits, link names, kinematic chains from URDF

**Pattern Compatibility**: `ros2-humble`, forward-compatible with Gazebo (Module 2), Isaac Sim (Module 3)

## Testing

All code snippets are validated in the **Standard Testing Environment**:

```bash
# Run from Docker container
docker run -it --rm \
  -v $(pwd):/workspace \
  osrf/ros:humble-desktop-full \
  bash

# Inside container
cd /workspace/specs/module-1-ros2/lesson-01
python3 simple_publisher.py
```

### Observable Outcome Checklist
- [ ] Code executes without errors
- [ ] Prediction matches actual output (±tolerances)
- [ ] RViz visualization shows expected state (if applicable)
- [ ] Terminal logs match predicted message structure
- [ ] Common errors documented with diagnostic signatures

## Pedagogical Approach

### Prediction-Execution-Reflection Cycle

Every lesson follows this structure:

**1. Prediction Phase**
- Read code (DO NOT run yet)
- Answer: "What will this node publish?"
- Write down your prediction (message type, rate, values)

**2. Execution Phase**
- Run the code
- Capture output (screenshot, copy terminal logs)
- Observe RViz visualization (if applicable)

**3. Reflection Phase**
- Compare prediction vs outcome
- Answer: "Did they match? Why/why not?"
- Identify mental model gaps

**4. Extension Challenge**
- Modify code to achieve new behavior
- Predict the change before running
- Verify your understanding

### Why This Works

**Evidence**:
- **Bloom's Taxonomy**: Prediction engages "Analysis" and "Evaluation" (higher-order thinking)
- **Retrieval Practice**: Active prediction improves retention by 30-50% vs passive reading
- **Industry Feedback**: 80% of robotics employers cite "debugging ability" as top skill gap

## Common Pitfalls

### 1. QoS Mismatch
**Symptom**: Node publishes but subscriber receives nothing
**Diagnosis**: Run `ros2 topic info /topic_name --verbose`
**Fix**: Match QoS profiles (both Reliable or both Best Effort)

### 2. Joint Limit Violations
**Symptom**: URDF parser error or robot motion clipped
**Diagnosis**: Check joint limits in URDF `<limit lower="X" upper="Y" />`
**Fix**: Validate commands against limits before publishing

### 3. Node Discovery Delay
**Symptom**: First few messages lost
**Diagnosis**: ROS 2 discovery takes ~1-2 seconds
**Fix**: Add `time.sleep(2)` after node initialization

## Next Steps

After completing Module 1:

1. **Module 2**: Transfer your ROS 2 nodes to Gazebo simulator
2. **Pattern Library**: Review `/patterns/` for reusable code
3. **Capstone Extension**: Add voice recognition (Whisper) in Module 4

## Resources

- **ROS 2 Humble Docs**: https://docs.ros.org/en/humble/
- **rclpy API Reference**: https://docs.ros2.org/humble/api/rclpy/
- **URDF Spec**: http://wiki.ros.org/urdf/XML
- **Constitution**: `../../.specify/memory/constitution.md`

## Support

- **Report Issues**: GitHub issue tracker with `module-1` label
- **Pedagogical Questions**: Use `pedagogy` label
- **Technical Questions**: Use `technical` label

---

**Module Version**: 1.0.0 | **Created**: 2026-02-07 | **Compatible with**: ROS 2 Humble, Ubuntu 22.04
