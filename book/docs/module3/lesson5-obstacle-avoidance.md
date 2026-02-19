---
title: "Lesson 5: Obstacle Avoidance"
sidebar_position: 6
description: "Dynamic obstacle avoidance with Nav2 controller tuning and recovery behaviors."
---

# Lesson 5: Obstacle Avoidance & Nav2 Tuning

## Prediction Phase

- What should a robot do when its planned path is blocked?
- How does the local planner differ from the global planner in handling obstacles?
- When should a robot give up on a goal vs. try recovery behaviors?

---

## DWB Controller Tuning

The DWB (Dynamic Window Based) controller is Nav2's default local planner. It evaluates candidate velocity commands and scores them:

```yaml
controller_server:
  ros__parameters:
    FollowPath:
      plugin: "dwb_core::DWBLocalPlanner"
      # Velocity limits
      min_vel_x: 0.0
      max_vel_x: 0.3       # Reduce for humanoids (stability)
      max_vel_theta: 0.8    # Reduce for smooth turning
      # Acceleration limits
      acc_lim_x: 1.5
      acc_lim_theta: 2.0
      decel_lim_x: -1.5
      # Scoring (higher weight = more important)
      critics: ["RotateToGoal", "Oscillation", "BaseObstacle", "GoalAlign", "PathAlign", "PathDist", "GoalDist"]
      BaseObstacle.scale: 0.02    # Obstacle avoidance weight
      PathAlign.scale: 32.0       # Path following weight
      GoalAlign.scale: 24.0       # Goal orientation weight
      PathDist.scale: 32.0
      GoalDist.scale: 24.0
```

:::tip Humanoid-Specific Tuning
Humanoid robots have a higher center of gravity and smaller stability margin. Use lower velocity limits and acceleration to prevent falls during obstacle avoidance maneuvers.
:::

## Recovery Behaviors

When the robot gets stuck, Nav2 executes recovery behaviors defined in the behavior tree:

| Recovery | Behavior | When Used |
|----------|----------|-----------|
| **Spin** | Rotate in place | Stuck facing obstacle |
| **Backup** | Move backward | Stuck in narrow space |
| **Wait** | Pause and retry | Temporary obstacle (person) |
| **Clear Costmap** | Reset obstacle data | Stale sensor data |

```yaml
# Configure recovery behaviors
recoveries_server:
  ros__parameters:
    recovery_plugins: ["spin", "backup", "wait"]
    spin:
      plugin: "nav2_recoveries/Spin"
      max_rotational_vel: 0.5
    backup:
      plugin: "nav2_recoveries/BackUp"
      speed: -0.1
    wait:
      plugin: "nav2_recoveries/Wait"
      duration: 5.0
```

## Stuck Detection

Nav2 detects the robot is stuck when:
- No progress toward goal for a configurable timeout
- Oscillating back and forth (Oscillation critic detects this)
- Controller fails to produce valid commands

```yaml
bt_navigator:
  ros__parameters:
    # Goal progress tracking
    goal_checker_plugin: "general_goal_checker"
    general_goal_checker:
      plugin: "nav2_controller::SimpleGoalChecker"
      xy_goal_tolerance: 0.25
      yaw_goal_tolerance: 0.25
```

## Dynamic Obstacle Handling

For moving obstacles (people, other robots):

1. **Local costmap** updates in real-time from sensor data
2. **DWB controller** replans locally every cycle (20 Hz)
3. **Recovery behaviors** trigger if forward progress stalls

```yaml
# Increase local costmap update rate for dynamic environments
local_costmap:
  local_costmap:
    ros__parameters:
      update_frequency: 10.0  # Higher for dynamic obstacles
      observation_sources: scan depth
      scan:
        topic: /scan
        clearing: true
        marking: true
        obstacle_max_range: 3.0
```

---

## Execution Phase

1. Set up a Gazebo world with static and dynamic obstacles
2. Configure DWB controller parameters
3. Send a navigation goal that requires obstacle avoidance
4. Test recovery behaviors by placing the robot in a stuck position
5. Tune parameters until navigation is smooth and reliable

---

## Reflection

- How did lowering max velocity affect obstacle avoidance behavior?
- Which recovery behavior was triggered most often?
- What parameter changes improved navigation in narrow corridors?
