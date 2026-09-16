import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    nav_pkg = get_package_share_directory('robot_navigation')
    ekf_config_path = os.path.join(nav_pkg, 'config', 'ekf.yaml')

    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[
            ekf_config_path, 
            {'use_sim_time': True}  # <-- THÊM DÒNG NÀY ĐỂ ÉP NODE DÙNG CLOCK ẢO
        ]
    )

    return LaunchDescription([
        ekf_node
    ])