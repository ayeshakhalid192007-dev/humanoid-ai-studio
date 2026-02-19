---
title: "Module 4 Exercises"
sidebar_position: 9
description: "Hands-on VLA pipeline exercises using the Predict-Execute-Reflect methodology."
---

# Module 4 Exercises

---

## Exercise 1: Voice Transcription Setup

### Predict
1. What is the expected transcription latency for a 3-second audio clip?
2. How will background noise from a robot's motors affect accuracy?
3. What domain-specific words might Whisper misrecognize?

### Execute
1. Set up Whisper API with your OpenAI key
2. Record 10 robot commands of varying complexity
3. Transcribe each and record accuracy and latency
4. Add domain vocabulary hints and re-test

**Expected outcome**: &gt;90% accuracy on clear speech, &lt;3s latency.

### Reflect
- How did domain hints improve accuracy?
- What types of commands were most often misrecognized?
- How would you handle continuous listening vs push-to-talk?

---

## Exercise 2: LLM Command Parser with Safety

### Predict
1. Will the LLM consistently output valid JSON?
2. What percentage of commands will trigger safety validation?
3. How will the LLM handle a command in a different language?

### Execute
1. Implement the command parser from Lesson 3
2. Implement the safety validators from Lesson 4
3. Test with 20 commands:
   - 5 simple valid commands
   - 5 complex multi-step commands
   - 5 edge cases (ambiguous, incomplete)
   - 5 dangerous/invalid commands
4. Record: parse success rate, validation results, LLM latency

### Reflect
- How many commands produced valid JSON on first try?
- Did the safety validators catch all dangerous commands?
- What improvements would you make to the system prompt?

---

## Exercise 3: ROS 2 Action Server for Robot Control

### Predict
1. How long will it take to create a functional action server?
2. What feedback information is most useful during navigation?
3. How should the action server handle concurrent goals?

### Execute
1. Create a navigation action server (from Lesson 5)
2. Create an action client that sends goals from parsed commands
3. Test goal execution with feedback monitoring
4. Test action cancellation mid-execution
5. Test with multiple sequential actions

**Expected outcome**: Action server handles goals, provides feedback, supports cancellation.

### Reflect
- How did feedback help understand execution progress?
- What happened when you sent a new goal while one was executing?
- How would you handle a sequence of dependent actions?

---

## Exercise 4: Full VLA Pipeline Integration

### Predict
1. What is the total end-to-end latency for the full pipeline?
2. Which stage will be the bottleneck?
3. How many consecutive commands can the pipeline handle?

### Execute
1. Connect all components: Speech → LLM → Validation → Action Server
2. Time the full pipeline for 10 voice commands
3. Apply optimization from Lesson 6 (caching, model selection)
4. Add pipeline monitoring from Lesson 7
5. Test error recovery: what happens when one stage fails?

**Expected outcome**: Full pipeline works end-to-end with &lt;10s latency.

### Reflect
- What was the actual end-to-end latency?
- Which optimization had the largest impact?
- What would you change for a production deployment?

---

## Module 4 Review

### Key Concepts

| Concept | Summary |
|---------|---------|
| VLA Pipeline | Speech → Text → Intent → Plan → Action |
| Whisper | OpenAI speech-to-text model |
| LLM Parsing | Structured command extraction using GPT |
| Safety Validation | Multi-layer checking: prompt, bounds, simulation |
| ROS 2 Actions | Long-running tasks with feedback and cancellation |
| Latency Optimization | Caching, model selection, parallel processing |

### Self-Assessment

- [ ] I can set up speech-to-text transcription
- [ ] I can build an LLM command parser with structured output
- [ ] I can implement multi-layer safety validation
- [ ] I can create ROS 2 action servers and clients
- [ ] I can optimize pipeline latency to meet targets
- [ ] I can debug VLA pipeline failures systematically
