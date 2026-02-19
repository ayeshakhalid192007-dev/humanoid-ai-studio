---
title: "Lesson 5: ROS 2 Action Servers"
sidebar_position: 6
description: "Implement ROS 2 action servers to execute robot commands from the VLA pipeline."
---

# Lesson 5: ROS 2 Action Servers for VLA

## Prediction Phase

- Why use actions instead of services for robot movement commands?
- What information should action feedback provide during execution?
- How do you cancel a robot action that's in progress?

---

## Actions vs Services vs Topics

| Feature | Topic | Service | **Action** |
|---------|-------|---------|-----------|
| Pattern | Pub/Sub | Request/Response | Goal/Feedback/Result |
| Async | Yes | Blocking | **Yes** |
| Feedback | No | No | **Yes (continuous)** |
| Cancelable | No | No | **Yes** |
| Use case | Data streams | Quick queries | **Long-running tasks** |

:::info Why Actions for VLA
Robot movements take seconds to minutes. Actions provide:
- Progress feedback ("50% complete, 2m to goal")
- Cancellation ("stop, new command incoming")
- Final result ("reached goal" or "failed: obstacle")
:::

## Action Server Implementation

```python
import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
import time

class RobotActionServer(Node):
    def __init__(self):
        super().__init__('robot_action_server')

        self._nav_server = ActionServer(
            self,
            NavigateToPose,
            'navigate_to_pose',
            self.execute_navigation
        )
        self.get_logger().info('Robot action server ready')

    async def execute_navigation(self, goal_handle):
        """Execute a navigation goal with feedback."""
        self.get_logger().info('Executing navigation goal...')

        target = goal_handle.request.pose
        feedback_msg = NavigateToPose.Feedback()

        # Simulate navigation with progress updates
        total_distance = 5.0  # Example
        for step in range(10):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info('Navigation canceled')
                return NavigateToPose.Result()

            # Update progress
            remaining = total_distance * (1 - step / 10)
            feedback_msg.distance_remaining = remaining
            goal_handle.publish_feedback(feedback_msg)

            time.sleep(0.5)  # Simulate movement time

        goal_handle.succeed()
        result = NavigateToPose.Result()
        self.get_logger().info('Navigation completed')
        return result

def main():
    rclpy.init()
    server = RobotActionServer()
    rclpy.spin(server)
```

## Action Client (VLA Integration)

```python
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped

class VLAActionClient(Node):
    def __init__(self):
        super().__init__('vla_action_client')
        self._nav_client = ActionClient(
            self, NavigateToPose, 'navigate_to_pose'
        )

    def send_navigation_goal(self, x: float, y: float):
        """Send navigation goal from parsed VLA command."""
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.orientation.w = 1.0

        self._nav_client.wait_for_server()

        future = self._nav_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        future.add_done_callback(self.goal_response_callback)

    def feedback_callback(self, feedback_msg):
        remaining = feedback_msg.feedback.distance_remaining
        self.get_logger().info(f'Distance remaining: {remaining:.1f}m')

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected')
            return

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        self.get_logger().info('Navigation complete!')
```

## VLA Command Executor

Connects LLM output to ROS 2 actions:

```python
class VLAExecutor(Node):
    def __init__(self):
        super().__init__('vla_executor')
        self.nav_client = VLAActionClient()

    async def execute_actions(self, actions: list[dict]):
        """Execute a list of validated VLA actions sequentially."""
        for action in actions:
            self.get_logger().info(f'Executing: {action["type"]}')

            if action["type"] == "navigate":
                self.nav_client.send_navigation_goal(
                    action["params"]["x"],
                    action["params"]["y"]
                )
            elif action["type"] == "stop":
                # Cancel any active goals
                pass

    async def cancel_current_action(self):
        """Cancel the currently executing action."""
        self.get_logger().warn('Canceling current action')
        # Cancel active goal handles
```

---

## Execution Phase

1. Create the action server node
2. Create the VLA action client
3. Test with manual navigation goals
4. Connect to the LLM command parser from Lesson 3
5. Test the full voice → parse → validate → execute flow
6. Test action cancellation mid-execution

---

## Reflection

- How did action feedback improve the user experience?
- What happened when you canceled an action mid-execution?
- How would you handle multiple actions queued up?
