---
title: "Debugging Checklist"
sidebar_position: 4
description: "Systematic troubleshooting guide for capstone integration issues."
---

# Capstone Debugging Checklist

## Quick Diagnostic Commands

```bash
# Check all nodes are running
ros2 node list

# Check all topics
ros2 topic list -t

# Check TF tree
ros2 run tf2_tools view_frames

# Check Nav2 status
ros2 action list
```

## Issue: Robot Doesn't Move

```
□ Is Gazebo running? → Check terminal for Gazebo errors
□ Is cmd_vel being published? → ros2 topic echo /cmd_vel
□ Is Nav2 controller running? → ros2 node list | grep controller
□ Is the goal being sent? → ros2 topic echo /navigate_to_pose/_action/status
□ Is the TF chain complete? → ros2 run tf2_tools view_frames
□ Is AMCL localized? → Check particle cloud in RViz2
```

## Issue: Voice Commands Not Recognized

```
□ Is the microphone working? → Test with: python -c "import sounddevice; print(sounddevice.query_devices())"
□ Is audio being captured? → Check audio file size > 0
□ Is Whisper API accessible? → Test with a known audio file
□ Is the OpenAI API key set? → echo $OPENAI_API_KEY
□ Is the speech node running? → ros2 node list | grep speech
□ Is the text being published? → ros2 topic echo /speech/text
```

## Issue: LLM Produces Invalid Output

```
□ Is the system prompt loaded correctly? → Log it at startup
□ Is the response valid JSON? → Try response_format: json_object
□ Are action names matching? → Compare with KNOWN_ACTIONS list
□ Is the temperature too high? → Set temperature=0.1 for consistency
□ Is the context too long? → Check max_tokens limit
```

## Issue: Navigation Fails

```
□ Is the map loaded? → ros2 topic echo /map --once
□ Is the goal in free space? → Check costmap in RViz2
□ Is the inflation radius too large? → Try reducing inflation_radius
□ Is the robot localized? → Set 2D Pose Estimate in RViz2
□ Are sensors publishing? → ros2 topic hz /scan
□ Is the costmap updating? → Visualize local costmap in RViz2
```

## Issue: High Latency (>10s)

```
□ Which stage is slowest? → Check per-stage timing logs
□ Is Whisper using the API? → Local Whisper is slower
□ Is LLM model correct? → Use gpt-4o-mini (faster than gpt-4)
□ Is caching enabled? → Check common command cache hits
□ Is the network slow? → Test API latency: curl -w "%{time_total}" ...
```

## Issue: Safety Validation Rejects Valid Commands

```
□ Are workspace bounds correct? → Print SafetyLimits values
□ Is the object in forbidden list? → Check forbidden_objects
□ Are velocity limits too strict? → Review max_linear_vel setting
□ Is simulation pre-check running? → Check if Gazebo is responding
```

## General Debugging Procedure

1. **Isolate**: Which subsystem is failing? Test each independently.
2. **Log**: Enable verbose logging in the failing subsystem.
3. **Inspect**: Use `ros2 topic echo/info/hz` to check data flow.
4. **Visualize**: Use RViz2 to see costmaps, TF, sensor data.
5. **Simplify**: Remove components until it works, then add back.

:::tip Ask the AI Chatbot
Use the course chatbot to ask questions about specific error messages or debugging procedures. Try selecting the error text and asking "What does this error mean?"
:::
