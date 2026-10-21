#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PointStamped
import math

class BallErrorNode(Node):
    def __init__(self):
        super().__init__('ball_error_node')

        self.declare_parameter('delay_time', 0.01)
        self.dt = self.get_parameter('delay_time').value

        self.pub = self.create_publisher(PointStamped, 'ball_e', 10)
        self.sub_r = self.create_subscription(PointStamped, 'ball_r', self.callback_r, 10)
        self.sub_f = self.create_subscription(PointStamped, 'ball_f', self.callback_f, 10)
        self.timer = self.create_timer(self.dt, self.error)
        self.ball_r = PointStamped()
        self.ball_f = PointStamped()
        self.get_logger().info(f"Nodo Ball Error esta corriendo")

    def error(self):
        out = PointStamped()
        out.point.x = self.ball_r.point.x - self.ball_f.point.x
        out.point.y = self.ball_r.point.y - self.ball_f.point.y
        self.pub.publish(out)
        
    def callback_r(self, msg):
        self.ball_r.point = msg.point
        
    def callback_f(self, msg):
        self.ball_f.point = msg.point

def main(args=None):
    rclpy.init(args=args)
    node = BallErrorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
