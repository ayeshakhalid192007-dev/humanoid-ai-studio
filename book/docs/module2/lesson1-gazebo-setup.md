---
title: "Lesson 1: Gazebo Setup & URDF Spawning"
sidebar_position: 2
description: "Install Gazebo, configure simulation environments, and spawn humanoid robots."
---

# Lesson 1: Gazebo Setup & URDF Spawning

## Prediction Phase

- What does a physics simulator need to accurately model a humanoid robot?
- How does Gazebo communicate with ROS 2 nodes?
- What happens when you spawn a robot without proper inertia properties?

---

## Gazebo Architecture

Gazebo is a 3D robotics simulator with:
- **Physics Engine**: ODE/Bullet for dynamics, collisions, gravity
- **Rendering Engine**: OGRE for 3D visualization
- **Sensor Simulation**: Cameras, lidar, IMU, contact sensors
- **ROS 2 Bridge**: `gazebo_ros` packages for topic/service integration

## Installation

```bash
# Install Gazebo (Ubuntu 22.04)
sudo apt update
sudo apt install gazebo
sudo apt install ros-humble-gazebo-ros-pkgs ros-humble-gazebo-ros2-control

# Verify installation
gazebo --version
```

## World Files

Gazebo worlds define the simulation environment:

```xml
<?xml version="1.0" ?>
<sdf version="1.6">
  <world name="humanoid_world">
    <!-- Ground plane -->
    <include>
      <uri>model://ground_plane</uri>
    </include>

    <!-- Sunlight -->
    <include>
      <uri>model://sun</uri>
    </include>

    <!-- Physics configuration -->
    <physics type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
      <real_time_update_rate>1000</real_time_update_rate>
    </physics>

    <!-- Gravity -->
    <gravity>0 0 -9.81</gravity>
  </world>
</sdf>
```

## Spawning a URDF in Gazebo

Use a ROS 2 launch file to start Gazebo and spawn your robot:

```python
# launch/gazebo_humanoid.launch.py
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_dir = get_package_share_directory('my_robot_description')
    urdf_file = os.path.join(pkg_dir, 'urdf', 'humanoid.urdf')

    with open(urdf_file, 'r') as f:
        robot_description = f.read()

    return LaunchDescription([
        # Start Gazebo
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    get_package_share_directory('gazebo_ros'),
                    'launch', 'gazebo.launch.py'
                )
            ),
        ),

        # Publish robot description
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
        ),

        # Spawn robot in Gazebo
        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=[
                '-topic', 'robot_description',
                '-entity', 'humanoid',
                '-x', '0', '-y', '0', '-z', '1.0'
            ],
        ),
    ])
```

```bash
# Launch simulation
ros2 launch my_robot_description gazebo_humanoid.launch.py
```

:::warning Spawn Height
Always spawn humanoid robots slightly above the ground (z > 0) to prevent initial collision issues. The robot will settle under gravity.
:::

## Gazebo-ROS 2 Integration

Gazebo publishes sensor data and receives commands through ROS 2 topics:

```bash
# List Gazebo topics
ros2 topic list | grep gazebo

# Check joint states
ros2 topic echo /joint_states

# Send joint commands
ros2 topic pub /joint_commands sensor_msgs/msg/JointState "..."
```

---

## Execution Phase

1. Install Gazebo and the ROS 2 integration packages
2. Launch an empty Gazebo world
3. Create a launch file to spawn the URDF from Module 1
4. Verify the robot appears and physics simulation is running
5. Inspect available ROS 2 topics from Gazebo

---

## Reflection

- What happened when the robot was spawned at ground level (z=0)?
- How do the physics step size and real-time factor relate?
- What ROS 2 topics did Gazebo create automatically?
