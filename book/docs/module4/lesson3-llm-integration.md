---
title: "Lesson 3: LLM Integration"
sidebar_position: 4
description: "Use Large Language Models for robot command understanding and structured output."
---

# Lesson 3: LLM Integration for Robot Control

## Prediction Phase

- How do you get structured, machine-readable output from an LLM?
- What prevents the LLM from generating impossible robot commands?
- How do you handle ambiguous commands like "move a bit to the left"?

---

## OpenAI API Setup

```python
from openai import OpenAI

client = OpenAI()  # Uses OPENAI_API_KEY env variable
```

## Prompt Engineering for Robot Control

The system prompt constrains the LLM to output valid robot commands:

```python
SYSTEM_PROMPT = """You are a robot command interpreter for a humanoid robot.

Available actions:
- navigate(x, y): Move to coordinates (meters)
- pick_up(object_name): Grasp an object
- put_down(location): Release held object
- wave(): Wave hand greeting
- stop(): Emergency stop

Rules:
1. Only use available actions listed above
2. Output valid JSON with an "actions" array
3. If the command is unclear, ask for clarification
4. If the command is dangerous or impossible, explain why and refuse
5. Break complex commands into sequential actions

Output format:
{"actions": [{"type": "action_name", "params": {...}}]}
"""

def parse_command(user_text: str) -> dict:
    """Parse voice command into structured robot actions."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        response_format={"type": "json_object"},
        temperature=0.1,  # Low temperature for consistent parsing
        max_tokens=200
    )

    import json
    return json.loads(response.choices[0].message.content)
```

### Function Calling (Structured Output)

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "navigate",
            "description": "Move the robot to a target position",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "number", "description": "X coordinate in meters"},
                    "y": {"type": "number", "description": "Y coordinate in meters"},
                    "speed": {"type": "string", "enum": ["slow", "normal", "fast"]}
                },
                "required": ["x", "y"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "pick_up",
            "description": "Pick up an object",
            "parameters": {
                "type": "object",
                "properties": {
                    "object_name": {"type": "string"},
                    "approach": {"type": "string", "enum": ["top", "side"]}
                },
                "required": ["object_name"]
            }
        }
    }
]

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a robot command interpreter."},
        {"role": "user", "content": "Go to the table and pick up the cup"}
    ],
    tools=tools,
    tool_choice="auto"
)
```

## Cost Optimization

| Strategy | Savings | Trade-off |
|----------|---------|-----------|
| Use `gpt-4o-mini` | 10-20x cheaper than GPT-4 | Slightly less capable |
| Low `max_tokens` | Proportional | May truncate complex responses |
| Cache common commands | Up to 80% | Stale if actions change |
| Batch commands | Reduce API calls | Higher per-command latency |

:::warning Rate Limiting
OpenAI API has rate limits. For a classroom of 20 students:
- Cache frequent commands locally
- Implement client-side rate limiting (20 queries/hour per session)
- Monitor daily spend with usage dashboard
:::

## Multi-Turn Conversation Context

```python
conversation = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

def process_command(user_input: str) -> dict:
    conversation.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation[-6:],  # Keep last 3 turns for context
        response_format={"type": "json_object"},
        temperature=0.1
    )

    result = response.choices[0].message.content
    conversation.append({"role": "assistant", "content": result})

    import json
    return json.loads(result)
```

---

## Execution Phase

1. Set up OpenAI API key
2. Implement the command parser with the system prompt
3. Test with various commands: simple ("go forward"), complex ("pick up the red cup from the table"), and ambiguous ("move there")
4. Implement function calling and compare output quality
5. Measure API latency and cost per command

---

## Reflection

- How consistently did the LLM produce valid JSON output?
- What commands caused incorrect or dangerous interpretations?
- How did function calling improve output reliability?
