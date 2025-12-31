---
sidebar_position: 3
---

# Chapter 3: Humanoid Robot Description with URDF

## Introduction to URDF

Unified Robot Description Format (URDF) is an XML-based format used in ROS to describe robot models. It defines the physical and visual properties of a robot, including its links (rigid parts), joints (connections between links), and other components like sensors and actuators.

URDF is essential for humanoid robotics as it provides a standardized way to describe the complex kinematic structure of humanoid robots, enabling simulation, visualization, and control.

## Purpose of URDF

URDF serves several critical purposes in robotics:

### 1. Kinematic Description
URDF defines the kinematic chain of a robot, describing how different parts are connected and how they move relative to each other. This is crucial for forward and inverse kinematics calculations.

### 2. Simulation Preparation
URDF models are used by physics simulators like Gazebo to create realistic robot simulations. The physical properties defined in URDF determine how the robot behaves in simulation.

### 3. Visualization
URDF models are used by visualization tools like RViz to display robots in a 3D environment, allowing developers to verify robot configurations and visualize motion.

### 4. Control System Integration
URDF provides the necessary information for control systems to understand the robot's structure and properly command its joints.

## Links, Joints, and Kinematic Structure

### Links
Links represent rigid bodies in the robot. Each link has:
- **Visual**: How the link appears in visualization
- **Collision**: How the link interacts in collision detection
- **Inertial**: Physical properties like mass and moment of inertia

Example of a link definition:
```xml
<link name="base_link">
  <visual>
    <geometry>
      <cylinder length="0.6" radius="0.2"/>
    </geometry>
    <material name="blue">
      <color rgba="0 0 0.8 1"/>
    </material>
  </visual>
  <collision>
    <geometry>
      <cylinder length="0.6" radius="0.2"/>
    </geometry>
  </collision>
  <inertial>
    <mass value="10"/>
    <inertia ixx="1.0" ixy="0.0" ixz="0.0" iyy="1.0" iyz="0.0" izz="1.0"/>
  </inertial>
</link>
```

### Joints
Joints connect links and define their relative motion. The main joint types are:
- **Fixed**: No movement between links
- **Revolute**: Rotational movement around an axis
- **Continuous**: Like revolute but unlimited rotation
- **Prismatic**: Linear sliding movement
- **Floating**: 6 degrees of freedom
- **Planar**: Movement in a plane

Example of a joint definition:
```xml
<joint name="base_to_wheel" type="continuous">
  <parent link="base_link"/>
  <child link="wheel_link"/>
  <origin xyz="0 0.2 0" rpy="0 0 0"/>
  <axis xyz="0 1 0"/>
</joint>
```

### Kinematic Structure
The kinematic structure defines the tree of links and joints. For humanoid robots, this typically includes:
- Torso as the base
- Arms with shoulder, elbow, and wrist joints
- Legs with hip, knee, and ankle joints
- Head with neck joints

## Visual and Collision Elements

### Visual Elements
Visual elements define how a link appears in visualization tools:

```xml
<visual>
  <origin xyz="0 0 0" rpy="0 0 0"/>
  <geometry>
    <box size="1 0.2 0.1"/>
    <!-- or <cylinder radius="0.1" length="0.5"/> -->
    <!-- or <sphere radius="0.1"/> -->
    <!-- or <mesh filename="package://robot_description/meshes/link.stl"/> -->
  </geometry>
  <material name="red">
    <color rgba="0.8 0 0 1"/>
  </material>
</visual>
```

### Collision Elements
Collision elements define how a link interacts in collision detection:

```xml
<collision>
  <origin xyz="0 0 0" rpy="0 0 0"/>
  <geometry>
    <box size="1 0.2 0.1"/>
    <!-- Simplified geometry often used for collision detection -->
  </geometry>
</collision>
```

## How URDF Enables Simulation and Control

### Simulation in Gazebo
URDF models are converted to SDF (Simulation Description Format) for use in Gazebo. The physical properties defined in URDF determine how the robot behaves in simulation:

```xml
<gazebo reference="link_name">
  <material>Gazebo/Blue</material>
  <mu1>0.2</mu1>
  <mu2>0.2</mu2>
  <kp>1000000.0</kp>
  <kd>100.0</kd>
</gazebo>
```

### Control Integration
URDF provides joint names and limits that control systems use:

```xml
<joint name="shoulder_joint" type="revolute">
  <parent link="torso"/>
  <child link="upper_arm"/>
  <origin xyz="0 0.1 0.3" rpy="0 0 0"/>
  <axis xyz="0 1 0"/>
  <limit lower="-2.0" upper="1.0" effort="30" velocity="1.0"/>
  <safety_controller k_position="30" k_velocity="500"
                     soft_lower_limit="-1.9" soft_upper_limit="0.9"/>
</joint>
```

## Preparing Humanoid Models for Simulators

### Complete Humanoid URDF Example
Here's a simplified example of a humanoid robot torso:

```xml
<?xml version="1.0"?>
<robot name="simple_humanoid">
  <!-- Torso -->
  <link name="torso">
    <visual>
      <geometry>
        <box size="0.3 0.2 0.6"/>
      </geometry>
      <material name="white">
        <color rgba="1 1 1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.3 0.2 0.6"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="10"/>
      <inertia ixx="0.5" ixy="0" ixz="0" iyy="0.5" iyz="0" izz="0.5"/>
    </inertial>
  </link>

  <!-- Head -->
  <link name="head">
    <visual>
      <geometry>
        <sphere radius="0.1"/>
      </geometry>
      <material name="skin">
        <color rgba="0.8 0.6 0.4 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <sphere radius="0.1"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="2"/>
      <inertia ixx="0.02" ixy="0" ixz="0" iyy="0.02" iyz="0" izz="0.02"/>
    </inertial>
  </link>

  <!-- Neck joint -->
  <joint name="neck_joint" type="revolute">
    <parent link="torso"/>
    <child link="head"/>
    <origin xyz="0 0 0.35" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-0.5" upper="0.5" effort="5" velocity="2"/>
  </joint>

  <!-- Left shoulder -->
  <link name="left_upper_arm">
    <visual>
      <geometry>
        <cylinder length="0.4" radius="0.05"/>
      </geometry>
      <material name="white"/>
    </visual>
    <collision>
      <geometry>
        <cylinder length="0.4" radius="0.05"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/>
    </inertial>
  </link>

  <!-- Left shoulder joint -->
  <joint name="left_shoulder_joint" type="revolute">
    <parent link="torso"/>
    <child link="left_upper_arm"/>
    <origin xyz="0.2 0 0.2" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" effort="10" velocity="2"/>
  </joint>
</robot>
```

### URDF Best Practices for Humanoid Robots

1. **Proper Mass Distribution**: Ensure each link has realistic mass and inertia values
2. **Joint Limits**: Define appropriate limits based on human anatomy or robot design
3. **Collision Avoidance**: Design joint limits to prevent self-collision
4. **Consistent Naming**: Use consistent naming conventions for joints and links
5. **Reference Frames**: Establish clear reference frames for each link

## Working with URDF in ROS 2

### Loading URDF in ROS 2
URDF files are typically loaded using the robot_state_publisher node:

```bash
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:='$(find-pkg-share my_robot_description)/urdf/my_robot.urdf'
```

### URDF with Xacro
For complex humanoid robots, Xacro (XML Macros) is often used to simplify URDF:

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="humanoid_with_xacro">
  <xacro:property name="M_PI" value="3.1415926535897931" />

  <xacro:macro name="simple_arm" params="prefix parent_link">
    <link name="${prefix}_upper_arm">
      <visual>
        <geometry>
          <cylinder length="0.4" radius="0.05"/>
        </geometry>
      </visual>
      <collision>
        <geometry>
          <cylinder length="0.4" radius="0.05"/>
        </geometry>
      </collision>
      <inertial>
        <mass value="1"/>
        <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/>
      </inertial>
    </link>
  </xacro:macro>

  <xacro:simple_arm prefix="left" parent_link="torso"/>
  <xacro:simple_arm prefix="right" parent_link="torso"/>
</robot>
```

## Tools for Working with URDF

### rviz2
Visualize your URDF model in RViz2:
```bash
ros2 run rviz2 rviz2
```
Add a RobotModel display and set the Robot Description to your URDF topic.

### check_urdf
Check your URDF for errors:
```bash
check_urdf /path/to/robot.urdf
```

### urdf_to_graphiz
Visualize the kinematic tree:
```bash
urdf_to_graphiz /path/to/robot.urdf
```

## Summary

This chapter covered the essential aspects of URDF for humanoid robot modeling. We explored how links and joints define the kinematic structure, how visual and collision elements enable simulation and visualization, and how URDF facilitates both simulation and control.

We examined how URDF models are prepared for simulators like Gazebo and discussed best practices for creating humanoid robot descriptions. The examples demonstrated practical applications of URDF in real robotic systems.

Understanding URDF is crucial for working with humanoid robots as it provides the foundation for simulation, visualization, and control. The standardized format enables consistent development across different robotic platforms and tools.

With this knowledge of ROS 2 fundamentals, Python AI integration, and URDF robot description, you now have the foundational understanding needed to work with humanoid robots in the Physical AI context.