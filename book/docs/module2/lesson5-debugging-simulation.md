---
title: "Lesson 5: Debugging Simulation"
sidebar_position: 6
description: "Troubleshoot common simulation problems: physics instability, collisions, and performance."
---

# Lesson 5: Debugging Simulation Issues

## Prediction Phase

- What causes a robot model to "explode" in simulation?
- How do you know if a simulation is running faster or slower than real time?
- What should you check first when your robot falls through the ground?

---

## Common Simulation Problems

### 1. Joint Explosions

**Symptoms**: Robot parts fly apart violently at simulation start.

**Causes**:
- Unrealistic inertia values (too small or zero)
- Overlapping collision geometries at spawn
- Step size too large for joint constraints

**Solutions**:
```xml
<!-- Ensure every link has realistic inertia -->
<inertial>
  <mass value="2.0"/>
  <!-- Calculate from geometry, don't use placeholder values -->
  <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.005"/>
</inertial>
```

```xml
<!-- Reduce physics step size -->
<physics type="ode">
  <max_step_size>0.0005</max_step_size>
  <ode>
    <solver>
      <iters>100</iters>
    </solver>
  </ode>
</physics>
```

### 2. Robot Falls Through Ground

**Symptoms**: Robot passes through the ground plane.

**Causes**:
- Missing collision geometry on foot links
- Collision geometry doesn't match visual geometry bounds
- Physics step size too large

**Solutions**:
- Add collision geometry to **every** link that should interact physically
- Verify collision bounds with `View > Collisions` in Gazebo
- Spawn robot above ground (z > 0) and let it settle

### 3. Unstable Standing / Jittering

**Symptoms**: Robot vibrates or oscillates when standing still.

**Causes**:
- Contact point solver not converging
- Insufficient friction
- Joint damping too low

**Solutions**:
```xml
<!-- Increase solver iterations -->
<ode>
  <solver>
    <iters>100</iters>
    <sor>1.3</sor>
  </solver>
  <constraints>
    <cfm>0.00001</cfm>
    <erp>0.2</erp>
  </constraints>
</ode>

<!-- Add joint damping -->
<dynamics>
  <damping>1.0</damping>
  <friction>0.5</friction>
</dynamics>

<!-- Increase foot friction -->
<surface>
  <friction>
    <ode>
      <mu>1.0</mu>
      <mu2>1.0</mu2>
    </ode>
  </friction>
</surface>
```

### 4. Slow Simulation Performance

**Symptoms**: Real-time factor drops below 0.5.

**Causes**:
- Too many collision checks (complex meshes)
- High sensor update rates
- Step size too small for the scene complexity

**Solutions**:
- Use simple collision geometries (boxes, cylinders) instead of mesh collisions
- Reduce sensor update rates (30 Hz camera → 10 Hz for testing)
- Increase `max_step_size` if accuracy permits
- Disable unused Gazebo GUI plugins

## Debugging Checklist

Use this systematic checklist when simulation doesn't behave as expected:

```
□ 1. Check URDF validity
    $ check_urdf robot.urdf
    $ urdf_to_graphviz robot.urdf

□ 2. Verify all links have inertial properties
    - Mass > 0
    - Inertia tensor positive definite

□ 3. Check collision geometries
    - Every physical link has collision tag
    - Gazebo > View > Collisions (visual check)

□ 4. Verify joint limits
    - Position limits set for revolute joints
    - Effort and velocity limits realistic

□ 5. Check physics parameters
    - Step size <= 0.001
    - Solver iterations >= 50

□ 6. Verify spawn configuration
    - Spawn height above ground
    - No initial collision overlaps

□ 7. Check real-time factor
    - Gazebo bottom bar shows RTF
    - RTF > 0.8 for useful simulation
```

## Gazebo Debugging Tools

```bash
# Check URDF syntax
check_urdf path/to/robot.urdf

# Visualize URDF tree
urdf_to_graphviz path/to/robot.urdf

# Gazebo verbose mode (more log output)
gazebo --verbose world.sdf

# Monitor Gazebo performance
gz stats
```

:::tip Iterative Debugging
Start with the simplest possible model (single box on ground plane) and add complexity incrementally. If something breaks, you know exactly which addition caused the problem.
:::

---

## Execution Phase

1. Take your humanoid URDF and intentionally introduce each bug above
2. Practice diagnosing each issue using the debugging checklist
3. Fix each issue and verify the robot is stable
4. Measure the real-time factor and optimize if below 0.8

---

## Reflection

- Which debugging technique was most useful for each problem type?
- How do you balance simulation accuracy with performance?
- What would you check first on a robot that "explodes" at spawn?
