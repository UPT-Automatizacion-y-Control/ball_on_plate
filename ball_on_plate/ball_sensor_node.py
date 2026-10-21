#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PointStamped
from evdev import InputDevice, ecodes
import os

class BallSensorNode(Node):
    def __init__(self):
        super().__init__('ball_sensor_node')

        self.declare_parameter('delay_time', 0.01)
        self.dt = self.get_parameter('delay_time').value
        
        # 1. Verificación de permisos (Faltaba esto para evitar errores de 'Permission Denied')
        device_path = '/dev/input/event14' # Para la pantalla tactil rectangular
        #device_path = '/dev/input/event16' # Para la pantalla tactil redonda
        if not os.path.exists(device_path):
            self.get_logger().error(f"El dispositivo {device_path} no existe. Verifica el número de event.")
            return

        # 2. Inicialización del Publicador
        self.publisher_ = self.create_publisher(PointStamped, 'ball_p', 10)
        
        try:
            self.dev = InputDevice(device_path)
            self.get_logger().info(f"Conectado a: {self.dev.name}")
        except Exception as e:
            self.get_logger().error(f"Error abriendo el dispositivo: {e}")
            return

        self.Xmin, self.Xmax = 125, 3935
        self.Ymin, self.Ymax = 116, 3940
        self.width_cm, self.height_cm = 20.2, 11.8
        self.current_x = 10.1
        self.current_y = 5.9
        self.timer = self.create_timer(self.dt, self.read_device)

    def read_device(self):
        try:
            # Leemos todos los eventos disponibles en el buffer para evitar lag
            while True:
                event = self.dev.read_one()
                if event is None:
                    break
                if event.type == ecodes.EV_ABS:
                    if event.code == ecodes.ABS_X:
                        self.current_x = max(0.0, (event.value - self.Xmax) / (self.Xmin - self.Xmax) * self.width_cm)
                    elif event.code == ecodes.ABS_Y:
                        self.current_y = max(0.0, (event.value - self.Ymin) / (self.Ymax - self.Ymin) * self.height_cm)
                          
            msg = PointStamped()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = "touch_frame"
            msg.point.x = self.current_x
            msg.point.y = self.current_y
            msg.point.z = 0.0     
            self.publisher_.publish(msg)

        except (BlockingIOError, OSError):
            # No hay datos nuevos por ahora
            pass

def main(args=None):
    rclpy.init(args=args)
    node = BallSensorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Nodo detenido por el usuario.")
    finally:
        # 4. Limpieza (Faltaba destruir el nodo al salir)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main() 
