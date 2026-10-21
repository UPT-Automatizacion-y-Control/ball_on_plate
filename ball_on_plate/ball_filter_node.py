#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PointStamped
from collections import deque
import math

class BallFilterNode(Node):
    def __init__(self):
        super().__init__('ball_filter_node')

        # Declarar parámetro de la ventana del filtro (equivalente a number_of_observations)
        self.declare_parameter('ball_filter.params.number_of_observations', 50)
        self.window_size = self.get_parameter('ball_filter.params.number_of_observations').value

        # Buffers para almacenar las últimas observaciones de X e Y
        self.history_x = deque(maxlen=self.window_size)
        self.history_y = deque(maxlen=self.window_size)

        # Publicador: Tópico de salida filtrada
        self.pub_ = self.create_publisher(PointStamped, 'ball_f', 10)

        # Suscriptor: Tópico original de la pantalla
        self.sub_ = self.create_subscription(PointStamped, 'ball_p', self.callback, 10)

        self.get_logger().info(f"Nodo de Filtrado (Python) iniciado con ventana de {self.window_size}")

    def callback(self, msg):

        if msg.point.x == 0.0 and msg.point.y == 0.0:
            return

        # 1. Agregar nuevos datos al historial
        self.history_x.append(msg.point.x)
        self.history_y.append(msg.point.y)

        # 2. Calcular el promedio de la ventana (Filtro de Media)
        count = len(self.history_x)
        avg_x = sum(self.history_x) / count
        avg_y = sum(self.history_y) / count

        # 3. Validar que los números sean finitos (evitar NaN o Inf)
        #if not (math.isfinite(avg_x) and math.isfinite(avg_y)):
        #    self.get_logger().warn("Salida inválida detectada (no finita)")
        #    return

        if not (math.isfinite(avg_x) and math.isfinite(avg_y)):
            return

        # 4. Crear y publicar el mensaje filtrado
        out = PointStamped()
        out.header = msg.header  # Mantiene el timestamp original para el control PD
        out.point.x = avg_x
        out.point.y = avg_y
        out.point.z = msg.point.z # Mantener Z si es necesario

        self.pub_.publish(out)

def main(args=None):
    rclpy.init(args=args)
    node = BallFilterNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
