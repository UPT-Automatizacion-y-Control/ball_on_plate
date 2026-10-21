#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PointStamped
import math

class BallReferenceNode(Node):
    def __init__(self):
        super().__init__('ball_reference_node')

        # Parámetros iniciales
        self.declare_parameter('modo', 'reposo')
        self.declare_parameter('radio', 3.0)
        self.declare_parameter('velocidad', 1.5)
        self.declare_parameter('delay_time', 0.01)

        self.centro_x = 10.1
        self.centro_y = 5.9
        
        self.dt = self.get_parameter('delay_time').value
        self.t = 0.0 

        self.pub = self.create_publisher(PointStamped, 'ball_r', 10)
        self.timer = self.create_timer(self.dt, self.reference)
        self.get_logger().info("Nodo Reference Ball activo. Controla con 'ros2 param set'.")

    def reference(self):
        modo = self.get_parameter('modo').value
        
        # --- CONFIGURACIÓN DE PARÁMETROS POR MODO ---
        # Si quieres que se muevan más rápido, aumenta el valor de 'v'
        if modo == 'circulo':
            radio, v = 1.5, 2.95
        elif modo == 'cuadrado':
            radio, v = 2.25, 1.0  # Subí un poco la velocidad aquí
        elif modo == 'triangulo':
            radio, v = 2.0, 1.45
        elif modo == 'rectangulo':
            radio, v = 3.3, 1.0
        elif modo == 'estrella':
            radio, v = 3.0, 1.175
        else:
            radio, v = 0.0, 0.0

        out = PointStamped()
        out.header.stamp = self.get_clock().now().to_msg()
        out.header.frame_id = "world"

        if modo == 'reposo':
            out.point.x = self.centro_x
            out.point.y = self.centro_y
            self.t = 0.0
        else:
            # Incremento de tiempo basado en la velocidad
            # Esto hace que 'v' realmente controle la rapidez del avance
            self.t += self.dt * v 
            
            # Calculamos la fase sobre un periodo fijo de 2PI
            periodo = 2 * math.pi
            fase = (self.t % periodo) / periodo

            if modo == 'circulo':
                out.point.x = self.centro_x + radio * math.cos(self.t)
                out.point.y = self.centro_y + radio * math.sin(self.t)

            elif modo == 'cuadrado':
                if fase < 0.25:
                    out.point.x = self.centro_x + radio
                    out.point.y = self.centro_y + radio * (fase * 8 - 1)
                elif fase < 0.5:
                    out.point.x = self.centro_x + radio * (1 - (fase - 0.25) * 8)
                    out.point.y = self.centro_y + radio
                elif fase < 0.75:
                    out.point.x = self.centro_x - radio
                    out.point.y = self.centro_y + radio * (1 - (fase - 0.5) * 8)
                else:
                    out.point.x = self.centro_x + radio * ((fase - 0.75) * 8 - 1)
                    out.point.y = self.centro_y - radio

            elif modo == 'triangulo':
                if fase < 1/3:
                    f = fase * 3
                    out.point.x = self.centro_x + radio * (1 - 2 * f)
                    out.point.y = self.centro_y - radio * 0.5
                elif fase < 2/3:
                    f = (fase - 1/3) * 3
                    out.point.x = self.centro_x - radio + radio * f
                    out.point.y = self.centro_y - radio * 0.5 + radio * 1.5 * f
                else:
                    f = (fase - 2/3) * 3
                    out.point.x = self.centro_x + radio * f
                    out.point.y = self.centro_y + radio - radio * 1.5 * f

            elif modo == 'rectangulo':
                rx, ry = radio * 1.5, radio * 0.7
                if fase < 0.25:
                    out.point.x = self.centro_x + rx; out.point.y = self.centro_y + ry * (fase * 8 - 1)
                elif fase < 0.5:
                    out.point.x = self.centro_x + rx * (1 - (fase - 0.25) * 8); out.point.y = self.centro_y + ry
                elif fase < 0.75:
                    out.point.x = self.centro_x - rx; out.point.y = self.centro_y + ry * (1 - (fase - 0.5) * 8)
                else:
                    out.point.x = self.centro_x + rx * ((fase - 0.75) * 8 - 1); out.point.y = self.centro_y - ry

            elif modo == 'estrella':
                puntas = 5
                fase = (puntas * self.t) / (2 * math.pi)
                # 2. Generar una onda triangular pura que oscila estrictamente entre 0 y 1
                onda_triangular = 2 * abs(fase - math.floor(fase + 0.5))
                # 3. Modular el radio (0.5 es el radio mínimo en los valles, 1.0 en las puntas)
                # Puedes ajustar el 0.5 y 0.5 para hacer la estrella más "esbelta" o "gorda"
                r_osc = radio * (0.5 + 0.5 * onda_triangular)
                out.point.x = self.centro_x + r_osc * math.cos(self.t)
                out.point.y = self.centro_y + r_osc * math.sin(self.t)

        self.pub.publish(out)

def main(args=None):
    rclpy.init(args=args)
    node = BallReferenceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
