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

    # 1. Định nghĩa các cục Launch
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(gazebo_pkg, 'launch', 'simulation.launch.py')),
        launch_arguments={'drive_type': 'mecanum'}.items()
    )

    ekf_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav_pkg, 'launch', 'localization.launch.py'))
    )

    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav_pkg, 'launch', 'slam.launch.py'))
    )

    nav2_params_file = os.path.join(nav_pkg, 'config', 'nav2_params.yaml')

    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2_bringup_pkg, 'launch', 'navigation_launch.py')),
        launch_arguments={
            'use_sim_time': 'true',
            'params_file': nav2_params_file  # <-- TRUYỀN FILE CẤU HÌNH VÀO ĐÂY
        }.items()
    )
    # ---------------------------------------------------------
    # HỆ THỐNG XỬ LÝ SỰ KIỆN (EVENT HANDLERS)
    # ---------------------------------------------------------

    # BƯỚC A: Lệnh thăm dò - Lắng nghe 1 tin nhắn duy nhất từ topic /clock rồi tự thoát
    wait_for_clock = ExecuteProcess(
        cmd=['ros2', 'topic', 'echo', '--once', '/clock'],
        output='log'
    )

    # BƯỚC B: Sự kiện - KHI Lệnh thăm dò hoàn thành (OnProcessExit) -> Chạy EKF và SLAM
    start_ekf_and_slam_event = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=wait_for_clock,
            on_exit=[ekf_launch, slam_launch]
        )
    )

    # BƯỚC C: Sự kiện cho Nav2.
    # Vì việc thăm dò cây TF (odom -> base_link) bằng lệnh CLI phức tạp hơn, 
    # và Nav2 có Lifecycle Manager riêng, ta có thể dùng Timer ngắn tính từ lúc EKF mở.
    start_nav2_event = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=wait_for_clock,
            on_exit=[TimerAction(period=3.0, actions=[nav2_launch])]
        )
    )

    return LaunchDescription([
        gazebo_launch,
        wait_for_clock,
        start_ekf_and_slam_event,
        start_nav2_event
    ])