#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <tf2/LinearMath/Quaternion.h>
#include <fcntl.h>
#include <termios.h>
#include <unistd.h>

class MotorBridgeNode : public rclcpp::Node {
public:
    MotorBridgeNode() : Node("motor_bridge_node"), x_(0.0), y_(0.0), th_(0.0) {
        this->declare_parameter("serial_port", "/dev/ttyACM0");
        std::string port = this->get_parameter("serial_port").as_string();
        
        if (!init_serial(port)) {
            RCLCPP_ERROR(this->get_logger(), "Không thể kết nối MCU tại %s", port.c_str());
            rclcpp::shutdown();
        }

        cmd_vel_sub_ = this->create_subscription<geometry_msgs::msg::Twist>(
            "/cmd_vel", 10, std::bind(&MotorBridgeNode::cmd_vel_callback, this, std::placeholders::_1));
        odom_pub_ = this->create_publisher<nav_msgs::msg::Odometry>("/odom", 50);
        timer_ = this->create_wall_timer(std::chrono::milliseconds(20), std::bind(&MotorBridgeNode::read_mcu_callback, this));
        last_time_ = this->get_clock()->now();
    }
    ~MotorBridgeNode() { if (serial_fd_ >= 0) close(serial_fd_); }

private:
    int serial_fd_;
    double x_, y_, th_;
    rclcpp::Time last_time_;
    std::string serial_buffer_;
    rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_sub_;
    rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_pub_;
    rclcpp::TimerBase::SharedPtr timer_;

    bool init_serial(const std::string& port) {
        serial_fd_ = open(port.c_str(), O_RDWR | O_NOCTTY | O_NONBLOCK);
        if (serial_fd_ < 0) return false;
        struct termios tty;
        if (tcgetattr(serial_fd_, &tty) != 0) return false;
        cfsetospeed(&tty, B115200);
        cfsetispeed(&tty, B115200);
        tty.c_cflag |= (CLOCAL | CREAD | CS8);
        tty.c_cflag &= ~(CSIZE | PARENB | CSTOPB | CRTSCTS);
        tty.c_iflag &= ~(IGNBRK | BRKINT | PARMRK | ISTRIP | INLCR | IGNCR | ICRNL | IXON);
        tty.c_lflag &= ~(ECHO | ECHONL | ICANON | ISIG | IEXTEN);
        tty.c_oflag &= ~OPOST;
        tty.c_cc[VMIN] = 0;
        tty.c_cc[VTIME] = 1;
        return tcsetattr(serial_fd_, TCSANOW, &tty) == 0;
    }

    void cmd_vel_callback(const geometry_msgs::msg::Twist::SharedPtr msg) {
        char buffer[64];
        snprintf(buffer, sizeof(buffer), "%.3f,%.3f,%.3f\n", msg->linear.x, msg->linear.y, msg->angular.z);
        write(serial_fd_, buffer, strlen(buffer));
    }

    void read_mcu_callback() {
        char buf[256];
        int n = read(serial_fd_, buf, sizeof(buf) - 1);
        if (n > 0) {
            buf[n] = '\0';
            serial_buffer_ += buf;
            size_t pos;
            while ((pos = serial_buffer_.find('\n')) != std::string::npos) {
                std::string line = serial_buffer_.substr(0, pos);
                serial_buffer_.erase(0, pos + 1);
                double vx = 0.0, vy = 0.0, vth = 0.0;
                if (sscanf(line.c_str(), "%lf,%lf,%lf", &vx, &vy, &vth) == 3) {
                    publish_odometry(vx, vy, vth);
                }
            }
        }
    }

    void publish_odometry(double vx, double vy, double vth) {
        rclcpp::Time current_time = this->get_clock()->now();
        double dt = (current_time - last_time_).seconds();
        x_ += (vx * cos(th_) - vy * sin(th_)) * dt;
        y_ += (vx * sin(th_) + vy * cos(th_)) * dt;
        th_ += vth * dt;
        last_time_ = current_time;

        auto odom = nav_msgs::msg::Odometry();
        odom.header.stamp = current_time;
        odom.header.frame_id = "odom";            
        odom.child_frame_id = "base_footprint";   
        odom.pose.pose.position.x = x_;
        odom.pose.pose.position.y = y_;
        tf2::Quaternion q;
        q.setRPY(0, 0, th_);
        odom.pose.pose.orientation.x = q.x();
        odom.pose.pose.orientation.y = q.y();
        odom.pose.pose.orientation.z = q.z();
        odom.pose.pose.orientation.w = q.w();
        odom.twist.twist.linear.x = vx;
        odom.twist.twist.linear.y = vy;
        odom.twist.twist.angular.z = vth;
        odom_pub_->publish(odom);
    }
};

int main(int argc, char **argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<MotorBridgeNode>());
    rclcpp::shutdown();
    return 0;
}