---
title: "Implementation Guide"
sidebar_position: 3
description: "Step-by-step integration guide for the capstone project."
---

# Capstone Implementation Guide

## Phase 1: ROS 2 Workspace Setup

Set up the project workspace with all required packages:

```bash
mkdir -p ~/capstone_ws/src
cd ~/capstone_ws/src

# Create packages
ros2 pkg create --build-type ament_python capstone_robot_description  # URDF
ros2 pkg create --build-type ament_python capstone_navigation        # Nav2
ros2 pkg create --build-type ament_python capstone_vla               # VLA pipeline
ros2 pkg create --build-type ament_python capstone_bringup           # Launch files

cd ~/capstone_ws
colcon build
source install/setup.bash
```

### Package Responsibilities

| Package | Contents |
|---------|----------|
| `capstone_robot_description` | URDF, meshes, Gazebo world files |
| `capstone_navigation` | Nav2 config, maps, SLAM launch files |
| `capstone_vla` | Speech, LLM, validation, action executor nodes |
| `capstone_bringup` | Top-level launch files, system configuration |

## Phase 2: Simulation Environment

1. Use the humanoid URDF from Module 2 (or enhance it)
2. Create a Gazebo world with rooms, obstacles, and waypoints
3. Add sensors: camera, lidar, IMU
4. Verify robot spawns and physics are stable

```bash
# Test simulation
ros2 launch capstone_bringup simulation.launch.py
```

## Phase 3: Navigation Stack

1. Generate or load a map (VSLAM from Module 3 or pre-built)
2. Configure Nav2 parameters for your robot
3. Test navigation to multiple waypoints
4. Tune obstacle avoidance parameters

```bash
# Test navigation independently
ros2 launch capstone_navigation navigation.launch.py
```

:::tip Test Each Subsystem Independently
Before integration, ensure each subsystem works on its own. Navigation should work with manual goals before connecting VLA.
:::

## Phase 4: VLA Pipeline

1. Set up Whisper transcription node
2. Implement LLM command parser node
3. Add safety validation node
4. Create action executor that sends Nav2 goals
5. Test the full speech-to-action flow

```bash
# Test VLA independently
ros2 launch capstone_vla vla_pipeline.launch.py
```

## Phase 5: System Integration

Connect all subsystems:

```python
# launch/full_system.launch.py
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    return LaunchDescription([
        # Simulation
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource('simulation.launch.py')
        ),
        # Navigation
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource('navigation.launch.py')
        ),
        # VLA Pipeline
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource('vla_pipeline.launch.py')
        ),
    ])
```

### Integration Checklist

- [ ] Simulation publishes sensor data on correct topics
- [ ] Navigation subscribes to sensor topics and publishes cmd_vel
- [ ] VLA pipeline sends goals to Nav2 action server
- [ ] TF tree is complete: map → odom → base_link → sensors
- [ ] Voice commands result in robot movement
- [ ] Safety validation blocks dangerous commands
- [ ] Error recovery works when navigation fails

## Architecture Overview

```
[Microphone] → [Speech Node] → /speech/text
                                     ↓
                              [LLM Parser Node] → /commands/parsed
                                     ↓
                           [Validation Node] → /commands/validated
                                     ↓
                            [Action Executor] → NavigateToPose action
                                     ↓
                              [Nav2 Stack] → /cmd_vel → [Gazebo Robot]
                                     ↑
                              [SLAM/AMCL] ← /scan, /camera
```

## Testing Strategy

1. **Unit**: Test each node independently with mock data
2. **Integration**: Test pairs of connected nodes
3. **System**: Test full pipeline from voice to action
4. **Performance**: Measure end-to-end latency (target under 10s)
5. **Failure**: Test error scenarios and recovery

---

## Common Integration Issues

See the [Debugging Checklist](./debugging-checklist) for systematic troubleshooting.
