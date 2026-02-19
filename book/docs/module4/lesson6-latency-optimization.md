---
title: "Lesson 6: Latency Optimization"
sidebar_position: 7
description: "Optimize the VLA pipeline to achieve under 10 seconds from voice to action."
---

# Lesson 6: Latency Optimization

## Prediction Phase

- Which VLA pipeline stage contributes the most latency?
- Can any stages run in parallel?
- What is the theoretical minimum latency for a voice command?

---

## Profiling the Pipeline

Measure each stage independently:

```python
import time
from contextlib import contextmanager

@contextmanager
def timer(stage_name: str):
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    print(f"[{stage_name}] {elapsed:.3f}s")

# Usage
with timer("Transcription"):
    text = transcribe_audio(audio_file)

with timer("LLM Parsing"):
    actions = parse_command(text)

with timer("Validation"):
    validated = validate_command(actions)

with timer("Action Start"):
    execute_actions(validated)
```

## Optimization Strategies

### 1. Streaming Transcription

Process audio while the user is still speaking:

```python
# Instead of recording full audio then transcribing:
# Record 5s → Transcribe → Parse → Execute (serial: ~8s)

# Use streaming: start transcription while recording
# This saves 2-3s of latency
```

### 2. LLM Optimization

| Strategy | Latency Reduction | Implementation |
|----------|-------------------|----------------|
| Use `gpt-4o-mini` | 2-3x faster than GPT-4 | Change model parameter |
| Lower `max_tokens` | Proportional | Set to 150-200 |
| Response caching | Eliminates API call | Local cache for common commands |
| Streaming response | Start parsing earlier | `stream=True` |

```python
# Cache common commands
COMMAND_CACHE = {
    "stop": {"actions": [{"type": "stop", "params": {}}]},
    "come here": {"actions": [{"type": "navigate", "params": {"x": 0, "y": 0}}]},
}

def parse_with_cache(text: str) -> dict:
    normalized = text.strip().lower()
    if normalized in COMMAND_CACHE:
        return COMMAND_CACHE[normalized]
    return parse_command(text)  # Fall back to LLM
```

### 3. Parallel Processing

```python
import asyncio

async def process_command_parallel(audio_file: str):
    """Process VLA pipeline with parallel stages where possible."""

    # Stage 1: Transcription (must be first)
    text = await transcribe_async(audio_file)

    # Stage 2 + 3: LLM parsing and pre-validation can overlap
    parse_task = asyncio.create_task(parse_command_async(text))

    # Wait for parsing
    actions = await parse_task

    # Stage 4: Validation (fast, <100ms)
    validated = validate_command(actions)

    # Stage 5: Execute immediately
    await execute_actions(validated)
```

## Benchmarking

Create a benchmark suite:

```python
import statistics

def benchmark_pipeline(test_commands: list[str], iterations: int = 10):
    results = {stage: [] for stage in ["total", "transcription", "parsing", "validation", "execution"]}

    for command in test_commands:
        for _ in range(iterations):
            # Time each stage
            total_start = time.perf_counter()
            # ... measure each stage ...
            results["total"].append(time.perf_counter() - total_start)

    # Report statistics
    for stage, times in results.items():
        print(f"{stage}: mean={statistics.mean(times):.2f}s, "
              f"p95={sorted(times)[int(len(times)*0.95)]:.2f}s")
```

Target metrics:
- **Total latency**: &lt;10s (p95)
- **Transcription**: &lt;3s
- **LLM parsing**: &lt;3s
- **Validation**: &lt;0.1s
- **Action start**: &lt;0.5s

---

## Execution Phase

1. Add timing instrumentation to each pipeline stage
2. Run the benchmark with 10+ test commands
3. Identify the bottleneck stage
4. Apply optimizations (caching, model selection, parallelism)
5. Re-benchmark and compare

---

## Reflection

- Which optimization had the biggest impact?
- What is the realistic minimum latency with current technology?
- How would you optimize differently for a robot with local GPU?
