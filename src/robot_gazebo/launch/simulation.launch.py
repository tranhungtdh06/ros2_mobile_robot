import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node

def generate_launch_description():
    gazebo_pkg = get_package_share_directory('robot_gazebo')
    desc_pkg = get_package_share_directory('robot_description')
    ros_gz_sim_pkg = get_package_share_directory('ros_gz_sim') # Đổi sang ros_gz_sim

    world_file = os.path.join(gazebo_pkg, 'worlds', 'maze.world')
    xacro_file = os.path.join(desc_pkg, 'urdf', 'robot.urdf.xacro')

    drive_type = LaunchConfiguration('drive_type')
    drive_type_arg = DeclareLaunchArgument('drive_type', default_value='mecanum')

    robot_description_content = Command(['xacro ', xacro_file, ' drive_type:=', drive_type])
    
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description_content, 'use_sim_time': True}]
    )

    # Chạy Gazebo Harmonic
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_pkg, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r {world_file}'}.items()
    )

    # Spawn Robot vào Gazebo Harmonic
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'autonomous_bot',
            '-z', '0.1'
        ],
        output='screen'
    )
    # Cấu hình cầu nối giữa ROS 2 và Gazebo
    bridge_params = os.path.join(
        get_package_share_directory('robot_gazebo'),
        'config',
        'gz_bridge.yaml'
    )
    
    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/imu/data@sensor_msgs/msg/Imu[gz.msgs.IMU',
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V'
        ],
        output='screen'
    )

    return LaunchDescription([
        drive_type_arg,
        robot_state_publisher,
        gazebo,
        spawn_robot,
        ros_gz_bridge
    ])