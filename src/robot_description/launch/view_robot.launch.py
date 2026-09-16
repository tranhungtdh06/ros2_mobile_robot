import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node

def generate_launch_description():
    pkg_path = get_package_share_directory('robot_description')
    xacro_file = os.path.join(pkg_path, 'urdf', 'robot.urdf.xacro')
    rviz_config_file = os.path.join(pkg_path, 'rviz', 'urdf_view.rviz')

    # Định nghĩa Argument từ Terminal
    drive_type_arg = DeclareLaunchArgument(
        'drive_type',
        default_value='mecanum',
        description='Type of drive: mecanum or diff'
    )

    # Dùng Command để chạy lệnh xacro, truyền argument vào file xacro
    robot_description_content = Command([
        'xacro ', xacro_file, ' drive_type:=', LaunchConfiguration('drive_type')
    ])

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description_content}]
    )

    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui'
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config_file],
    )

    return LaunchDescription([
        drive_type_arg,
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz_node
    ])