---
title: "Lesson 2: Isaac ROS VSLAM (GPU Path)"
sidebar_position: 3
description: "GPU-accelerated VSLAM with NVIDIA Isaac ROS for real-time robot localization."
---

# Lesson 2: NVIDIA Isaac ROS VSLAM

:::info Preferred Path for NVIDIA GPU Owners
This lesson covers the GPU-accelerated VSLAM path using NVIDIA Isaac ROS. If you don't have an NVIDIA GPU, proceed to Lesson 3 for CPU-based alternatives.
:::

## Prediction Phase

- How much faster can GPU-accelerated VSLAM run compared to CPU?
- What NVIDIA hardware is needed for Isaac ROS?
- How does Isaac ROS VSLAM integrate with the Nav2 stack?

---

## Prerequisites

```bash
# Check NVIDIA GPU availability
nvidia-smi

# Required: NVIDIA GPU with compute capability 7.0+
# (Jetson Xavier/Orin, RTX 2060+, Tesla T4+)
# CUDA 11.8+ and cuDNN 8.6+
```

## Isaac ROS Overview

NVIDIA Isaac ROS provides GPU-accelerated ROS 2 packages:
- **isaac_ros_visual_slam**: GPU-accelerated visual odometry and SLAM
- **isaac_ros_apriltag**: GPU-accelerated fiducial detection
- **isaac_ros_image_pipeline**: GPU image processing
- **isaac_ros_dnn_inference**: Deep learning inference on ROS topics

## Installation

```bash
# Install Isaac ROS common
sudo apt install ros-humble-isaac-ros-common

# Install Isaac ROS Visual SLAM
sudo apt install ros-humble-isaac-ros-visual-slam

# Or build from source (Docker recommended)
cd ~/workspaces/isaac_ros-dev
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_visual_slam.git
colcon build --packages-select isaac_ros_visual_slam
```

## Configuration

```yaml
# isaac_ros_vslam_params.yaml
isaac_ros_visual_slam:
  ros__parameters:
    # Input configuration
    image_height: 480
    image_width: 640

    # SLAM parameters
    enable_slam_visualization: true
    enable_observations_view: true
    enable_landmarks_view: true

    # Performance
    num_cameras: 1  # stereo: 2
    enable_imu_fusion: true
    gyro_noise_density: 0.000244
    accel_noise_density: 0.001862

    # Map
    map_frame: "map"
    odom_frame: "odom"
    base_frame: "base_link"
```

## Launch

```python
# launch/isaac_vslam.launch.py
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='isaac_ros_visual_slam',
            executable='visual_slam_node',
            name='visual_slam',
            parameters=['config/isaac_ros_vslam_params.yaml'],
            remappings=[
                ('image', '/camera/image_raw'),
                ('camera_info', '/camera/camera_info'),
            ],
        ),
    ])
```

```bash
ros2 launch my_robot isaac_vslam.launch.py
```

## Output Topics

| Topic | Type | Description |
|-------|------|-------------|
| `/visual_slam/tracking/odometry` | `nav_msgs/Odometry` | Robot pose estimate |
| `/visual_slam/vis/observations_cloud` | `PointCloud2` | Tracked features |
| `/visual_slam/vis/landmarks_cloud` | `PointCloud2` | 3D map points |
| `/tf` | `TFMessage` | map→odom→base_link transforms |

## Performance Comparison

| Metric | Isaac ROS (GPU) | ORB-SLAM3 (CPU) |
|--------|----------------|-----------------|
| Latency | ~10ms | ~30-50ms |
| CPU Usage | ~15% | ~80-100% |
| GPU Usage | ~20% | 0% |
| Accuracy | Sub-centimeter | Centimeter |

---

## Execution Phase

1. Verify NVIDIA GPU with `nvidia-smi`
2. Install Isaac ROS Visual SLAM
3. Configure parameters for your camera
4. Launch with simulated or real camera data
5. Visualize the map in RViz2

---

## Reflection

- How did GPU acceleration affect tracking latency?
- What happens when the camera faces a textureless surface?
- How would you integrate this with Nav2 for autonomous navigation?
