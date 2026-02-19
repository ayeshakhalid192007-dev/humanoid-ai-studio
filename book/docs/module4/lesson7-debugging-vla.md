---
title: "Lesson 7: Debugging VLA Systems"
sidebar_position: 8
description: "Troubleshoot VLA pipeline failures including LLM errors, invalid commands, and integration issues."
---

# Lesson 7: Debugging VLA Pipelines

## Prediction Phase

- What types of failures can occur at each pipeline stage?
- How do you distinguish between a transcription error and an LLM error?
- What logging is needed to debug VLA issues in production?

---

## Failure Categories

### Stage Failures

| Stage | Failure | Symptom | Fix |
|-------|---------|---------|-----|
| Speech | No audio | Empty transcription | Check mic, permissions |
| Transcription | Wrong words | Invalid command parsed | Improve Whisper prompt |
| LLM | Hallucination | Non-existent action generated | Tighten system prompt |
| LLM | Wrong JSON | Parse error | Use function calling |
| Validation | Rejected command | Action refused | Check safety limits |
| Execution | Action failed | Robot doesn't move | Check ROS 2 action server |

### LLM Hallucination Handling

```python
KNOWN_ACTIONS = {"navigate", "pick_up", "put_down", "wave", "stop"}

def validate_llm_output(parsed: dict) -> dict:
    """Validate that LLM output contains only known actions."""
    validated_actions = []

    for action in parsed.get("actions", []):
        if action.get("type") not in KNOWN_ACTIONS:
            print(f"WARNING: Unknown action '{action['type']}' - skipping")
            continue
        validated_actions.append(action)

    if not validated_actions:
        raise ValueError("No valid actions in LLM output")

    return {"actions": validated_actions}
```

### Ambiguous Input Resolution

```python
CLARIFICATION_PROMPT = """
The user's command is ambiguous. Generate a clarification question.

Command: "{command}"
Ambiguity: {reason}

Respond with a brief clarification question.
"""

def handle_ambiguous_command(command: str, reason: str) -> str:
    """Ask user for clarification when command is ambiguous."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": CLARIFICATION_PROMPT.format(
                command=command, reason=reason
            )}
        ],
        max_tokens=50
    )
    return response.choices[0].message.content
```

## Pipeline Monitoring

```python
import logging

logger = logging.getLogger("vla_pipeline")

class PipelineMonitor:
    """Log all VLA pipeline events for debugging."""

    def log_transcription(self, audio_length: float, text: str, confidence: float):
        logger.info(f"TRANSCRIPTION audio={audio_length:.1f}s text='{text}' conf={confidence:.2f}")

    def log_llm_parse(self, input_text: str, output: dict, latency: float):
        logger.info(f"LLM_PARSE input='{input_text}' actions={len(output.get('actions',[]))} latency={latency:.2f}s")

    def log_validation(self, action: dict, passed: bool, reason: str):
        level = logging.INFO if passed else logging.WARNING
        logger.log(level, f"VALIDATION action={action['type']} passed={passed} reason='{reason}'")

    def log_execution(self, action: dict, success: bool, duration: float):
        level = logging.INFO if success else logging.ERROR
        logger.log(level, f"EXECUTION action={action['type']} success={success} duration={duration:.2f}s")
```

## Troubleshooting Decision Tree

```
Command not working?
├── Check transcription output
│   ├── Empty → Check microphone and audio capture
│   └── Wrong words → Adjust Whisper prompt context
├── Check LLM output
│   ├── Invalid JSON → Switch to function calling
│   ├── Unknown action → Tighten system prompt
│   └── Wrong parameters → Add few-shot examples
├── Check validation
│   ├── Rejected → Review safety limits
│   └── Passed incorrectly → Strengthen validators
└── Check execution
    ├── Action server not found → ros2 action list
    ├── Goal rejected → Check action server state
    └── Timeout → Check robot hardware/simulation
```

---

## Execution Phase

1. Add PipelineMonitor logging to your VLA pipeline
2. Test with intentionally bad inputs:
   - Mumbled speech
   - Impossible commands ("fly to the moon")
   - Ambiguous commands ("go over there")
   - Mixed language
3. Review logs and trace each failure to its source
4. Implement fixes for each failure type

---

## Reflection

- Which failure type was most common in your testing?
- How did the troubleshooting decision tree help?
- What additional monitoring would you add for production?
