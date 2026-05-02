import rclpy
import math
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, Imu
from nav_msgs.msg import Odometry, OccupancyGrid
from std_msgs.msg import Header


class FakeSensorNode(Node):
    def __init__(self):
        super().__init__('fake_sensor_node')

        self.scan_pub  = self.create_publisher(LaserScan,     '/scan',       10)
        self.imu_pub   = self.create_publisher(Imu,           '/imu',        10)
        self.odom_pub  = self.create_publisher(Odometry,      '/wheel_odom', 10)
        self.map_pub   = self.create_publisher(OccupancyGrid, '/map',        10)

        self.create_timer(0.10, self.publish_scan)   # 10Hz
        self.create_timer(0.05, self.publish_imu)    # 20Hz
        self.create_timer(0.05, self.publish_odom)   # 20Hz
        self.create_timer(1.00, self.publish_map)    # 1Hz

        self.get_logger().info('가짜 센서 노드 시작 (scan / imu / wheel_odom / map)')

    def publish_scan(self):
        msg = LaserScan()
        msg.header.stamp    = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'
        msg.angle_min       = -math.pi
        msg.angle_max       =  math.pi
        msg.angle_increment = math.pi / 180.0
        msg.range_min       = 0.1
        msg.range_max       = 10.0
        msg.ranges          = [5.0] * 360
        self.scan_pub.publish(msg)

    def publish_imu(self):
        msg = Imu()
        msg.header.stamp    = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'
        msg.orientation.w   = 1.0
        msg.orientation.x   = 0.0
        msg.orientation.y   = 0.0
        msg.orientation.z   = 0.0
        msg.angular_velocity.x    = 0.0
        msg.angular_velocity.y    = 0.0
        msg.angular_velocity.z    = 0.0
        msg.linear_acceleration.x = 0.0
        msg.linear_acceleration.y = 0.0
        msg.linear_acceleration.z = 9.81
        # 9칸 공분산 배열 초기화
        msg.orientation_covariance         = [0.01, 0.0, 0.0, 0.0, 0.01, 0.0, 0.0, 0.0, 0.01]
        msg.angular_velocity_covariance    = [0.01, 0.0, 0.0, 0.0, 0.01, 0.0, 0.0, 0.0, 0.01]
        msg.linear_acceleration_covariance = [0.01, 0.0, 0.0, 0.0, 0.01, 0.0, 0.0, 0.0, 0.01]
        self.imu_pub.publish(msg)

    def publish_odom(self):
        msg = Odometry()
        msg.header.stamp        = self.get_clock().now().to_msg()
        msg.header.frame_id     = 'odom'
        msg.child_frame_id      = 'base_link'
        msg.pose.pose.orientation.w = 1.0
        msg.twist.twist.linear.x    = 0.0
        msg.pose.covariance[0]      = 0.01
        msg.pose.covariance[7]      = 0.01
        msg.pose.covariance[35]     = 0.01
        msg.twist.covariance[0]     = 0.01
        msg.twist.covariance[35]    = 0.01
        self.odom_pub.publish(msg)

    def publish_map(self):
        # 200x200 셀, 해상도 0.05m → 10m x 10m 빈 맵
        width  = 200
        height = 200
        msg = OccupancyGrid()
        msg.header.stamp    = self.get_clock().now().to_msg()
        msg.header.frame_id = 'map'
        msg.info.resolution = 0.05
        msg.info.width      = width
        msg.info.height     = height
        msg.info.origin.position.x = -5.0
        msg.info.origin.position.y = -5.0
        msg.info.origin.orientation.w = 1.0
        msg.data = [0] * (width * height)   # 0 = free
        self.map_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(FakeSensorNode())
    rclpy.shutdown()
