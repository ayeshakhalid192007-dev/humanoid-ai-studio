---
title: "Module 1 Exercises"
sidebar_position: 7
description: "Hands-on exercises for ROS 2 fundamentals using the Predict-Execute-Reflect methodology."
---

# Module 1 Exercises

These exercises follow the **Predict → Execute → Reflect** methodology. For each exercise, write down your predictions before running any code.

---

## Exercise 1: Custom Sensor Publisher/Subscriber

**Objective**: Build a multi-sensor data pipeline using topics with appropriate QoS settings.

### Predict

1. If an IMU publishes at 100 Hz but your subscriber callback takes 15ms, what happens?
2. Which QoS profile would you use for IMU data vs. emergency stop commands?
3. What happens if you start the subscriber before the publisher?

### Execute

1. Create a package called `sensor_pipeline`
2. Write a publisher that simulates IMU data (linear acceleration, angular velocity) at 50 Hz
3. Write a subscriber that processes IMU data and publishes a derived "stability score" on a new topic
4. Use `BEST_EFFORT` QoS for the IMU topic
5. Add a third node that subscribes to the stability score using `RELIABLE` QoS

```bash
# Create the package
ros2 pkg create --build-type ament_python sensor_pipeline
```

**Expected outcome**: Three connected nodes visible in `rqt_graph`, IMU data flowing at ~50 Hz (verify with `ros2 topic hz`).

### Reflect

- Did the subscriber keep up with the publish rate?
- What happened with the QoS mismatch experiment?
- How would you handle the case where the IMU publisher crashes?

---

## Exercise 2: Multi-Joint URDF Robot

**Objective**: Build a URDF model with multiple joint types and verify it in RViz.

### Predict

1. What happens if a revolute joint has no position limits defined?
2. How does the inertia tensor affect simulation behavior?
3. What's the difference between visual and collision geometries?

### Execute

1. Create a URDF file for a 3-DOF robot arm with:
   - A fixed base link
   - Revolute joint for base rotation (yaw)
   - Revolute joint for shoulder (pitch)
   - Prismatic joint for extension
2. Add visual geometries (cylinders for links)
3. Add collision geometries (simplified boxes)
4. Set joint limits (position, velocity, effort)
5. Launch in RViz with `joint_state_publisher_gui`

```bash
# Visualize URDF
ros2 launch urdf_tutorial display.launch.py model:=path/to/your_robot.urdf
```

**Expected outcome**: Robot visible in RViz with interactive joint sliders.

### Reflect

- What happened when you moved joints beyond their limits in the GUI?
- How did changing the inertia values affect anything at this stage?
- What would break if collision geometry was much larger than visual geometry?

---

## Exercise 3: Robot Joint Control Service

**Objective**: Create a service interface for commanding robot joint positions.

### Predict

1. Why use a service instead of a topic for joint commands?
2. What should happen if a requested joint position exceeds limits?
3. How would you handle multiple simultaneous service calls?

### Execute

1. Define a custom service: `SetJointAngle.srv`
   ```
   string joint_name
   float64 angle_degrees
   ---
   bool success
   string message
   float64 final_angle
   ```
2. Create a server node that validates joint limits before accepting commands
3. Create a client node that sends a sequence of joint commands
4. Test error handling: request an angle beyond joint limits

**Expected outcome**: Server rejects out-of-range commands with clear error message, accepts valid commands.

### Reflect

- How does the service pattern ensure the client knows if the command succeeded?
- What would you change for a real robot that takes time to move?
- When would an Action be more appropriate than a Service here?

---

## Exercise 4: Debug a Broken ROS 2 System

**Objective**: Use debugging tools to diagnose and fix issues in a provided system.

### Predict

1. List three common reasons a subscriber might not receive messages
2. What tool would you use first when debugging a silent node?
3. How do you check if a QoS mismatch is the problem?

### Execute

Create a system with intentional bugs. Start all nodes, then use debugging tools to find and fix each issue:

**Bug 1**: Publisher uses topic `/sensor/temp`, subscriber listens on `/sensors/temp`
- Use `ros2 topic list` and `rqt_graph` to identify

**Bug 2**: Publisher uses `BEST_EFFORT`, subscriber requires `RELIABLE`
- Use `ros2 topic info --verbose` to compare QoS

**Bug 3**: Service server crashes on specific input but no error is printed
- Use `rqt_console` to find hidden error messages

**Bug 4**: Node starts but doesn't appear in `ros2 node list`
- Check if `rclpy.init()` was called

**Debugging procedure for each bug**:
1. Run `ros2 node list` — is the node running?
2. Run `ros2 topic list -t` — does the topic exist?
3. Run `ros2 topic info /topic_name` — are publisher/subscriber counts correct?
4. Run `ros2 topic echo /topic_name` — is data flowing?
5. Run `rqt_graph` — is the graph connected as expected?

### Reflect

- Which debugging tool was most useful for each bug type?
- How would you build monitoring into a production robot system?
- What logging practices would help prevent these issues?

---

## Module 1 Review

### Key Concepts

| Concept | Summary |
|---------|---------|
| Nodes | Single-purpose processes in the ROS 2 graph |
| Topics | Named pub/sub channels for streaming data |
| Services | Request/response for synchronous operations |
| QoS | Reliability/durability policies for message delivery |
| URDF | XML format for robot model description |
| rqt_graph | Visual tool for inspecting node/topic connections |

### Self-Assessment

- [ ] I can create publisher and subscriber nodes with custom QoS
- [ ] I can define URDF models with multiple joint types
- [ ] I can create service servers and clients
- [ ] I can use CLI and rqt tools to debug a ROS 2 system
- [ ] I understand when to use topics vs services vs actions
