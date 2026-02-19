---
title: "Lesson 2: Nodes, Topics & Pub/Sub Patterns"
sidebar_position: 3
description: "Master ROS 2 communication with publishers, subscribers, QoS policies, and topic CLI tools."
---

# Lesson 2: Nodes, Topics & Publish/Subscribe Patterns

## Prediction Phase

Before reading, consider:
- How do independent programs (nodes) share data in a distributed system?
- What happens if a subscriber can't process messages as fast as they arrive?
- Why might you need different reliability guarantees for sensor data vs. commands?

---

## ROS 2 Communication Model

ROS 2 nodes communicate primarily through **topics** using the publish/subscribe pattern. This is a decoupled, asynchronous communication model where:

- **Publishers** send messages to a named topic
- **Subscribers** listen on a named topic and receive messages
- Publishers and subscribers don't need to know about each other

:::info Key Concept
Topics are named buses. Any node can publish or subscribe to any topic, enabling modular, loosely-coupled architectures.
:::

## Nodes

A **node** is a single-purpose process in the ROS 2 graph. Each node should handle one concern:

```python
import rclpy
from rclpy.node import Node

class SensorReader(Node):
    def __init__(self):
        super().__init__('sensor_reader')
        self.get_logger().info('Sensor reader node started')

def main():
    rclpy.init()
    node = SensorReader()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
```

## Publisher Node

A publisher sends messages at a regular interval:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

class TemperaturePublisher(Node):
    def __init__(self):
        super().__init__('temperature_publisher')

        # Configure QoS for sensor data
        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=5
        )

        self.publisher = self.create_publisher(
            Float64, '/sensors/temperature', sensor_qos
        )
        self.timer = self.create_timer(0.1, self.publish_temperature)
        self.get_logger().info('Publishing temperature at 10 Hz')

    def publish_temperature(self):
        msg = Float64()
        msg.data = 36.6  # Simulated reading
        self.publisher.publish(msg)

def main():
    rclpy.init()
    node = TemperaturePublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Subscriber Node

A subscriber processes incoming messages via a callback:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

class TemperatureMonitor(Node):
    def __init__(self):
        super().__init__('temperature_monitor')

        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=5
        )

        self.subscription = self.create_subscription(
            Float64, '/sensors/temperature',
            self.temperature_callback, sensor_qos
        )
        self.get_logger().info('Monitoring temperature topic')

    def temperature_callback(self, msg):
        temp = msg.data
        if temp > 40.0:
            self.get_logger().warn(f'HIGH TEMP: {temp}°C')
        else:
            self.get_logger().info(f'Temperature: {temp}°C')

def main():
    rclpy.init()
    node = TemperatureMonitor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Quality of Service (QoS) Policies

QoS policies control how messages are delivered between publishers and subscribers.

### Key QoS Settings

| Policy | Options | Use Case |
|--------|---------|----------|
| **Reliability** | `RELIABLE` / `BEST_EFFORT` | Reliable for commands, best-effort for sensors |
| **Durability** | `VOLATILE` / `TRANSIENT_LOCAL` | Transient local for late-joining subscribers |
| **History** | `KEEP_LAST` / `KEEP_ALL` | Keep last N messages or all |
| **Depth** | Integer (1-1000+) | How many messages to buffer |

### Common QoS Profiles

```python
from rclpy.qos import qos_profile_sensor_data, qos_profile_system_default

# Sensor data: best-effort, volatile, keep last 5
# Use for: IMU, camera, lidar (high frequency, OK to drop)
sensor_qos = qos_profile_sensor_data

# System default: reliable, volatile, keep last 10
# Use for: commands, state updates (must not drop)
default_qos = qos_profile_system_default
```

:::warning QoS Compatibility
Publisher and subscriber QoS must be compatible. A `BEST_EFFORT` publisher cannot communicate with a `RELIABLE` subscriber. Mismatched QoS is a common source of "no messages received" bugs.
:::

## Topic CLI Commands

Essential commands for inspecting the ROS 2 topic graph:

```bash
# List all active topics
ros2 topic list

# List with message types
ros2 topic list -t

# Show messages on a topic
ros2 topic echo /sensors/temperature

# Topic metadata (type, publishers, subscribers)
ros2 topic info /sensors/temperature

# Measure publish rate
ros2 topic hz /sensors/temperature

# Publish a single message
ros2 topic pub /sensors/temperature std_msgs/msg/Float64 "{data: 42.0}"

# Publish at 10 Hz
ros2 topic pub --rate 10 /sensors/temperature std_msgs/msg/Float64 "{data: 42.0}"
```

## Node CLI Commands

```bash
# List active nodes
ros2 node list

# Node details (subscribers, publishers, services)
ros2 node info /temperature_publisher
```

---

## Execution Phase

1. Create a ROS 2 package and add both nodes above
2. Run the publisher: `ros2 run your_package temperature_publisher`
3. In another terminal, run the subscriber: `ros2 run your_package temperature_monitor`
4. Use `ros2 topic list`, `ros2 topic echo`, and `ros2 topic hz` to inspect
5. Try changing QoS settings and observe the effects

---

## Reflection

- What happened when you changed reliability from `BEST_EFFORT` to `RELIABLE`?
- How does the `depth` parameter affect behavior under high publish rates?
- When would you choose `KEEP_ALL` history vs `KEEP_LAST`?
- How does the topic abstraction enable modular robot architectures?

---

## Key Takeaways

- Topics provide decoupled, many-to-many communication
- QoS policies must match between publishers and subscribers
- Use `BEST_EFFORT` for high-frequency sensor streams
- Use `RELIABLE` for commands and critical state updates
- CLI tools (`ros2 topic`, `ros2 node`) are essential for debugging
