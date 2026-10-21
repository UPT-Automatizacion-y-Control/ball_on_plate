#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PointStamped, PoseStamped
import time
from scipy.spatial.transform import Rotation

class BallControlNode(Node):
    def __init__(self):
        super().__init__('ball_control_node')
    
        # 1. Declaración de Parámetros (Kp, Ki, Kd)
        self.declare_parameter('kx',  5.0)
        self.declare_parameter('ky',  5.0)
        self.declare_parameter('kix', 1.0) 
        self.declare_parameter('kiy', 1.0)
        self.declare_parameter('kdx', 4.8) #0.00175
        self.declare_parameter('kdy', 4.8)
        self.declare_parameter('delay_time', 0.01)

        #self.declare_parameter('kx',  5.0)
        #self.declare_parameter('ky',  5.0)
        #self.declare_parameter('kix', 0.0) 
        #self.declare_parameter('kiy', 0.0)
        #self.declare_parameter('kdx', 4.69) #0.00175
        #self.declare_parameter('kdy', 4.69)
        #self.declare_parameter('delay_time', 0.01)

        # Leer parámetros
        self.kx = self.get_parameter('kx').value
        self.ky = self.get_parameter('ky').value
        self.kix = self.get_parameter('kix').value
        self.kiy = self.get_parameter('kiy').value
        self.kdx = self.get_parameter('kdx').value
        self.kdy = self.get_parameter('kdy').value
        self.dt = self.get_parameter('delay_time').value
        
        # 2. Variables de Estado
        self.error_x = 0.0
        self.error_y = 0.0
        self.prev_x = 0.0
        self.prev_y = 0.0
        self.integral_x = 0.0
        self.integral_y = 0.0
        self.derivate_x = 0.0
        self.derivate_y = 0.0

        self.last_msg_time = self.get_clock().now()
        self.sub_pos = self.create_subscription(PointStamped, 'ball_e', self.error_callback, 10)
        self.publisher_ = self.create_publisher(PoseStamped, 'user_goal', 10)
        self.get_logger().info("Nodo Ball Control Iniciado")
    
    def error_callback(self, msg):
        
        self.error_x = msg.point.x
        self.error_y = msg.point.y
        self.integral_x += self.error_x * self.dt
        self.integral_y += self.error_y * self.dt
        limit = 3000.0
        self.integral_x = max(min(self.integral_x, limit), -limit)
        self.integral_y = max(min(self.integral_y, limit), -limit)
        
        self.derivate_x = (self.error_x - self.prev_x) / self.dt
        self.derivate_y = (self.error_y - self.prev_y) / self.dt
        try:

            pose = PoseStamped()
            #pose.header.stamp = self.get_clock().now().to_msg()
            #pose.header.frame_id = "base_link"
            pose.header = msg.header
            pose.pose.position.z = 0.17 
            # Eje X del robot (basado en error de Y)
            roll = self.ky * self.error_y + self.kiy * self.integral_y + self.kdy * self.derivate_y
            # Eje Y del robot (basado en error de X)
            pitch = self.kx * self.error_x + self.kix * self.integral_x + self.kdx * self.derivate_x
            q = Rotation.from_euler('xyz', [-roll/1000, pitch/1000, 0]).as_quat()
            
            pose.pose.orientation.x = q[0]
            pose.pose.orientation.y = q[1]
            pose.pose.orientation.z = q[2]
            pose.pose.orientation.w = q[3]
            self.publisher_.publish(pose)

        except Exception as e:
            self.get_logger().error(f"Error en el cálculo PID: {e}")
        self.prev_x = self.error_x
        self.prev_y = self.error_y

def main(args=None):
    rclpy.init(args=args)
    node = BallControlNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
