import rclpy
import math
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
from dynamixel_sdk import PortHandler, PacketHandler, COMM_SUCCESS


class WheelOdomNode(Node):
    def __init__(self):
        super().__init__('wheel_odom_node')

        # ── SCAR 치수 (실측값으로 수정) ──────────────────
        self.WHEEL_RADIUS = 0.12      # 바퀴 반지름 (m)
        self.WHEEL_BASE   = 0.30      # 좌우 바퀴 간 거리 (m)

        # ── Dynamixel 설정 ────────────────────────────────
        self.port_handler   = PortHandler('/dev/ttyUSB0')
        self.packet_handler = PacketHandler(2.0)

        # 4륜 Dynamixel ID (실제 ID로 수정)
        #   [FRONT_LEFT]  [FRONT_RIGHT]
        #   [REAR_LEFT ]  [REAR_RIGHT ]
        self.FRONT_LEFT_ID  = 3
        self.FRONT_RIGHT_ID = 1
        self.REAR_LEFT_ID   = 7
        self.REAR_RIGHT_ID  = 5

        # Dynamixel Present Velocity 주소 (Protocol 2.0 XSeries)
        self.PRESENT_VELOCITY_ADDR = 128
        self.PRESENT_VELOCITY_LEN  = 4

        # 하드웨어 연결 시도 — 실패해도 노드는 계속 실행
        self.hardware_connected = False
        try:
            if not self.port_handler.openPort():
                self.get_logger().warn('Dynamixel 포트 열기 실패 — 소프트웨어 테스트 모드')
            elif not self.port_handler.setBaudRate(57600):
                self.get_logger().warn('Baudrate 설정 실패 — 소프트웨어 테스트 모드')
            else:
                self.hardware_connected = True
                self.get_logger().info('Dynamixel 연결 성공 — 실제 하드웨어 모드')
        except Exception as e:
            self.get_logger().warn(f'Dynamixel 초기화 실패: {e} — 소프트웨어 테스트 모드')

        # ── 상태 변수 ─────────────────────────────────────
        self.x     = 0.0
        self.y     = 0.0
        self.theta = 0.0
        self.last_time = self.get_clock().now()

        # ── 발행 ─────────────────────────────────────────
        self.odom_pub       = self.create_publisher(Odometry, '/wheel_odom', 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        # ── 타이머 20Hz ───────────────────────────────────
        self.create_timer(0.05, self.timer_callback)
        self.get_logger().info('wheel_odom_node 시작 (4륜)')

    def read_velocity(self, dxl_id):
        # 하드웨어 없으면 0 반환
        if not self.hardware_connected:
            return 0.0

        try:
            val, result, _ = self.packet_handler.read4ByteTxRx(
                self.port_handler, dxl_id, self.PRESENT_VELOCITY_ADDR)
        except Exception:
            return 0.0

        if result != COMM_SUCCESS:
            return 0.0

        # 부호 있는 32비트 정수 변환
        if val > 0x7FFFFFFF:
            val -= 0x100000000

        # 0.229 RPM/unit → rad/s 변환
        return val * 0.229 * 2.0 * math.pi / 60.0

    def timer_callback(self):
        now = self.get_clock().now()
        dt  = (now - self.last_time).nanoseconds / 1e9
        self.last_time = now

        # ── 4륜 바퀴 속도 읽기 (rad/s) ───────────────────
        v_front_left  = self.read_velocity(self.FRONT_LEFT_ID)
        v_front_right = self.read_velocity(self.FRONT_RIGHT_ID)
        v_rear_left   = self.read_velocity(self.REAR_LEFT_ID)
        v_rear_right  = self.read_velocity(self.REAR_RIGHT_ID)

        # ── 왼쪽/오른쪽 평균 속도 (m/s) ──────────────────
        vl = ((v_front_left  + v_rear_left)  / 2.0) * self.WHEEL_RADIUS
        vr = ((v_front_right + v_rear_right) / 2.0) * self.WHEEL_RADIUS

        # ── 차동 구동 계산 ────────────────────────────────
        v     = (vr + vl) / 2.0
        omega = (vr - vl) / self.WHEEL_BASE

        # ── 위치 적분 ─────────────────────────────────────
        self.x     += v * math.cos(self.theta) * dt
        self.y     += v * math.sin(self.theta) * dt
        self.theta += omega * dt

        # ── /wheel_odom 발행 ──────────────────────────────
        odom = Odometry()
        odom.header.stamp    = now.to_msg()
        odom.header.frame_id = 'odom'
        odom.child_frame_id  = 'base_link'

        odom.pose.pose.position.x    = self.x
        odom.pose.pose.position.y    = self.y
        odom.pose.pose.orientation.z = math.sin(self.theta / 2.0)
        odom.pose.pose.orientation.w = math.cos(self.theta / 2.0)

        odom.twist.twist.linear.x  = v
        odom.twist.twist.angular.z = omega

        odom.pose.covariance[0]  = 0.01
        odom.pose.covariance[7]  = 0.01
        odom.pose.covariance[35] = 0.01
        odom.twist.covariance[0]  = 0.01
        odom.twist.covariance[35] = 0.01

        self.odom_pub.publish(odom)

    def destroy_node(self):
        if self.hardware_connected:
            self.port_handler.closePort()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = WheelOdomNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
