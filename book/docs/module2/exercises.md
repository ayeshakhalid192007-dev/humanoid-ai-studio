---
title: "Module 2 Exercises"
sidebar_position: 7
description: "Hands-on simulation exercises using the Predict-Execute-Reflect methodology."
---

# Module 2 Exercises

---

## Exercise 1: Spawn and Interact with Humanoid in Gazebo

### Predict
1. What will happen when you spawn the humanoid at z=0 vs z=0.5?
2. How will the robot behave with no joint controllers active?
3. What physics parameters will most affect the robot's stability?

### Execute
1. Create a Gazebo world with a ground plane and obstacles
2. Write a launch file that spawns your Module 1 URDF
3. Experiment with different spawn positions and orientations
4. Observe the robot settling under gravity

**Expected outcome**: Robot spawns, settles on ground, remains stable.

### Reflect
- Did the robot settle as expected?
- What happened without any joint controllers?
- How did spawn position affect the initial behavior?

---

## Exercise 2: Physics Parameter Tuning

### Predict
1. How will halving the step size affect simulation speed?
2. What happens if you set friction to zero on the feet?
3. How does the solver iteration count affect joint stability?

### Execute
1. Create three world files with different physics settings:
   - **Fast**: step=0.005, iters=20
   - **Balanced**: step=0.001, iters=50
   - **Accurate**: step=0.0005, iters=100
2. Spawn the same robot in each and compare:
   - Real-time factor (bottom of Gazebo window)
   - Joint stability (any jittering?)
   - Contact behavior (feet on ground)
3. Record results in a table

### Reflect
- What was the relationship between step size and real-time factor?
- At what point did increasing iterations stop improving stability?
- Which settings would you use for development vs. final testing?

---

## Exercise 3: Sensor Integration

### Predict
1. What frame rate can you achieve with a 640x480 camera?
2. How will IMU noise affect downstream processing?
3. What happens if lidar max range is less than room size?

### Execute
1. Add an RGB camera to the robot's head link
2. Add an IMU to the torso
3. Add a lidar to the chest
4. Launch in Gazebo and verify each sensor topic exists
5. Visualize camera in `rqt_image_view`, lidar in RViz2
6. Measure actual update rates with `ros2 topic hz`

**Expected outcome**: All three sensors publishing data at configured rates.

### Reflect
- Did actual sensor rates match configured rates?
- How did adding sensors affect the real-time factor?
- What noise model settings produced realistic-looking data?

---

## Exercise 4: Debug a Broken Simulation

### Predict
1. What are three symptoms of incorrect inertia values?
2. How can you tell if a collision geometry is missing?
3. What tools help identify QoS mismatches in sensor topics?

### Execute

Create a URDF with these intentional bugs, then fix each one:

1. **Bug**: One link has mass=0 and zero inertia → observe behavior → fix
2. **Bug**: Foot link has no collision geometry → observe → fix
3. **Bug**: Joint limits allow 360° on a shoulder joint → observe → fix
4. **Bug**: Camera sensor publishes at 100 Hz causing slowdown → observe → fix

Follow the debugging checklist from Lesson 5 for each bug.

### Reflect
- Which bugs were hardest to diagnose?
- How did the debugging checklist help structure your approach?
- What would you add to the checklist based on your experience?

---

## Module 2 Review

### Key Concepts

| Concept | Summary |
|---------|---------|
| Gazebo | 3D simulator with physics, rendering, and ROS 2 integration |
| Physics engine | ODE/Bullet computes forces and collisions each timestep |
| Inertia tensor | Describes mass distribution; critical for simulation stability |
| Sensor plugins | Gazebo plugins that simulate cameras, lidar, IMU |
| Isaac Sim | GPU-accelerated simulator for ML training (optional) |

### Self-Assessment

- [ ] I can spawn a URDF robot in Gazebo via a ROS 2 launch file
- [ ] I can tune physics parameters for stability and performance
- [ ] I can add and configure simulated sensors
- [ ] I can systematically debug simulation issues
- [ ] I understand the trade-offs between different simulation platforms
