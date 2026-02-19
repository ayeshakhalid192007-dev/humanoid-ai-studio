---
sidebar_position: 2
title: Lesson 1 - ROS 2 Fundamentals
description: Install ROS 2 Humble and create your first publisher/subscriber nodes
---

# Lesson 1: ROS 2 Fundamentals

## Overview

In this lesson, you'll install ROS 2 Humble, understand the core publish-subscribe pattern, and create your first nodes. By the end, you'll have a working talker/listener system demonstrating message flow.

## Installation (Ubuntu 22.04)

### Step 1: Setup Sources

```bash
# Ensure UTF-8 locale
sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# Add ROS 2 apt repository
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
```

### Step 2: Install ROS 2 Humble

```bash
sudo apt update
sudo apt upgrade
sudo apt install ros-humble-desktop python3-argcomplete
sudo apt install ros-dev-tools
```

### Step 3: Environment Setup

Add to your `~/.bashrc`:

```bash
source /opt/ros/humble/setup.bash
```

Then reload: `source ~/.bashrc`

## Core Concepts

### Nodes

A **node** is an independent process that performs computation. Nodes communicate via:
- **Topics**: Asynchronous pub/sub (many-to-many)
- **Services**: Synchronous request/response (one-to-one)
- **Actions**: Long-running tasks with feedback

### Topics

Topics enable **decoupled communication**:
- Publishers send messages to a topic
- Subscribers receive messages from a topic
- Multiple publishers/subscribers can use the same topic

**Analogy**: Topics are like radio stations. Publishers broadcast on a frequency, subscribers tune in.

## Prediction Exercise

**Before running the code below**, answer:
1. What topic name will be used?
2. How many nodes will be running?
3. What message type will flow?
4. What happens if the listener starts after the publisher?

## Example: Talker/Listener

### Talker (Publisher)

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class TalkerNode(Node):
    def __init__(self):
        super().__init__('talker')
        self.publisher = self.create_publisher(String, 'chatter', 10)
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.counter = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello World: {self.counter}'
        self.publisher.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.counter += 1

def main(args=None):
    rclpy.init(args=args)
    node = TalkerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Listener (Subscriber)

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class ListenerNode(Node):
    def __init__(self):
        super().__init__('listener')
        self.subscription = self.create_subscription(
            String, 'chatter', self.listener_callback, 10)

    def listener_callback(self, msg):
        self.get_logger().info(f'I heard: "{msg.data}"')

def main(args=None):
    rclpy.init(args=args)
    node = ListenerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Running the Example

### Terminal 1: Start Talker
```bash
python3 talker.py
```

**Expected Output**:
```
[INFO] [talker]: Publishing: "Hello World: 0"
[INFO] [talker]: Publishing: "Hello World: 1"
[INFO] [talker]: Publishing: "Hello World: 2"
```

### Terminal 2: Start Listener
```bash
python3 listener.py
```

**Expected Output**:
```
[INFO] [listener]: I heard: "Hello World: 2"
[INFO] [listener]: I heard: "Hello World: 3"
[INFO] [listener]: I heard: "Hello World: 4"
```

## Reflection Questions

1. **Why did the listener miss messages 0, 1, 2?**
   - The publisher started before the subscriber
   - Messages sent before subscription are lost (no buffering by default)
   - **Fix**: Start listener first, or use QoS RELIABLE mode

2. **What happens if you start two listeners?**
   - Both receive all messages (pub/sub is many-to-many)
   - Each listener gets its own copy

3. **What if you stop the talker?**
   - Listener continues waiting for messages
   - No error - ROS 2 handles node disconnection gracefully

## CLI Tools

### List Active Topics
```bash
ros2 topic list
```

### Echo Topic Messages
```bash
ros2 topic echo /chatter
```

### View Topic Info
```bash
ros2 topic info /chatter
```

### Visualize Node Graph
```bash
rqt_graph
```

## Acceptance Criteria

You've completed this lesson when you can:
- ✅ Run talker and listener nodes successfully
- ✅ Explain why messages are lost if listener starts late
- ✅ Use `ros2 topic list` and `ros2 topic echo` to debug
- ✅ Modify the message content and observe changes
- ✅ Predict what happens with multiple publishers/subscribers

## Next Steps

Continue to [Lesson 2: URDF Robot Modeling](./lesson2-urdf-models.md) to learn how to define robot structure and kinematics.

---

**💡 Ask the Chatbot**:
- "What's the difference between QoS RELIABLE and BEST_EFFORT?"
- "How do I debug a node that isn't publishing?"
- "What message types are available in ROS 2?"
