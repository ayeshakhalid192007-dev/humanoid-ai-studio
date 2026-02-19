---
title: "Lesson 4: Nav2 Navigation Stack"
sidebar_position: 5
description: "Configure the ROS 2 Navigation2 stack for autonomous robot navigation."
---

# Lesson 4: Nav2 Navigation Stack

## Prediction Phase

- What components does a robot need for autonomous navigation?
- How does a robot plan a path from A to B while avoiding obstacles?
- What is the difference between a global and local planner?

---

## Nav2 Architecture

Nav2 (Navigation 2) is the ROS 2 navigation framework. Core components:

```
Goal Pose → BT Navigator → Global Planner → Local Controller → cmd_vel
                ↑                ↑                 ↑
           Behavior Tree    Global Costmap    Local Costmap
                                ↑                 ↑
                            Map Server      Sensor Data (lidar, depth)
```

### Key Components

| Component | Role | Package |
|-----------|------|---------|
| **BT Navigator** | Orchestrates navigation via behavior tree | `nav2_bt_navigator` |
| **Global Planner** | Plans full path on map | `nav2_navfn_planner` |
| **Local Controller** | Follows path, avoids obstacles | `nav2_dwb_controller` |
| **Costmap** | Grid of navigation costs (obstacles, inflation) | `nav2_costmap_2d` |
| **Map Server** | Serves static map | `nav2_map_server` |
| **AMCL** | Particle filter localization | `nav2_amcl` |

## Installation

```bash
sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup
```

## Configuration

```yaml
# nav2_params.yaml
bt_navigator:
  ros__parameters:
    global_frame: map
    robot_base_frame: base_link
    odom_topic: /odom
    default_bt_xml_filename: "navigate_w_replanning_and_recovery.xml"

controller_server:
  ros__parameters:
    controller_frequency: 20.0
    FollowPath:
      plugin: "dwb_core::DWBLocalPlanner"
      min_vel_x: 0.0
      max_vel_x: 0.5
      max_vel_theta: 1.0
      min_speed_xy: 0.0
      max_speed_xy: 0.5
      acc_lim_x: 2.5
      acc_lim_theta: 3.2
      decel_lim_x: -2.5

planner_server:
  ros__parameters:
    GridBased:
      plugin: "nav2_navfn_planner/NavfnPlanner"
      tolerance: 0.5
      use_astar: false
      allow_unknown: true

global_costmap:
  global_costmap:
    ros__parameters:
      update_frequency: 1.0
      publish_frequency: 1.0
      global_frame: map
      robot_base_frame: base_link
      robot_radius: 0.3
      resolution: 0.05
      plugins: ["static_layer", "obstacle_layer", "inflation_layer"]
      static_layer:
        plugin: "nav2_costmap_2d::StaticLayer"
        map_subscribe_transient_local: true
      obstacle_layer:
        plugin: "nav2_costmap_2d::ObstacleLayer"
        observation_sources: scan
        scan:
          topic: /scan
          max_obstacle_height: 2.0
          clearing: true
          marking: true
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 3.0
        inflation_radius: 0.55

local_costmap:
  local_costmap:
    ros__parameters:
      update_frequency: 5.0
      publish_frequency: 2.0
      global_frame: odom
      robot_base_frame: base_link
      rolling_window: true
      width: 3
      height: 3
      resolution: 0.05
      plugins: ["obstacle_layer", "inflation_layer"]
```

## Launch File

```python
# launch/navigation.launch.py
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    nav2_params = os.path.join(
        get_package_share_directory('my_robot_nav'),
        'config', 'nav2_params.yaml'
    )
    map_file = os.path.join(
        get_package_share_directory('my_robot_nav'),
        'maps', 'building.yaml'
    )

    return LaunchDescription([
        Node(
            package='nav2_map_server',
            executable='map_server',
            parameters=[{'yaml_filename': map_file}],
        ),
        Node(
            package='nav2_amcl',
            executable='amcl',
            parameters=[nav2_params],
        ),
        Node(
            package='nav2_controller',
            executable='controller_server',
            parameters=[nav2_params],
        ),
        Node(
            package='nav2_planner',
            executable='planner_server',
            parameters=[nav2_params],
        ),
        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            parameters=[nav2_params],
        ),
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            parameters=[{
                'autostart': True,
                'node_names': [
                    'map_server', 'amcl', 'controller_server',
                    'planner_server', 'bt_navigator'
                ]
            }],
        ),
    ])
```

## Sending Navigation Goals

```bash
# From command line
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: 'map'}, pose: {position: {x: 2.0, y: 1.0}}}}"
```

```python
# Programmatically
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator

nav = BasicNavigator()
nav.waitUntilNav2Active()

goal = PoseStamped()
goal.header.frame_id = 'map'
goal.pose.position.x = 2.0
goal.pose.position.y = 1.0
goal.pose.orientation.w = 1.0

nav.goToPose(goal)
while not nav.isTaskComplete():
    feedback = nav.getFeedback()
```

---

## Execution Phase

1. Install Nav2: `sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup`
2. Create the nav2_params.yaml configuration
3. Launch Nav2 with your simulated robot
4. Send a navigation goal via CLI or Python
5. Observe the planned path and robot motion in RViz2

---

## Reflection

- How did the robot handle narrow passages?
- What happened when you changed the inflation radius?
- How does the costmap resolution affect planning accuracy vs. speed?
