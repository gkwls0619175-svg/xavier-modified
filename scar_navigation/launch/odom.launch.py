import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('scar_navigation')
    ekf_params = os.path.join(pkg, 'config', 'ekf.yaml')

    # 오도메트리만 단독 테스트할 때 사용
    wheel_odom = Node(
        package='scar_navigation',
        executable='wheel_odom_node',
        name='wheel_odom_node',
        output='screen',
    )

    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[ekf_params],
    )

    return LaunchDescription([
        wheel_odom,
        ekf_node,
    ])

