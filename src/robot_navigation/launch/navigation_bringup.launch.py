import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess, RegisterEventHandler, TimerAction
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    gazebo_pkg = get_package_share_directory('robot_gazebo')
    nav_pkg = get_package_share_directory('robot_navigation')
    nav2_bringup_pkg = get_package_share_directory('nav2_bringup')

    # Chỉ định đường dẫn tới Bản đồ tĩnh và File cấu hình
    map_file = os.path.join(nav_pkg, 'maps', 'final_maze_map.yaml')
    nav2_params_file = os.path.join(nav_pkg, 'config', 'nav2_params.yaml')

    # 1. Khởi động Môi trường mô phỏng (Gazebo)
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(gazebo_pkg, 'launch', 'simulation.launch.py')),
        launch_arguments={'drive_type': 'mecanum'}.items() # Đảm bảo đúng loại truyền động của bạn
    )

    # 2. Khởi động EKF (Sensor Fusion)
    ekf_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav_pkg, 'launch', 'localization.launch.py'))
    )

    # 3. Khởi động Nav2 (AMCL + Navigation)
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2_bringup_pkg, 'launch', 'bringup_launch.py')),
        launch_arguments={
            'use_sim_time': 'true',
            'map': map_file,
            'params_file': nav2_params_file
        }.items()
    )

    # 4. Trình xử lý sự kiện: Đợi Gazebo load xong clock mới bung các thuật toán
    wait_for_clock = ExecuteProcess(
        cmd=['ros2', 'topic', 'echo', '--once', '/clock'],
        output='log'
    )

    start_nodes_event = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=wait_for_clock,
            on_exit=[ekf_launch, TimerAction(period=3.0, actions=[nav2_launch])]
        )
    )

    return LaunchDescription([
        gazebo_launch,
        wait_for_clock,
        start_nodes_event
    ])