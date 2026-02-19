---
title: "Lesson 2: Physics Simulation"
sidebar_position: 3
description: "Understand gravity, collisions, friction, and joint dynamics for realistic humanoid simulation."
---

# Lesson 2: Physics Engines & Simulation Dynamics

## Prediction Phase

- What happens to a simulated humanoid if friction is set to zero?
- How does simulation step size affect accuracy vs. performance?
- Why do robots sometimes "explode" in physics simulations?

---

## Physics Fundamentals

Gazebo uses physics engines to compute forces, collisions, and motion at each timestep.

### Key Physical Properties

**Gravity**: Default Earth gravity (0, 0, -9.81 m/s²)

**Mass and Inertia**: Every link needs proper mass and inertia tensor:
```xml
<inertial>
  <mass value="5.0"/>
  <inertia
    ixx="0.1" ixy="0" ixz="0"
    iyy="0.1" iyz="0"
    izz="0.05"/>
</inertial>
```

:::warning Inertia Values
Incorrect inertia tensors are the #1 cause of simulation instability. Use realistic values based on the link's geometry and mass distribution. A solid cylinder of mass m, radius r, length h has:
- ixx = iyy = m(3r² + h²)/12
- izz = mr²/2
:::

### Collision Detection

Gazebo checks for intersecting collision geometries each timestep:

```xml
<collision name="torso_collision">
  <geometry>
    <box>
      <size>0.3 0.2 0.5</size>
    </box>
  </geometry>
  <surface>
    <friction>
      <ode>
        <mu>0.8</mu>
        <mu2>0.8</mu2>
      </ode>
    </friction>
    <bounce>
      <restitution_coefficient>0.1</restitution_coefficient>
    </bounce>
  </surface>
</collision>
```

### Friction Models

| Parameter | Description | Typical Values |
|-----------|-------------|----------------|
| `mu` | Primary friction coefficient | 0.5-1.0 (rubber on concrete) |
| `mu2` | Secondary friction direction | Usually same as mu |
| `slip1/slip2` | Slip compliance | 0 (no slip) to 1 (ice) |

## Physics Engine Parameters

```xml
<physics type="ode">
  <max_step_size>0.001</max_step_size>
  <real_time_factor>1.0</real_time_factor>
  <real_time_update_rate>1000</real_time_update_rate>
  <ode>
    <solver>
      <type>quick</type>
      <iters>50</iters>
      <sor>1.3</sor>
    </solver>
    <constraints>
      <cfm>0.0</cfm>
      <erp>0.2</erp>
    </constraints>
  </ode>
</physics>
```

| Parameter | Effect | Trade-off |
|-----------|--------|-----------|
| `max_step_size` | Time per physics step | Smaller = more accurate, slower |
| `iters` | Solver iterations per step | More = more accurate, slower |
| `real_time_factor` | Target speed vs. real time | 1.0 = real time |
| `cfm` | Constraint force mixing | Higher = softer constraints |
| `erp` | Error reduction parameter | Higher = faster error correction |

## Joint Dynamics

Joint dynamics control how joints respond to forces:

```xml
<joint name="shoulder_pitch" type="revolute">
  <dynamics>
    <damping>0.5</damping>
    <friction>0.1</friction>
    <spring_reference>0</spring_reference>
    <spring_stiffness>0</spring_stiffness>
  </dynamics>
  <limit>
    <lower>-1.57</lower>
    <upper>1.57</upper>
    <effort>100</effort>
    <velocity>2.0</velocity>
  </limit>
</joint>
```

## ODE vs Bullet Physics

| Feature | ODE | Bullet |
|---------|-----|--------|
| Speed | Faster for simple scenes | Better for complex collisions |
| Accuracy | Good for articulated bodies | Better for soft bodies |
| Stability | May need parameter tuning | Generally more stable |
| Default | Yes (Gazebo default) | Available as alternative |

## Common Issues and Solutions

**Joint explosions**: Robot parts fly apart
- Cause: Unrealistic inertia values, step size too large
- Fix: Calculate proper inertia, reduce `max_step_size` to 0.001 or smaller

**Jittering at rest**: Robot vibrates on ground
- Cause: Solver not converging
- Fix: Increase `iters` to 100+, adjust `cfm` and `erp`

**Interpenetration**: Objects pass through each other
- Cause: Step size too large for object velocities
- Fix: Reduce `max_step_size`, simplify collision meshes

---

## Execution Phase

1. Experiment with different physics step sizes (0.01, 0.001, 0.0001)
2. Change friction coefficients and observe the robot sliding
3. Modify inertia values and observe stability changes
4. Try switching to Bullet physics engine
5. Record the real-time factor under different settings

---

## Reflection

- How did reducing the step size affect simulation speed vs. accuracy?
- What friction values made the robot walk stably?
- Why is the inertia tensor important for simulation stability?
