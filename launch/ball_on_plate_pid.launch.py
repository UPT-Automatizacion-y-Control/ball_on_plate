import os
from launch import LaunchDescription
from launch_ros.actions import Node

DELAY_TIME = 1/120

def generate_launch_description():

    control_node = Node(
        package='ball_on_plate', executable='ball_control_node', name='ball_control', output='screen',
        parameters=[{'delay_time': DELAY_TIME}], remappings=[('ball_e', 'ball_e'), ('user_goal', 'user_goal')])

    error_node = Node(
        package='ball_on_plate', executable='ball_error_node', name='ball_error', output='screen',
        parameters=[{'delay_time': DELAY_TIME}], remappings=[('ball_f', 'ball_f'), ('ball_r', 'ball_r'), ('ball_e', 'ball_e')])

    filter_node = Node(
        package='ball_on_plate', executable='ball_filter_node', name='ball_filter', output='screen',
        parameters=[{'ball_filter.params.number_of_observations': 50}], remappings=[('ball_p', 'ball_p'), ('ball_f', 'ball_f')])

    reference_node = Node(
        package='ball_on_plate', executable='ball_reference_node', name='ball_reference', output='screen',
        parameters=[{'delay_time': DELAY_TIME}], remappings=[('ball_r', 'ball_r')])

    sensor_node = Node(
        package='ball_on_plate', executable='ball_sensor_node', name='ball_sensor', output='screen',
        parameters=[{'delay_time': DELAY_TIME}])

    return LaunchDescription(
            [ control_node, error_node, filter_node, reference_node, sensor_node ])
