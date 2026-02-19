---
sidebar_position: 3
title: Lesson 2 - URDF Robot Modeling
description: Define humanoid robot structure using URDF with joints, links, and constraints
---

# Lesson 2: URDF Robot Modeling

## Overview

URDF (Unified Robot Description Format) is the XML-based language for defining robot structure. In this lesson, you'll learn how to model a humanoid robot with joints, links, collision geometry, and visual meshes.

## What is URDF?

URDF describes:
- **Links**: Rigid bodies (torso, arms, legs, head)
- **Joints**: Connections between links with motion constraints
- **Sensors**: Cameras, lidar, IMU placement
- **Actuators**: Motors and their control interfaces

**Analogy**: URDF is like a skeleton blueprint - it defines how bones (links) connect via joints, what they look like, and how they can move.

## Basic URDF Structure

```xml
<?xml version="1.0"?>
<robot name="simple_humanoid">
  <!-- Links define rigid bodies -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.3 0.3 0.5"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 0.8 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.3 0.3 0.5"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="10.0"/>
      <inertia ixx="1.0" ixy="0" ixz="0" iyy="1.0" iyz="0" izz="1.0"/>
    </inertial>
  </link>

  <!-- Joints define motion between links -->
  <joint name="hip_joint" type="revolute">
    <parent link="base_link"/>
    <child link="leg_link"/>
    <origin xyz="0 0 -0.25" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" effort="100" velocity="1.0"/>
  </joint>

  <link name="leg_link">
    <visual>
      <geometry>
        <cylinder length="0.8" radius="0.05"/>
      </geometry>
    </visual>
  </link>
</robot>
```

## Joint Types

### 1. Revolute (Hinge)
- Rotates around an axis
- Has **joint limits** (min/max angle)
- Example: Elbow, knee, hip

```xml
<joint name="elbow" type="revolute">
  <limit lower="-2.0" upper="0.0" effort="50" velocity="2.0"/>
</joint>
```

### 2. Prismatic (Slider)
- Linear motion along an axis
- Example: Telescoping arm

```xml
<joint name="extend_arm" type="prismatic">
  <limit lower="0.0" upper="0.5" effort="100" velocity="0.5"/>
</joint>
```

### 3. Fixed (Rigid)
- No motion - permanently attached
- Example: Camera mount, sensor bracket

```xml
<joint name="camera_mount" type="fixed"/>
```

### 4. Continuous (Unlimited Rotation)
- Rotates 360° without limits
- Example: Wheel, turret

```xml
<joint name="wheel_joint" type="continuous">
  <axis xyz="0 0 1"/>
</joint>
```

## Joint Limits Explained

```xml
<limit lower="-1.57" upper="1.57" effort="100" velocity="1.0"/>
```

- **lower/upper**: Angle limits in radians (-90° to +90° here)
- **effort**: Maximum force/torque (Nm)
- **velocity**: Maximum speed (rad/s)

**Why Limits Matter**: Prevents:
- Self-collision (arm hitting torso)
- Workspace violations (reaching impossible positions)
- Joint damage in physical robots

## Prediction Exercise

Given this hip joint:
```xml
<joint name="hip_pitch" type="revolute">
  <limit lower="-0.5" upper="1.5" effort="150" velocity="2.0"/>
</joint>
```

**Questions** (predict before running):
1. Can the leg bend backward past the torso?
2. What's the maximum forward bend angle in degrees?
3. What happens if you command 2.0 radians?

<details>
<summary>Answers (expand after predicting)</summary>

1. **No** - lower limit -0.5 rad (-28.6°) prevents significant backward bend
2. **85.9 degrees** - upper limit 1.5 rad = 85.9°
3. **Clamped to 1.5 rad** - ROS 2 joint controller enforces limits, logs warning

</details>

## Complete Humanoid Example

```xml
<?xml version="1.0"?>
<robot name="basic_humanoid">
  <!-- Torso -->
  <link name="torso">
    <visual>
      <geometry>
        <box size="0.4 0.3 0.6"/>
      </geometry>
      <material name="gray">
        <color rgba="0.5 0.5 0.5 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.4 0.3 0.6"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="15.0"/>
      <inertia ixx="1.5" iyy="1.2" izz="1.0" ixy="0" ixz="0" iyz="0"/>
    </inertial>
  </link>

  <!-- Left Leg -->
  <joint name="left_hip" type="revolute">
    <parent link="torso"/>
    <child link="left_thigh"/>
    <origin xyz="0.1 0 -0.3" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-0.5" upper="1.5" effort="150" velocity="2.0"/>
  </joint>

  <link name="left_thigh">
    <visual>
      <geometry>
        <cylinder length="0.5" radius="0.06"/>
      </geometry>
    </visual>
    <collision>
      <geometry>
        <cylinder length="0.5" radius="0.06"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="3.0"/>
      <inertia ixx="0.1" iyy="0.1" izz="0.05" ixy="0" ixz="0" iyz="0"/>
    </inertial>
  </link>

  <joint name="left_knee" type="revolute">
    <parent link="left_thigh"/>
    <child link="left_shin"/>
    <origin xyz="0 0 -0.25" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="0.0" upper="2.5" effort="100" velocity="2.0"/>
  </joint>

  <link name="left_shin">
    <visual>
      <geometry>
        <cylinder length="0.5" radius="0.05"/>
      </geometry>
    </visual>
  </link>

  <!-- Right Leg (symmetric) -->
  <!-- ... similar structure ... -->

  <!-- Head with Camera -->
  <joint name="neck" type="revolute">
    <parent link="torso"/>
    <child link="head"/>
    <origin xyz="0 0 0.4" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-1.57" upper="1.57" effort="20" velocity="1.0"/>
  </joint>

  <link name="head">
    <visual>
      <geometry>
        <sphere radius="0.15"/>
      </geometry>
    </visual>
  </link>
</robot>
```

## Spawning in Gazebo

To spawn your URDF in Gazebo:

```bash
# Save URDF as humanoid.urdf
ros2 run gazebo_ros spawn_entity.py \
  -entity humanoid \
  -file humanoid.urdf \
  -x 0 -y 0 -z 1.0
```

## Visualization in RViz

```bash
# Launch robot_state_publisher
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:="$(cat humanoid.urdf)"

# Launch RViz
rviz2
```

In RViz:
1. Add → RobotModel
2. Set Fixed Frame to "torso"
3. See your robot visualized!

## Common Issues

### Issue 1: "Error: joint limit violated"
**Cause**: Commanded angle outside lower/upper limits
**Solution**: Check joint limits in URDF, adjust command

### Issue 2: "Robot falls through floor"
**Cause**: Missing collision geometry
**Solution**: Add `<collision>` tags to all links

### Issue 3: "Joint moves too slowly"
**Cause**: `velocity` limit too low
**Solution**: Increase `velocity` value in joint limit

## Acceptance Criteria

You've completed this lesson when you can:
- ✅ Write URDF with multiple links and joints
- ✅ Explain the difference between revolute and prismatic joints
- ✅ Predict which commands will violate joint limits
- ✅ Spawn your URDF in Gazebo
- ✅ Visualize robot in RViz

## Next Steps

Continue to [Lesson 4: Services](./lesson4-services.md) to learn request-response patterns in ROS 2.

---

**💡 Ask the Chatbot**:
- "How do I debug 'joint limit violated' errors?"
- "What's the difference between visual and collision geometry?"
- "How do inertia values affect simulation physics?"
