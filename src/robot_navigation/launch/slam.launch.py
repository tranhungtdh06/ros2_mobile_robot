import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    nav_pkg = get_package_share_directory('robot_navigation')
    slam_toolbox_pkg = get_package_share_directory('slam_toolbox')

    slam_params_file = os.path.join(nav_pkg, 'config', 'slam_toolbox.yaml')

    # Gọi file launch mặc định của slam_toolbox (chế độ online async)
    start_slam_toolbox = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(slam_toolbox_pkg, 'launch', 'online_async_launch.py')
        ),
        launch_arguments={
            'slam_params_file': slam_params_file,
            'use_sim_time': 'true'
        }.items()
    )

    return LaunchDescription([
        start_slam_toolbox
    ])