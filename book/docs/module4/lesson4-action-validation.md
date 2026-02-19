---
title: "Lesson 4: Action Validation & Safety"
sidebar_position: 5
description: "Multi-layer safety validation for robot commands from LLM outputs."
---

# Lesson 4: Multi-Layer Action Validation

## Prediction Phase

- What could go wrong if you execute LLM outputs without validation?
- How many layers of safety checking are needed for a physical robot?
- What should happen when a command fails validation?

---

## The Safety Problem

LLMs can generate plausible but dangerous commands:
- "Move at maximum speed" (may cause falls)
- "Pick up the knife" (safety concern)
- Hallucinated coordinates outside the workspace

:::caution Never Trust Raw LLM Output
Every command from an LLM must be validated before execution. LLMs don't understand physical constraints, workspace limits, or safety requirements.
:::

## Three-Layer Validation

### Layer 1: LLM Prompt Constraints

Build safety into the system prompt:

```python
SAFETY_PROMPT = """
SAFETY RULES (never override):
1. Maximum velocity: 0.5 m/s linear, 1.0 rad/s angular
2. Stay within workspace: x=[0,5], y=[0,5] meters
3. Never interact with: knives, electrical outlets, stairs
4. If any doubt about safety, refuse and explain
5. Always confirm destructive actions before execution
"""
```

### Layer 2: Parameter Bounds Checking

Validate every parameter against physical constraints:

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class SafetyLimits:
    max_linear_vel: float = 0.5     # m/s
    max_angular_vel: float = 1.0    # rad/s
    workspace_x: tuple = (0.0, 5.0) # meters
    workspace_y: tuple = (0.0, 5.0)
    max_reach: float = 0.8          # arm reach in meters
    forbidden_objects: list = None

    def __post_init__(self):
        if self.forbidden_objects is None:
            self.forbidden_objects = ["knife", "scissors", "glass"]

LIMITS = SafetyLimits()

def validate_navigate(params: dict) -> tuple[bool, str]:
    """Validate navigation command parameters."""
    x, y = params.get("x", 0), params.get("y", 0)

    if not (LIMITS.workspace_x[0] <= x <= LIMITS.workspace_x[1]):
        return False, f"X={x} outside workspace {LIMITS.workspace_x}"

    if not (LIMITS.workspace_y[0] <= y <= LIMITS.workspace_y[1]):
        return False, f"Y={y} outside workspace {LIMITS.workspace_y}"

    speed = params.get("speed", "normal")
    if speed == "fast" and LIMITS.max_linear_vel < 0.5:
        return False, "Fast speed exceeds safety limits"

    return True, "Navigation parameters valid"

def validate_pick_up(params: dict) -> tuple[bool, str]:
    """Validate grasp command parameters."""
    obj = params.get("object_name", "").lower()

    if obj in LIMITS.forbidden_objects:
        return False, f"Cannot interact with forbidden object: {obj}"

    return True, "Pick-up parameters valid"

def validate_action(action: dict) -> tuple[bool, str]:
    """Validate any action against safety limits."""
    validators = {
        "navigate": validate_navigate,
        "pick_up": validate_pick_up,
        "stop": lambda p: (True, "Stop always valid"),
    }

    action_type = action.get("type", "")
    validator = validators.get(action_type)

    if validator is None:
        return False, f"Unknown action type: {action_type}"

    return validator(action.get("params", {}))
```

### Layer 3: Simulation Pre-Check

For safety-critical actions, test in simulation first:

```python
async def simulation_precheck(action: dict) -> tuple[bool, str]:
    """Run action in Gazebo simulation before real execution."""
    # Only for high-risk actions
    if action["type"] not in ["navigate", "pick_up"]:
        return True, "Low-risk action, skip simulation"

    # Send to simulation environment
    # Check for collisions, falls, or constraint violations
    # Return result

    # Simplified check:
    return True, "Simulation pre-check passed"
```

## Complete Validation Pipeline

```python
async def validate_command(actions: list[dict]) -> list[dict]:
    """Run all actions through the 3-layer validation pipeline."""
    validated = []

    for action in actions:
        # Layer 2: Parameter bounds
        is_valid, message = validate_action(action)
        if not is_valid:
            raise ValueError(f"Validation failed: {message}")

        # Layer 3: Simulation (for risky actions)
        sim_ok, sim_msg = await simulation_precheck(action)
        if not sim_ok:
            raise ValueError(f"Simulation check failed: {sim_msg}")

        validated.append(action)

    return validated
```

---

## Execution Phase

1. Implement the SafetyLimits dataclass with your robot's constraints
2. Write validators for each action type
3. Test with valid commands (should pass)
4. Test with dangerous commands (should reject with clear reason)
5. Test with edge cases (coordinates at exact boundary)

---

## Reflection

- Which validation layer caught the most issues?
- What commands slipped through all layers but were still problematic?
- How would you handle partial failures in a multi-step command?
