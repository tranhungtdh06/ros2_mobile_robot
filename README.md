# ROS 2 Mobile Robot Project

Dự án phát triển robot tự hành (Autonomous Mobile Robot) sử dụng ROS 2, mô phỏng trên Gazebo Harmonic và tích hợp hệ thống điều hướng Nav2 & SLAM. Robot hỗ trợ khả năng thay đổi cấu hình truyền động linh hoạt (Mecanum / Differential Drive).

## 1. Yêu cầu hệ thống (Prerequisites)
- Hệ điều hành: Ubuntu 22.04 / 24.04 (tương ứng ROS 2 Humble / Jazzy).
- Trình mô phỏng: Gazebo Harmonic (`ros_gz_sim`).
- Các gói ROS 2 cần thiết: `nav2_bringup`, `slam_toolbox`, `robot_localization`, `xacro`, `teleop_twist_keyboard`.

## 2. Biên dịch dự án (Build)
Mở terminal và di chuyển vào thư mục workspace, sau đó chạy lệnh build:

```bash
cd ~/mobile_bot_ws
colcon build --symlink-install

# ==========================================
# ALIAS CHO PROJECT ROS2 MOBILE ROBOT
# ==========================================
# Cập nhật workspace
alias build_bot="cd ~/mobile_bot_ws && colcon build --symlink-install && source install/setup.bash"
alias source_bot="source ~/mobile_bot_ws/install/setup.bash"

# Khởi chạy các chức năng
alias view_bot="ros2 launch robot_description view_robot.launch.py"
alias map_bot="ros2 launch robot_navigation mapping_bringup.launch.py"
alias nav_bot="ros2 launch robot_navigation navigation_bringup.launch.py"

# Công cụ hỗ trợ
alias run_teleop="ros2 run teleop_twist_keyboard teleop_twist_keyboard"
alias open_rviz_nav="ros2 launch nav2_bringup rviz_launch.py use_sim_time:=true"

# lưu map
ros2 run nav2_map_server map_saver_cli -f ~/mobile_bot_ws/src/robot_navigation/maps/my_new_map --ros-args -p use_sim_time:=true
## 4. Danh sách Phím tắt (Alias) để thao tác nhanh
Để không phải gõ các câu lệnh dài, dự án hỗ trợ các alias sau (Cần được cấu hình trong `~/.bashrc`):

- `build_bot`: Dùng để build lại toàn bộ project và source workspace.
- `source_bot`: Nạp lại workspace cho terminal mới.
- `view_bot`: Mở nhanh mô hình 3D của robot trên RViz (Test 1).
- `map_bot`: Bật chế độ SLAM quét bản đồ (Test 2).
- `nav_bot`: Bật chế độ Tự hành Nav2 (Test 3).
- `run_teleop`: Mở bàn phím điều khiển robot.
- `open_rviz_nav`: Bật màn hình hiển thị RViz dành riêng cho chế độ SLAM hoặc Navigation.

## 5. Quy trình Chạy & Hiển thị RViz tiêu chuẩn

Vì môi trường mô phỏng (Gazebo) và giao diện hiển thị (RViz) chạy tách biệt để tối ưu hiệu suất, dưới đây là quy trình 3 bước chuẩn để khởi động hệ thống:

**Khi muốn chạy SLAM (Quét bản đồ):**
- **Terminal 1:** Gõ `map_bot` (Chờ Gazebo bật lên và load mô hình).
- **Terminal 2:** Gõ `open_rviz_nav` (Để mở giao diện xem bản đồ đang quét).
- **Terminal 3:** Gõ `run_teleop` (Để lái robot).
*Lưu ý: Nếu RViz không hiển thị map, hãy bấm "Play" dưới góc trái phần mềm Gazebo để thời gian mô phỏng bắt đầu chạy.*

**Khi muốn chạy Tự hành (Navigation):**
- **Terminal 1:** Gõ `nav_bot` (Khởi động hệ thống dẫn đường với bản đồ có sẵn).
- **Terminal 2:** Gõ `open_rviz_nav` (Mở giao diện giám sát Nav2).
*Thao tác trên RViz:* 
1. Dùng công cụ `2D Pose Estimate` trên thanh công cụ để cung cấp vị trí ban đầu cho robot.
2. Dùng công cụ `Nav2 Goal` để chỉ định điểm đến. Robot sẽ tự động di chuyển trong Gazebo và RViz.