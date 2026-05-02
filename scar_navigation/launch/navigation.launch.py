import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('scar_navigation')
    nav2_params = os.path.join(pkg, 'config', 'nav2_params.yaml')
    ekf_params  = os.path.join(pkg, 'config', 'ekf.yaml')

    # ── 휠 오도메트리 노드 ─────────────────────────────────
    wheel_odom = Node(
        package='scar_navigation',
        executable='wheel_odom_node',
        name='wheel_odom_node',
        output='screen',
    )

    # ── EKF 융합 노드 (휠 오도메트리 + IMU → /odom) ────────
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[ekf_params],
    )

    # ── controller_server ──────────────────────────────────
    controller_server = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        parameters=[nav2_params],
    )

    # ── planner_server ─────────────────────────────────────
    planner_server = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        parameters=[nav2_params],
    )

    # ── recoveries_server ──────────────────────────────────
    recoveries_server = Node(
        package='nav2_recoveries',
        executable='recoveries_server',
        name='recoveries_server',
        output='screen',
        parameters=[nav2_params],
    )

    # ── bt_navigator ───────────────────────────────────────
    bt_navigator = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        parameters=[nav2_params],
    )

    # ── lifecycle_manager ──────────────────────────────────
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
        wheel_odom,
        ekf_node,
        controller_server,
        planner_server,
        recoveries_server,
        bt_navigator,
        lifecycle_manager,
    ])

