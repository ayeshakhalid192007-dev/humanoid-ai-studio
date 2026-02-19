---
title: "Lesson 6: RViz2 Navigation Visualization"
sidebar_position: 7
description: "Visualize costmaps, paths, and TF trees in RViz2 for navigation debugging."
---

# Lesson 6: RViz2 for Navigation Visualization

## Prediction Phase

- What information do you need to visualize to debug navigation failures?
- How do costmaps represent obstacles and free space?
- What does the TF tree tell you about the robot's coordinate frames?

---

## RViz2 Display Configuration

Launch RViz2 with navigation displays:

```bash
rviz2 -d nav2_default_view.rviz
```

### Essential Displays for Navigation

| Display Type | Topic | Purpose |
|-------------|-------|---------|
| **Map** | `/map` | Static map from map server |
| **Global Costmap** | `/global_costmap/costmap` | Navigation cost grid |
| **Local Costmap** | `/local_costmap/costmap` | Real-time obstacle costs |
| **Global Plan** | `/plan` | Planned path (green line) |
| **Local Plan** | `/local_plan` | Controller trajectory |
| **LaserScan** | `/scan` | Lidar data overlay |
| **TF** | `/tf` | Coordinate frame tree |
| **Robot Model** | `robot_description` | Robot visualization |

## Costmap Visualization

### Global Costmap
Shows the full map with inflation zones around obstacles:
- **Free space**: White/light areas (cost = 0)
- **Obstacles**: Black/dark areas (cost = 254)
- **Inflation zone**: Gradient from obstacle (cost 1-253)

### Local Costmap
Rolling window around the robot showing real-time sensor data:
- Updates at 5-10 Hz from lidar/depth sensors
- Shows dynamic obstacles not in the static map
- Critical for obstacle avoidance decisions

## TF Tree Inspection

The TF tree shows relationships between coordinate frames:

```bash
# View TF tree
ros2 run tf2_tools view_frames

# Check specific transform
ros2 run tf2_ros tf2_echo map base_link

# Monitor TF timing
ros2 run tf2_ros tf2_monitor
```

Expected navigation TF chain:
```
map → odom → base_link → [sensor frames]
```

:::warning TF Issues
Missing or stale TF transforms are the most common cause of navigation failures. If Nav2 reports "transform timeout", check:
1. Is the TF publisher running? (`ros2 topic echo /tf`)
2. Are timestamps consistent? (`ros2 run tf2_ros tf2_monitor`)
3. Is the frame chain complete? (`ros2 run tf2_tools view_frames`)
:::

## Debugging Navigation Failures

### Robot Won't Move
1. Check costmap: Is the goal in free space? (Not inside an obstacle)
2. Check TF: Is the map→odom→base_link chain complete?
3. Check AMCL: Is the robot correctly localized? (particle cloud in RViz)

### Robot Takes Wrong Path
1. Check global costmap: Are obstacle inflations correct?
2. Check planner tolerance: Is it too high (accepting bad goals)?
3. Visualize the global plan: Does it look reasonable?

### Robot Oscillates
1. Check DWB parameters: Oscillation critic weight too low
2. Check local costmap: Are there phantom obstacles?
3. Reduce velocity limits for smoother behavior

## Setting 2D Pose Estimate

When AMCL can't localize, set an initial pose in RViz2:
1. Click "2D Pose Estimate" button in toolbar
2. Click and drag on the map to set position and orientation
3. AMCL will converge from this initial estimate

## Setting Navigation Goal

Send a goal directly from RViz2:
1. Click "Nav2 Goal" button in toolbar
2. Click on the map for the target position
3. Drag to set the target orientation
4. Watch the robot navigate

---

## Execution Phase

1. Launch Nav2 with your robot in Gazebo
2. Open RViz2 and add all navigation displays listed above
3. Set an initial pose estimate and verify localization
4. Send navigation goals and observe costmaps, paths, and TF
5. Intentionally create problems (block path, remove TF publisher) and debug

---

## Reflection

- Which visualization was most helpful for understanding navigation behavior?
- How did the costmap inflation radius affect path planning?
- What TF issues did you encounter and how did you resolve them?
