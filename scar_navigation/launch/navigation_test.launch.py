"""
navigation_test.launch.py
──────────────────────────────────────────────────────────
하드웨어 없이 소프트웨어 스택 전체 테스트용 런치 파일

fake_sensor_node 가 아래를 모두 대체:
  - /scan       (LaserScan)
  - /imu        (Imu)
  - /wheel_odom (Odometry)
  - /map        (OccupancyGrid)
  - map→odom TF (static)
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg        = get_package_share_directory('scar_navigation')
    nav2_params = os.path.join(pkg, 'config', 'nav2_params.yaml')
    ekf_params  = os.path.join(pkg, 'config', 'ekf.yaml')

    # ── 가짜 센서 (scan / imu / wheel_odom / map) ─────
    fake_sensor = Node(
        package='scar_navigation',
        executable='fake_sensor_node',
        name='fake_sensor_node',
        output='screen',
    )

    # ── 가짜 TF: map → odom ───────────────────────────
    fake_tf_map_odom = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='fake_tf_map_odom',
        arguments=['0', '0', '0', '0', '0', '0', 'map', 'odom'],
    )

    # ── EKF (wheel_odom + imu → /odom) ───────────────
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[ekf_params],
    )

    # ── Nav2 노드들 ───────────────────────────────────
    controller_server = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        parameters=[nav2_params],
    )

    planner_server = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        parameters=[nav2_params],
    )

    recoveries_server = Node(
        package='nav2_recoveries',
        executable='recoveries_server',
        name='recoveries_server',
        output='screen',
        parameters=[nav2_params],
    )

    bt_navigator = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        parameters=[nav2_params],
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[{
            'autostart': True,
            'node_names': [
                'controller_server',
                'planner_server',
                'recoveries_server',
                'bt_navigator',
            ]
        }]
    )

    return LaunchDescription([
        fake_tf_map_odom,     # TF 먼저
        fake_sensor,          # 가짜 센서
        ekf_node,             # EKF
        controller_server,
        planner_server,
        recoveries_server,
        bt_navigator,
        lifecycle_manager,
    ])
