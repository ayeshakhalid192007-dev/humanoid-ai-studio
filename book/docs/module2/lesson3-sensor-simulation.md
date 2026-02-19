---
title: "Lesson 3: Sensor Simulation"
sidebar_position: 4
description: "Simulate cameras, lidar, IMU, and depth sensors in Gazebo with ROS 2 integration."
---

# Lesson 3: Simulating Sensors

## Prediction Phase

- How accurate are simulated sensors compared to real hardware?
- What ROS 2 message types do cameras and lidar use?
- Why would you add noise to simulated sensor data?

---

## Sensor Types in Gazebo

Gazebo simulates common robot sensors through plugins that publish to ROS 2 topics.

### RGB Camera

```xml
<!-- Add to your URDF inside a link -->
<gazebo reference="camera_link">
  <sensor type="camera" name="head_camera">
    <update_rate>30.0</update_rate>
    <camera name="head_camera">
      <horizontal_fov>1.3962634</horizontal_fov>
      <image>
        <width>640</width>
        <height>480</height>
        <format>R8G8B8</format>
      </image>
      <clip>
        <near>0.02</near>
        <far>300</far>
      </clip>
    </camera>
    <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
      <ros>
        <remapping>image_raw:=/camera/image_raw</remapping>
        <remapping>camera_info:=/camera/camera_info</remapping>
      </ros>
      <frame_name>camera_link</frame_name>
    </plugin>
  </sensor>
</gazebo>
```

### Depth Camera

```xml
<gazebo reference="depth_camera_link">
  <sensor type="depth" name="depth_camera">
    <update_rate>15.0</update_rate>
    <camera>
      <horizontal_fov>1.047</horizontal_fov>
      <image>
        <width>640</width>
        <height>480</height>
      </image>
      <clip>
        <near>0.1</near>
        <far>10.0</far>
      </clip>
    </camera>
    <plugin name="depth_camera_controller" filename="libgazebo_ros_camera.so">
      <ros>
        <remapping>depth/image_raw:=/depth_camera/depth/image_raw</remapping>
        <remapping>depth/camera_info:=/depth_camera/depth/camera_info</remapping>
        <remapping>points:=/depth_camera/points</remapping>
      </ros>
      <frame_name>depth_camera_link</frame_name>
    </plugin>
  </sensor>
</gazebo>
```

### Lidar

```xml
<gazebo reference="lidar_link">
  <sensor type="ray" name="lidar">
    <update_rate>10.0</update_rate>
    <ray>
      <scan>
        <horizontal>
          <samples>360</samples>
          <min_angle>-3.14159</min_angle>
          <max_angle>3.14159</max_angle>
        </horizontal>
      </scan>
      <range>
        <min>0.1</min>
        <max>30.0</max>
        <resolution>0.01</resolution>
      </range>
    </ray>
    <plugin name="lidar_controller" filename="libgazebo_ros_ray_sensor.so">
      <ros>
        <remapping>~/out:=/scan</remapping>
      </ros>
      <output_type>sensor_msgs/LaserScan</output_type>
      <frame_name>lidar_link</frame_name>
    </plugin>
  </sensor>
</gazebo>
```

### IMU

```xml
<gazebo reference="imu_link">
  <sensor type="imu" name="imu_sensor">
    <update_rate>100.0</update_rate>
    <plugin name="imu_plugin" filename="libgazebo_ros_imu_sensor.so">
      <ros>
        <remapping>~/out:=/imu/data</remapping>
      </ros>
      <frame_name>imu_link</frame_name>
      <initial_orientation_as_reference>false</initial_orientation_as_reference>
    </plugin>
    <imu>
      <angular_velocity>
        <x><noise type="gaussian"><mean>0</mean><stddev>0.001</stddev></noise></x>
        <y><noise type="gaussian"><mean>0</mean><stddev>0.001</stddev></noise></y>
        <z><noise type="gaussian"><mean>0</mean><stddev>0.001</stddev></noise></z>
      </angular_velocity>
      <linear_acceleration>
        <x><noise type="gaussian"><mean>0</mean><stddev>0.01</stddev></noise></x>
        <y><noise type="gaussian"><mean>0</mean><stddev>0.01</stddev></noise></y>
        <z><noise type="gaussian"><mean>0</mean><stddev>0.01</stddev></noise></z>
      </linear_acceleration>
    </imu>
  </sensor>
</gazebo>
```

## Sensor Noise Models

Real sensors have noise. Adding noise to simulation improves transfer to real hardware:

| Sensor | Noise Type | Typical Values |
|--------|-----------|----------------|
| Camera | Gaussian pixel noise | stddev: 0.007 |
| Lidar | Range Gaussian noise | stddev: 0.01m |
| IMU gyro | Gaussian + bias | stddev: 0.001 rad/s |
| IMU accel | Gaussian + bias | stddev: 0.01 m/s² |

## Viewing Sensor Data

```bash
# View camera image
ros2 run rqt_image_view rqt_image_view

# Echo IMU data
ros2 topic echo /imu/data

# Visualize lidar in RViz2
rviz2  # Add LaserScan display, topic: /scan

# Check sensor update rates
ros2 topic hz /camera/image_raw
ros2 topic hz /scan
ros2 topic hz /imu/data
```

:::tip RViz2 Visualization
RViz2 is the primary tool for visualizing sensor data. Add display types matching your sensor topics: Image, LaserScan, PointCloud2, Imu, TF.
:::

---

## Execution Phase

1. Add a camera and IMU to your humanoid URDF from Module 1
2. Spawn in Gazebo and verify topics with `ros2 topic list`
3. View camera output with `rqt_image_view`
4. Visualize lidar data in RViz2
5. Compare IMU data with and without noise models

---

## Reflection

- How does the sensor update rate affect downstream processing?
- Why is noise modeling important for sim-to-real transfer?
- What is the performance cost of adding multiple high-resolution cameras?
