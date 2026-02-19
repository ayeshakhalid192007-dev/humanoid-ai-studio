---
title: "Lesson 5: RQT & Debugging Tools"
sidebar_position: 6
description: "Use RQT graph, console, and plotting tools to visualize and debug ROS 2 systems."
---

# Lesson 5: RQT Visualization & Debugging Tools

## Prediction Phase

Before reading, consider:
- How would you visualize all the nodes and topics in a running system?
- What tools help when a subscriber isn't receiving expected messages?
- How do you monitor real-time data without writing custom code?

---

## RQT Ecosystem Overview

RQT is a Qt-based framework for ROS 2 GUI tools. Key plugins:

| Tool | Purpose | Command |
|------|---------|---------|
| `rqt_graph` | Node/topic connection graph | `ros2 run rqt_graph rqt_graph` |
| `rqt_console` | Log message viewer | `ros2 run rqt_console rqt_console` |
| `rqt_plot` | Real-time data plotting | `ros2 run rqt_plot rqt_plot` |
| `rqt_topic` | Topic introspection | `ros2 run rqt_topic rqt_topic` |

## rqt_graph: Visualizing the Node Graph

`rqt_graph` shows how nodes are connected through topics:

```bash
# Launch rqt_graph
ros2 run rqt_graph rqt_graph
```

The graph displays:
- **Ovals**: Nodes
- **Arrows**: Topic connections (publisher → subscriber)
- **Labels**: Topic names on arrows

:::tip Debugging Disconnected Nodes
If a node appears isolated (no arrows), check:
1. Is the topic name spelled correctly?
2. Are QoS policies compatible?
3. Is the node actually publishing/subscribing?
:::

## rqt_console: Log Message Viewer

View and filter log messages from all running nodes:

```bash
ros2 run rqt_console rqt_console
```

Features:
- Filter by severity: DEBUG, INFO, WARN, ERROR, FATAL
- Filter by node name
- Search message content
- Highlight patterns

## rqt_plot: Real-Time Data Plotting

Plot numeric topic data in real-time:

```bash
# Plot temperature data
ros2 run rqt_plot rqt_plot /sensors/temperature/data

# Plot multiple fields
ros2 run rqt_plot rqt_plot /joint_states/position[0] /joint_states/position[1]
```

## CLI Debugging Commands

### Node Inspection

```bash
# List all running nodes
ros2 node list

# Detailed node info (publishers, subscribers, services)
ros2 node info /temperature_publisher
```

### Topic Debugging

```bash
# See all topics with types
ros2 topic list -t

# Check publish frequency
ros2 topic hz /sensors/temperature

# Check message bandwidth
ros2 topic bw /camera/image_raw

# See message content
ros2 topic echo /sensors/temperature

# Show one message then exit
ros2 topic echo /sensors/temperature --once
```

### Interface Inspection

```bash
# Show message definition
ros2 interface show std_msgs/msg/Float64

# Show service definition
ros2 interface show example_interfaces/srv/SetBool
```

## Debugging Workflow

When something isn't working, follow this systematic approach:

**Step 1: Check nodes are running**
```bash
ros2 node list
# Verify expected nodes appear
```

**Step 2: Check topic connections**
```bash
ros2 topic list -t
ros2 topic info /your_topic
# Verify publishers and subscriber counts
```

**Step 3: Verify data flow**
```bash
ros2 topic echo /your_topic
ros2 topic hz /your_topic
# Confirm messages are being published
```

**Step 4: Check QoS compatibility**
```bash
ros2 topic info /your_topic --verbose
# Compare publisher/subscriber QoS settings
```

**Step 5: Visualize the full graph**
```bash
ros2 run rqt_graph rqt_graph
# Look for disconnected nodes or unexpected connections
```

:::warning Common Issues
- **No messages**: QoS mismatch between publisher and subscriber
- **Delayed messages**: Network latency or overloaded callback queue
- **Missing nodes**: Node crashed silently — check `rqt_console` for errors
- **Wrong data**: Check message type matches between publisher and subscriber
:::

---

## Execution Phase

1. Start multiple nodes from previous lessons (publisher, subscriber, service)
2. Launch `rqt_graph` and observe the node connection graph
3. Open `rqt_console` and filter messages by severity
4. Plot sensor data in real-time with `rqt_plot`
5. Practice the debugging workflow by intentionally breaking a QoS setting

---

## Reflection

- How did `rqt_graph` help you understand the system architecture?
- What would you check first when a subscriber reports no messages?
- How does real-time plotting help in tuning control parameters?
- What debugging information is available from `ros2 node info`?
