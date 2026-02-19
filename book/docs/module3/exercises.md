---
title: "Module 3 Exercises"
sidebar_position: 8
description: "Hands-on perception and navigation exercises using the Predict-Execute-Reflect methodology."
---

# Module 3 Exercises

---

## Exercise 1: Build a Map with VSLAM

### Predict
1. How many feature points do you expect from a typical indoor room?
2. What happens if the robot moves too fast for the camera frame rate?
3. Will loop closure be detected in a square room with distinct features?

### Execute
1. Launch your robot in a Gazebo world with multiple rooms
2. Start RTAB-Map (or your chosen SLAM system)
3. Teleoperate the robot through the entire environment
4. Complete a loop back to the starting position
5. Save the generated map

**Expected outcome**: Complete map with loop closure correction visible.

### Reflect
- Did loop closure improve the map quality?
- What areas had poor feature detection?
- How would you improve mapping in featureless corridors?

---

## Exercise 2: Configure Nav2 for Basic Navigation

### Predict
1. What inflation radius will allow passage through a 1-meter doorway?
2. How will costmap resolution affect path planning?
3. What happens if the global planner can't find a path?

### Execute
1. Configure nav2_params.yaml with appropriate parameters
2. Load the map from Exercise 1
3. Launch Nav2 with your robot
4. Set initial pose in RViz2
5. Send a navigation goal to a specific room
6. Record the path taken and any recovery behaviors

### Reflect
- Did the robot navigate successfully on the first attempt?
- What parameter changes improved navigation?
- How did the inflation radius affect path choice near walls?

---

## Exercise 3: Navigate Around Obstacles

### Predict
1. How will the robot react to a suddenly appearing obstacle?
2. Which recovery behavior will trigger in a dead-end?
3. How fast should the local costmap update for reliable avoidance?

### Execute
1. Add dynamic obstacles to the Gazebo world (moving boxes)
2. Send the robot on a navigation path that encounters obstacles
3. Observe local costmap updates and path replanning
4. Place the robot in a dead-end and observe recovery behaviors
5. Tune DWB controller for smooth obstacle avoidance

### Reflect
- How quickly did the local costmap detect new obstacles?
- Were recovery behaviors appropriate for each stuck situation?
- What velocity limits provided the best balance of speed and safety?

---

## Exercise 4: Tune Navigation Parameters

### Predict
1. What is the minimum time a robot needs to navigate 10 meters in a clear hallway?
2. How does the goal tolerance affect final positioning accuracy?
3. What happens with too many solver iterations in DWB?

### Execute
Create three parameter configurations and compare:
- **Conservative**: Low velocity, wide inflation, many recovery behaviors
- **Balanced**: Medium settings
- **Aggressive**: High velocity, minimal inflation, fewer recoveries

For each, measure:
- Time to navigate a fixed route
- Number of recovery behaviors triggered
- Final position accuracy
- Any collisions or failures

### Reflect
- Which configuration was most reliable?
- What is the practical trade-off between speed and safety?
- What parameters would you change for a production deployment?

---

## Module 3 Review

### Key Concepts

| Concept | Summary |
|---------|---------|
| VSLAM | Localization and mapping using camera features |
| Loop Closure | Drift correction when revisiting locations |
| Nav2 | ROS 2 navigation framework (planners + controllers + costmaps) |
| Costmap | Grid representing navigation costs around obstacles |
| DWB Controller | Local planner using dynamic window approach |
| Recovery Behaviors | Automatic actions when robot gets stuck |

### Self-Assessment

- [ ] I can set up VSLAM and build a map of an environment
- [ ] I can configure Nav2 parameters for my robot
- [ ] I can send navigation goals and monitor progress
- [ ] I can tune obstacle avoidance for different environments
- [ ] I can debug navigation failures using RViz2 and TF tools
