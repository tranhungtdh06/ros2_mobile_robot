import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node

def generate_launch_description():
    desc_pkg = get_package_share_directory('robot_description')
    hardware_pkg = get_package_share_directory('robot_hardware')

    xacro_file = os.path.join(desc_pkg, 'urdf', 'robot.urdf.xacro')
    
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': Command(['xacro ', xacro_file, ' drive_type:=', LaunchConfiguration('drive_type')]), 
            'use_sim_time': False
        }]
    )

    lidar_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(hardware_pkg, 'launch', 'rplidar.launch.py'))
    )

    motor_node = Node(
        package='robot_hardware',
        executable='motor_bridge_node',
        output='screen',
        parameters=[{'serial_port': '/dev/ttyACM0', 'baudrate': 115200}]
    )

    return LaunchDescription([
        DeclareLaunchArgument('drive_type', default_value='mecanum'),
        robot_state_publisher,
        lidar_launch,
        motor_node
    ])