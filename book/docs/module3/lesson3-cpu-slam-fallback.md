---
title: "Lesson 3: CPU SLAM Alternatives"
sidebar_position: 4
description: "ORB-SLAM3 and RTAB-Map for systems without NVIDIA GPUs."
---

# Lesson 3: CPU-Based SLAM Alternatives

:::info For Non-NVIDIA Systems
This lesson covers CPU-based SLAM solutions for students without NVIDIA GPUs. These approaches work on any modern computer.
:::

## Prediction Phase

- Can CPU-based SLAM achieve real-time performance?
- What trade-offs exist between ORB-SLAM3 and RTAB-Map?
- How do you choose between monocular, stereo, and RGB-D SLAM?

---

## ORB-SLAM3

ORB-SLAM3 is a feature-based SLAM system supporting monocular, stereo, and RGB-D cameras with optional IMU fusion.

### Installation

```bash
# Dependencies
sudo apt install libopencv-dev libeigen3-dev libpangolin-dev

# Build ORB-SLAM3
git clone https://github.com/UZ-SLAMLab/ORB_SLAM3.git
cd ORB_SLAM3
chmod +x build.sh
./build.sh
```

### ROS 2 Integration

```bash
# Install ROS 2 wrapper
cd ~/ros2_ws/src
git clone https://github.com/zang09/ORB_SLAM3_ROS2.git
cd ~/ros2_ws
colcon build --packages-select orb_slam3_ros2
```

### Configuration

```yaml
# orb_slam3_params.yaml
orb_slam3:
  ros__parameters:
    voc_file: "path/to/ORBvoc.txt"
    settings_file: "path/to/camera_settings.yaml"
    sensor_type: "rgbd"  # mono, stereo, rgbd
    visualization: true
```

## RTAB-Map

RTAB-Map (Real-Time Appearance-Based Mapping) provides a complete SLAM and 3D reconstruction solution with ROS 2 native support.

### Installation

```bash
# Install from apt (recommended)
sudo apt install ros-humble-rtabmap-ros

# Launch with default parameters
ros2 launch rtabmap_launch rtabmap.launch.py
```

### Configuration

```python
# launch/rtabmap_slam.launch.py
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='rtabmap_slam',
            executable='rtabmap',
            parameters=[{
                'subscribe_depth': True,
                'subscribe_rgb': True,
                'frame_id': 'base_link',
                'odom_frame_id': 'odom',
                'approx_sync': True,
                'queue_size': 10,
                # SLAM parameters
                'Mem/IncrementalMemory': 'true',
                'Mem/InitWMWithAllNodes': 'false',
                'RGBD/ProximityBySpace': 'true',
                'Reg/Strategy': '0',  # Visual registration
            }],
            remappings=[
                ('rgb/image', '/camera/color/image_raw'),
                ('depth/image', '/camera/depth/image_raw'),
                ('rgb/camera_info', '/camera/color/camera_info'),
            ],
        ),
    ])
```

## Comparison

| Feature | ORB-SLAM3 | RTAB-Map |
|---------|-----------|----------|
| ROS 2 Support | Community wrapper | Native |
| Dense Mapping | No (sparse only) | Yes (3D reconstruction) |
| Loop Closure | Yes (DBoW2) | Yes (appearance-based) |
| Sensors | Mono/Stereo/RGBD+IMU | Stereo/RGBD/Lidar |
| CPU Usage | 50-80% single core | 60-100% multi-core |
| Best For | Low-resource systems | Full 3D mapping |

:::tip Recommendation
For this course, use **RTAB-Map** for its easier ROS 2 integration and dense mapping capability. Use **ORB-SLAM3** if you need minimal resource usage.
:::

---

## Execution Phase

1. Install either ORB-SLAM3 or RTAB-Map (RTAB-Map recommended)
2. Configure for your camera type (RGB-D preferred)
3. Launch SLAM with simulated camera data from Gazebo
4. Move the robot around and observe the map building
5. Test loop closure by revisiting a location

---

## Reflection

- How did CPU SLAM performance compare to the Gazebo real-time factor?
- Was loop closure detected when revisiting locations?
- What environment features helped vs. hurt SLAM accuracy?
