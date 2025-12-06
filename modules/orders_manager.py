"""
Módulo para gestión de pedidos y reportes
"""
from db_connection import get_connection
from datetime import datetime

class OrdersManager:
    """Gestiona pedidos de productos"""
    
    @staticmethod
    def crear_pedido(id_cliente, id_combinacion, cantidad, fecha_entrega, estado='pendiente'):
        """
        Crea un nuevo pedido desde una combinación del catálogo
        """
        conn = get_connection()
        if not conn:
            return {'success': False, 'error': 'Error de conexión a BD'}
        
        try:
            cur = conn.cursor()
            
            # Obtener información de la combinación
            cur.execute("""
                SELECT c.nombre_guardado, mb.tipo
                FROM combinaciones c
                JOIN modelos_bolsas mb ON c.id_modelo = mb.id_modelo
                WHERE c.id_combinacion = ?
            """, (id_combinacion,))
            
            combinacion = cur.fetchone()
            if not combinacion:
                return {'success': False, 'error': 'Combinación no encontrada'}
            
            # Calcular precio según tipo de modelo
            tipo_modelo = combinacion[1]
            if tipo_modelo == 'simple':
                precio_unitario = 180.0
            elif tipo_modelo == 'combinado':
                precio_unitario = 220.0
            elif tipo_modelo == 'especial':
                precio_unitario = 250.0
            else:
                precio_unitario = 180.0
            
            subtotal = precio_unitario * cantidad
            
            # Obtener fecha actual
            fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Insertar pedido
            cur.execute("""
                INSERT INTO pedidos (id_cliente, fecha_pedido, fecha_entrega, estado, total)
                VALUES (?, ?, ?, ?, ?)
            """, (id_cliente, fecha_actual, fecha_entrega, estado, subtotal))
            
            id_pedido = cur.lastrowid
            
            # Insertar detalle del pedido
            cur.execute("""
                INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, precio_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?)
            """, (id_pedido, id_combinacion, cantidad, precio_unitario, subtotal))
            
            conn.commit()
            cur.close()
            conn.close()
            
            return {'success': True, 'id_pedido': id_pedido, 'total': subtotal}
        
        except Exception as e:
            print(f"Error creando pedido: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def obtener_pedidos():
        """
        Obtiene todos los pedidos con información completa
        """
        conn = get_connection()
        if not conn:
            return []
        
        try:
            cur = conn.cursor()
            
            cur.execute("""
                SELECT p.id_pedido, 
                       COALESCE(c.nombre_cliente, 'Cliente Eliminado'),
                       COALESCE(comb.nombre_guardado, 'Producto sin nombre'),
                       p.fecha_pedido,
                       p.fecha_entrega,
                       p.estado,
                       p.total,
                       dp.cantidad
                FROM pedidos p
                LEFT JOIN clientes c ON p.id_cliente = c.id_cliente
                LEFT JOIN detalle_pedido dp ON p.id_pedido = dp.id_pedido
                LEFT JOIN combinaciones comb ON dp.id_producto = comb.id_combinacion
                ORDER BY p.id_pedido DESC
            """)
            
            pedidos = []
            for row in cur.fetchall():
                pedidos.append({
                    'id_pedido': row[0],
                    'nombre_cliente': row[1],
                    'nombre_producto': row[2],
                    'fecha_pedido': row[3],
                    'fecha_entrega': row[4],
                    'estado': row[5],
                    'total': row[6],
                    'cantidad': row[7] or 0
                })
            
            cur.close()
            conn.close()
            
            return pedidos
        
        except Exception as e:
            print(f"Error obteniendo pedidos: {e}")
            return []
    
    @staticmethod
    def obtener_pedido(id_pedido):
        """
        Obtiene un pedido específico
        """
        conn = get_connection()
        if not conn:
            return None
        
        try:
            cur = conn.cursor()
            
            cur.execute("""
                SELECT p.*, 
                       COALESCE(c.nombre_cliente, 'Cliente Eliminado'), 
                       COALESCE(comb.nombre_guardado, 'Producto sin nombre'), 
                       dp.cantidad
                FROM pedidos p
                LEFT JOIN clientes c ON p.id_cliente = c.id_cliente
                LEFT JOIN detalle_pedido dp ON p.id_pedido = dp.id_pedido
                LEFT JOIN combinaciones comb ON dp.id_producto = comb.id_combinacion
                WHERE p.id_pedido = ?
            """, (id_pedido,))
            
            pedido = cur.fetchone()
            cur.close()
            conn.close()
            
            if pedido:
                return {
                    'id_pedido': pedido[0],
                    'id_cliente': pedido[1],
                    'fecha_pedido': pedido[2],
                    'fecha_entrega': pedido[3],
                    'estado': pedido[4],
                    'total': pedido[5],
                    'nombre_cliente': pedido[6],
                    'nombre_producto': pedido[7],
                    'cantidad': pedido[8] or 0
                }
            
            return None
        
        except Exception as e:
            print(f"Error obteniendo pedido: {e}")
            return None
    
    @staticmethod
    def actualizar_pedido(id_pedido, fecha_entrega, estado):
        """
        Actualiza un pedido existente
        """
        conn = get_connection()
        if not conn:
            return {'success': False, 'error': 'Error de conexión a BD'}
        
        try:
            cur = conn.cursor()
            
            cur.execute("""
                UPDATE pedidos 
                SET fecha_entrega = ?, estado = ?
                WHERE id_pedido = ?
            """, (fecha_entrega, estado, id_pedido))
            
            conn.commit()
            cur.close()
            conn.close()
            
            return {'success': True}
        
        except Exception as e:
            print(f"Error actualizando pedido: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def eliminar_pedido(id_pedido):
        """
        Elimina un pedido y sus detalles
        """
        conn = get_connection()
        if not conn:
            return {'success': False, 'error': 'Error de conexión a BD'}
        
        try:
            cur = conn.cursor()
            
            # Eliminar detalles primero
            cur.execute("DELETE FROM detalle_pedido WHERE id_pedido = ?", (id_pedido,))
            
            # Eliminar pagos asociados si existen
            try:
                cur.execute("DELETE FROM pagos WHERE id_pedido = ?", (id_pedido,))
            except:
                pass
            
            # Eliminar pedido
            cur.execute("DELETE FROM pedidos WHERE id_pedido = ?", (id_pedido,))
            
            conn.commit()
            cur.close()
            conn.close()
            
            return {'success': True}
        
        except Exception as e:
            print(f"Error eliminando pedido: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def obtener_pedidos_por_estado():
        """
        Obtiene pedidos categorizados por estado para reportes
        """
        conn = get_connection()
        if not conn:
            return {'por_entregar': [], 'entregados': [], 'vencidos': [], 'todos': []}
        
        try:
            cur = conn.cursor()
            fecha_actual = datetime.now().strftime('%Y-%m-%d')
            
            # Pedidos POR ENTREGAR (pendientes, en proceso, finalizados - NO entregados ni cancelados)
            # Y que su fecha de entrega sea hoy o futura
            cur.execute("""
                SELECT p.id_pedido, 
                       COALESCE(c.nombre_cliente, 'Cliente Eliminado'), 
                       COALESCE(comb.nombre_guardado, 'Producto sin nombre'),
                       p.fecha_pedido, 
                       p.fecha_entrega, 
                       p.estado, 
                       p.total
                FROM pedidos p
                LEFT JOIN clientes c ON p.id_cliente = c.id_cliente
                LEFT JOIN detalle_pedido dp ON p.id_pedido = dp.id_pedido
                LEFT JOIN combinaciones comb ON dp.id_producto = comb.id_combinacion
                WHERE p.estado IN ('pendiente', 'en_proceso', 'finalizado')
                AND p.fecha_entrega >= ?
                GROUP BY p.id_pedido
                ORDER BY p.fecha_entrega ASC
            """, (fecha_actual,))
            por_entregar = cur.fetchall()
            
            # Pedidos ENTREGADOS
            cur.execute("""
                SELECT p.id_pedido, 
                       COALESCE(c.nombre_cliente, 'Cliente Eliminado'), 
                       COALESCE(comb.nombre_guardado, 'Producto sin nombre'),
                       p.fecha_pedido, 
                       p.fecha_entrega, 
                       p.estado, 
                       p.total
                FROM pedidos p
                LEFT JOIN clientes c ON p.id_cliente = c.id_cliente
                LEFT JOIN detalle_pedido dp ON p.id_pedido = dp.id_pedido
                LEFT JOIN combinaciones comb ON dp.id_producto = comb.id_combinacion
                WHERE p.estado = 'entregado'
                GROUP BY p.id_pedido
                ORDER BY p.fecha_entrega DESC
            """)
            entregados = cur.fetchall()
            
            # Pedidos VENCIDOS (fecha pasada y NO entregados ni cancelados)
            cur.execute("""
                SELECT p.id_pedido, 
                       COALESCE(c.nombre_cliente, 'Cliente Eliminado'), 
                       COALESCE(comb.nombre_guardado, 'Producto sin nombre'),
                       p.fecha_pedido, 
                       p.fecha_entrega, 
                       p.estado, 
                       p.total
                FROM pedidos p
                LEFT JOIN clientes c ON p.id_cliente = c.id_cliente
                LEFT JOIN detalle_pedido dp ON p.id_pedido = dp.id_pedido
                LEFT JOIN combinaciones comb ON dp.id_producto = comb.id_combinacion
                WHERE p.fecha_entrega < ?
                AND p.estado NOT IN ('entregado', 'cancelado')
                GROUP BY p.id_pedido
                ORDER BY p.fecha_entrega ASC
            """, (fecha_actual,))
            vencidos = cur.fetchall()
            
            # TODOS los pedidos
            cur.execute("""
                SELECT p.id_pedido, 
                       COALESCE(c.nombre_cliente, 'Cliente Eliminado'), 
                       COALESCE(comb.nombre_guardado, 'Producto sin nombre'),
                       p.fecha_pedido, 
                       p.fecha_entrega, 
                       p.estado, 
                       p.total
                FROM pedidos p
                LEFT JOIN clientes c ON p.id_cliente = c.id_cliente
                LEFT JOIN detalle_pedido dp ON p.id_pedido = dp.id_pedido
                LEFT JOIN combinaciones comb ON dp.id_producto = comb.id_combinacion
                GROUP BY p.id_pedido
                ORDER BY p.id_pedido DESC
            """)
            todos = cur.fetchall()
            
            cur.close()
            conn.close()
            
            print(f"📊 REPORTES - Por entregar: {len(por_entregar)}, Entregados: {len(entregados)}, Vencidos: {len(vencidos)}, Todos: {len(todos)}")
            
            return {
                'por_entregar': por_entregar,
                'entregados': entregados,
                'vencidos': vencidos,
                'todos': todos
            }
        
        except Exception as e:
            print(f"❌ Error obteniendo pedidos por estado: {e}")
            import traceback
            traceback.print_exc()
            return {'por_entregar': [], 'entregados': [], 'vencidos': [], 'todos': []}
    
    @staticmethod
    def obtener_estadisticas_dashboard():
        """
        Obtiene estadísticas para el dashboard de reportes
        """
        conn = get_connection()
        if not conn:
            return None
        
        try:
            cur = conn.cursor()
            
            # Total de pedidos (sin incluir cancelados)
            cur.execute("SELECT COUNT(*) FROM pedidos WHERE estado != 'cancelado'")
            total_pedidos = cur.fetchone()[0] or 0
            
            # Pedidos por estado
            cur.execute("""
                SELECT estado, COUNT(*) as cantidad, SUM(total) as monto_total
                FROM pedidos
                GROUP BY estado
            """)
            por_estado = {}
            for row in cur.fetchall():
                por_estado[row[0]] = {
                    'cantidad': row[1],
                    'monto': row[2] or 0
                }
            
            # Ingresos totales (solo entregados)
            cur.execute("SELECT COALESCE(SUM(total), 0) FROM pedidos WHERE estado = 'entregado'")
            ingresos_totales = cur.fetchone()[0] or 0
            
            # Pedidos del mes actual
            cur.execute("""
                SELECT COUNT(*), COALESCE(SUM(total), 0)
                FROM pedidos
                WHERE strftime('%Y-%m', fecha_pedido) = strftime('%Y-%m', 'now')
                AND estado != 'cancelado'
            """)
            mes_actual = cur.fetchone()
            pedidos_mes = mes_actual[0] or 0
            ingresos_mes = mes_actual[1] or 0
            
            # Clientes activos (que tienen al menos un pedido)
            cur.execute("""
                SELECT COUNT(DISTINCT id_cliente) 
                FROM pedidos 
                WHERE estado != 'cancelado'
            """)
            clientes_activos = cur.fetchone()[0] or 0
            
            # Productos más vendidos
            cur.execute("""
                SELECT 
                    COALESCE(comb.nombre_guardado, 'Diseño sin nombre') as nombre,
                    SUM(dp.cantidad) as total_vendido
                FROM detalle_pedido dp
                LEFT JOIN pedidos p ON dp.id_pedido = p.id_pedido
                LEFT JOIN combinaciones comb ON dp.id_producto = comb.id_combinacion
                WHERE p.estado != 'cancelado'
                GROUP BY dp.id_producto
                HAVING total_vendido > 0
                ORDER BY total_vendido DESC
                LIMIT 5
            """)
            productos_top = [tuple(row) for row in cur.fetchall()]
            
            # Ventas por mes (últimos 6 meses)
            cur.execute("""
                SELECT 
                    strftime('%Y-%m', fecha_pedido) as mes,
                    COUNT(*) as pedidos,
                    COALESCE(SUM(total), 0) as ventas
                FROM pedidos
                WHERE fecha_pedido >= date('now', '-6 months')
                AND estado != 'cancelado'
                GROUP BY mes
                ORDER BY mes ASC
            """)
            ventas_mensuales = [tuple(row) for row in cur.fetchall()]
            
            cur.close()
            conn.close()
            
            estadisticas = {
                'total_pedidos': total_pedidos,
                'por_estado': por_estado,
                'ingresos_totales': ingresos_totales,
                'pedidos_mes': pedidos_mes,
                'ingresos_mes': ingresos_mes,
                'clientes_activos': clientes_activos,
                'productos_top': productos_top if productos_top else [],
                'ventas_mensuales': ventas_mensuales if ventas_mensuales else []
            }
            
            return estadisticas
        
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            import traceback
            traceback.print_exc()
            return {
                'total_pedidos': 0,
                'por_estado': {},
                'ingresos_totales': 0,
                'pedidos_mes': 0,
                'ingresos_mes': 0,
                'clientes_activos': 0,
                'productos_top': [],
                'ventas_mensuales': []
            }