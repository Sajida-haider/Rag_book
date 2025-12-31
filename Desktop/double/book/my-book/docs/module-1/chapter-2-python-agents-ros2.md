---
sidebar_position: 2
---

# Chapter 2: Python Agents with ROS 2 (rclpy)

## Introduction to rclpy

The Robot Operating System 2 (ROS 2) Python client library (rclpy) provides Python bindings for ROS 2. It allows developers to create ROS 2 nodes in Python, enabling seamless integration between Python-based AI agents and robot control systems.

Python is an excellent choice for AI development due to its rich ecosystem of machine learning libraries (TensorFlow, PyTorch, scikit-learn) and ease of prototyping. By using rclpy, we can bridge the gap between sophisticated AI algorithms and real-world robot control.

## ROS 2 Node Lifecycle

Understanding the lifecycle of a ROS 2 node is crucial for creating robust and reliable robot applications. The lifecycle consists of several states and transitions:

### Primary States
- **Unconfigured**: The node has been created but not configured
- **Inactive**: The node is configured but not active
- **Active**: The node is running and participating in communication
- **Finalized**: The node has been shut down and cannot return to other states

### Lifecycle Management
Nodes can be managed through lifecycle services that allow transitions between states. This enables features like graceful startup, configuration updates, and controlled shutdown.

Example of a lifecycle node in Python:
```python
import rclpy
from rclpy.lifecycle import LifecycleNode
from rclpy.lifecycle import LifecycleState, TransitionCallbackReturn

class LifecycleMinimalPublisher(LifecycleNode):
    def __init__(self):
        super().__init__('lifecycle_talker')
        self.timer = None

    def on_configure(self, state):
        self.get_logger().info('on_configure() is called.')
        self.timer = self.create_timer(2, self.timer_callback)
        self.timer.cancel()
        return TransitionCallbackReturn.SUCCESS

    def on_activate(self, state):
        self.get_logger().info('on_activate() is called.')
        self.timer.reset()
        return TransitionCallbackReturn.SUCCESS

    def on_deactivate(self, state):
        self.get_logger().info('on_deactivate() is called.')
        self.timer.cancel()
        return TransitionCallbackReturn.SUCCESS

    def on_cleanup(self, state):
        self.get_logger().info('on_cleanup() is called.')
        self.destroy_timer(self.timer)
        self.timer = None
        return TransitionCallbackReturn.SUCCESS

    def timer_callback(self):
        self.get_logger().info('Lifecycle publisher: "Hello World"')
```

## Publishing and Subscribing using rclpy

### Creating a Publisher
A publisher node creates and sends messages to a topic. Here's how to create a publisher in Python:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello World: %d' % self.i
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)
        self.i += 1

def main(args=None):
    rclpy.init(args=args)
    minimal_publisher = MinimalPublisher()
    rclpy.spin(minimal_publisher)
    minimal_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Creating a Subscriber
A subscriber node receives messages from a topic. Here's how to create a subscriber in Python:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalSubscriber(Node):
    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            String,
            'topic',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info('I heard: "%s"' % msg.data)

def main(args=None):
    rclpy.init(args=args)
    minimal_subscriber = MinimalSubscriber()
    rclpy.spin(minimal_subscriber)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Services for Robot Commands

Services provide a request-response communication pattern that's ideal for robot commands that require a specific response.

### Creating a Service Server
```python
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts

class MinimalService(Node):
    def __init__(self):
        super().__init__('minimal_service')
        self.srv = self.create_service(AddTwoInts, 'add_two_ints', self.add_two_ints_callback)

    def add_two_ints_callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info('Incoming request\na: %d b: %d' % (request.a, request.b))
        return response

def main(args=None):
    rclpy.init(args=args)
    minimal_service = MinimalService()
    rclpy.spin(minimal_service)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Creating a Service Client
```python
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts

class MinimalClientAsync(Node):
    def __init__(self):
        super().__init__('minimal_client_async')
        self.cli = self.create_client(AddTwoInts, 'add_two_ints')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        self.req = AddTwoInts.Request()

    def send_request(self, a, b):
        self.req.a = a
        self.req.b = b
        self.future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()

def main():
    rclpy.init()
    minimal_client = MinimalClientAsync()
    response = minimal_client.send_request(1, 2)
    minimal_client.get_logger().info(
        'Result of add_two_ints: for %d + %d = %d' %
        (1, 2, response.sum))
    minimal_client.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Bridging AI Logic (Python Agents) to Robot Controllers

One of the most powerful aspects of ROS 2 is its ability to connect sophisticated AI algorithms to robot controllers. This section demonstrates how to bridge AI decision-making with robot control.

### Example: AI Agent Controlling a Robot Arm
```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
import numpy as np

class AIArmController(Node):
    def __init__(self):
        super().__init__('ai_arm_controller')

        # Subscribe to sensor data
        self.subscription = self.create_subscription(
            JointState,
            'joint_states',
            self.joint_state_callback,
            10)

        # Publisher for trajectory commands
        self.trajectory_publisher = self.create_publisher(
            JointTrajectory,
            'joint_trajectory',
            10)

        # Timer for AI decision making
        self.timer = self.create_timer(0.1, self.ai_decision_callback)

        self.current_joint_states = None

    def joint_state_callback(self, msg):
        self.current_joint_states = msg

    def ai_decision_callback(self):
        if self.current_joint_states is None:
            return

        # AI logic: determine desired joint positions
        # This could be a neural network, planning algorithm, etc.
        desired_positions = self.ai_planning_algorithm(
            self.current_joint_states.position
        )

        # Send trajectory command
        self.send_trajectory_command(desired_positions)

    def ai_planning_algorithm(self, current_positions):
        # Example: simple sinusoidal movement pattern
        # In practice, this could be a complex AI model
        time_step = self.get_clock().now().nanoseconds / 1e9
        new_positions = []
        for i, pos in enumerate(current_positions):
            # Create a simple oscillating pattern
            offset = 0.5 * np.sin(time_step + i)
            new_positions.append(pos + offset)
        return new_positions

    def send_trajectory_command(self, positions):
        trajectory_msg = JointTrajectory()
        trajectory_msg.joint_names = ['joint1', 'joint2', 'joint3']  # Example joint names

        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start.sec = 1  # Execute in 1 second

        trajectory_msg.points.append(point)
        self.trajectory_publisher.publish(trajectory_msg)

def main(args=None):
    rclpy.init(args=args)
    ai_controller = AIArmController()
    rclpy.spin(ai_controller)
    ai_controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Conceptual AI → ROS → Actuator Flow

The flow from AI decision-making to physical actuation involves several layers:

### 1. AI Layer
- Processes sensor data
- Makes high-level decisions
- Plans trajectories or actions
- Could be implemented with machine learning models, planners, etc.

### 2. ROS Middleware Layer
- Handles communication between AI and control layers
- Manages message passing and service calls
- Provides abstraction from hardware specifics

### 3. Control Layer
- Translates high-level commands to low-level control signals
- Implements control algorithms (PID, model predictive control, etc.)
- Interfaces with hardware drivers

### 4. Hardware Layer
- Physical actuators, motors, sensors
- Hardware abstraction layer (HAL)
- Real-time control systems

This layered architecture allows for modular development where each layer can be developed and tested independently.

## Best Practices for Python AI-ROS Integration

### Error Handling
Always implement proper error handling in your ROS 2 nodes:

```python
try:
    # AI processing
    result = ai_algorithm(sensor_data)
    # Publish result
    self.result_publisher.publish(result)
except Exception as e:
    self.get_logger().error(f'AI algorithm failed: {e}')
    # Implement fallback behavior
```

### Asynchronous Processing
For computationally expensive AI operations, consider using separate threads:

```python
import threading
from concurrent.futures import ThreadPoolExecutor

class AIProcessingNode(Node):
    def __init__(self):
        super().__init__('ai_processing_node')
        self.executor = ThreadPoolExecutor(max_workers=2)

    def sensor_callback(self, msg):
        # Submit AI processing to thread pool
        future = self.executor.submit(self.ai_process, msg)
        # Handle result when ready
        future.add_done_callback(self.ai_result_callback)
```

### Resource Management
Monitor and manage computational resources, especially important for AI models:

```python
import psutil
import time

def monitor_resources(self):
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent

    if cpu_percent > 90 or memory_percent > 90:
        self.get_logger().warn('High resource usage detected')
        # Implement resource management strategy
```

## Summary

This chapter demonstrated how to bridge Python AI agents with ROS 2 controllers using rclpy. We covered the ROS 2 node lifecycle, publishing and subscribing to topics, using services for robot commands, and creating a conceptual flow from AI decision-making to physical actuation.

The examples showed how to integrate AI algorithms with robot control systems, following best practices for error handling, asynchronous processing, and resource management. These patterns form the foundation for creating sophisticated AI-driven robotic systems.

In the next chapter, we'll explore how to describe humanoid robots using URDF (Unified Robot Description Format).