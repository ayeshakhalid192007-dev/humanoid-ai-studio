---
title: "Lesson 4: ROS 2 Services"
sidebar_position: 5
description: "Learn request/response communication with ROS 2 services for robot control interfaces."
---

# Lesson 4: ROS 2 Services & Service-Based Control

## Prediction Phase

Before reading, consider:
- When would you need a guaranteed response rather than fire-and-forget messaging?
- How is controlling a robot arm joint different from streaming sensor data?
- What happens if two nodes try to call the same service simultaneously?

---

## Services vs Topics

| Feature | Topics (Pub/Sub) | Services (Request/Response) |
|---------|------------------|-----------------------------|
| Pattern | Many-to-many, async | One-to-one, synchronous |
| Guarantees | No response confirmation | Response confirms completion |
| Use case | Streaming data, events | Commands, queries, configuration |
| Example | Sensor readings | Set joint position, get robot state |

:::info When to Use Services
Use services when the caller **needs to know the result** of an operation. Use topics when data flows continuously without needing acknowledgment.
:::

## Service Definition (.srv Files)

Service interfaces define the request and response types, separated by `---`:

```
# SetJointPosition.srv
string joint_name
float64 target_position
float64 max_velocity
---
bool success
string message
float64 actual_position
```

## Service Server

The server handles incoming requests:

```python
import rclpy
from rclpy.node import Node
from example_interfaces.srv import SetBool

class GripperController(Node):
    def __init__(self):
        super().__init__('gripper_controller')
        self.srv = self.create_service(
            SetBool, '/gripper/activate', self.handle_gripper
        )
        self.gripper_active = False
        self.get_logger().info('Gripper service ready')

    def handle_gripper(self, request, response):
        self.gripper_active = request.data
        state = "ACTIVATED" if request.data else "DEACTIVATED"
        self.get_logger().info(f'Gripper {state}')

        response.success = True
        response.message = f'Gripper {state.lower()} successfully'
        return response

def main():
    rclpy.init()
    node = GripperController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Service Client

The client sends requests and waits for responses:

```python
import rclpy
from rclpy.node import Node
from example_interfaces.srv import SetBool

class GripperClient(Node):
    def __init__(self):
        super().__init__('gripper_client')
        self.client = self.create_client(SetBool, '/gripper/activate')

        # Wait for service to be available
        while not self.client.wait_for_service(timeout_sec=2.0):
            self.get_logger().warn('Waiting for gripper service...')

    def send_request(self, activate: bool):
        request = SetBool.Request()
        request.data = activate
        future = self.client.call_async(request)
        return future

def main():
    rclpy.init()
    client = GripperClient()

    future = client.send_request(True)
    rclpy.spin_until_future_complete(client, future)

    result = future.result()
    if result.success:
        client.get_logger().info(f'Result: {result.message}')
    else:
        client.get_logger().error(f'Failed: {result.message}')

    client.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

:::warning Async Calls
Always use `call_async()` rather than blocking `call()`. Blocking calls can deadlock the node's executor. Use `spin_until_future_complete()` or callbacks to handle responses.
:::

## Service CLI Commands

```bash
# List active services
ros2 service list

# Show service type
ros2 service type /gripper/activate

# Find services by type
ros2 service find example_interfaces/srv/SetBool

# Call a service from terminal
ros2 service call /gripper/activate example_interfaces/srv/SetBool "{data: true}"
```

## Services vs Topics vs Actions

| | Topics | Services | Actions |
|--|--------|----------|---------|
| Communication | Pub/Sub | Request/Response | Goal/Feedback/Result |
| Blocking | No | Yes (client waits) | No (async with feedback) |
| Cancel | N/A | N/A | Yes |
| Use case | Sensor data | Quick commands | Long-running tasks |

---

## Execution Phase

1. Run the gripper server: `ros2 run your_package gripper_controller`
2. Call it from CLI: `ros2 service call /gripper/activate example_interfaces/srv/SetBool "{data: true}"`
3. Run the client node and observe the request/response flow
4. Use `ros2 service list` and `ros2 service type` to inspect

---

## Reflection

- How does the service pattern differ from publishing a command on a topic?
- What would happen if the service server crashes mid-request?
- When would you choose an Action over a Service?
- How could services be used for robot configuration management?
