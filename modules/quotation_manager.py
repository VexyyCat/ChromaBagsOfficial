"""
Módulo para gestión de cotizaciones
"""
from db_connection import get_connection
from datetime import datetime

class QuotationManager:
    """Gestiona cotizaciones de productos"""
    
    @staticmethod
    def crear_cotizacion(id_cliente, productos, estado='pendiente'):
        """
        Crea una nueva cotización
        productos: lista de dict [{id_combinacion, cantidad, precio_unitario}, ...]
        """
        conn = get_connection()
        if not conn:
            return {'success': False, 'error': 'Error de conexión a BD'}
        
        try:
            cur = conn.cursor()
            
            # Calcular total
            total_estimado = sum(p['cantidad'] * p['precio_unitario'] for p in productos)
            
            # Insertar cotización
            cur.execute("""
                INSERT INTO cotizaciones (id_cliente, total_estimado, estado)
                VALUES (?, ?, ?)
            """, (id_cliente, total_estimado, estado))
            
            id_cotizacion = cur.lastrowid
            
            # Insertar detalles (usando materiales como proxy de productos)
            # Nota: La tabla detalle_cotizacion está diseñada para materiales
            # Para productos, deberías crear una tabla detalle_cotizacion_productos
            # Por ahora, guardamos en detalle_cotizacion
            
            for producto in productos:
                subtotal = producto['cantidad'] * producto['precio_unitario']
                cur.execute("""
                    INSERT INTO detalle_cotizacion (
                        id_cotizacion, id_material, cantidad, 
                        costo_unitario, subtotal
                    ) VALUES (?, ?, ?, ?, ?)
                """, (id_cotizacion, producto['id_combinacion'], 
                      producto['cantidad'], producto['precio_unitario'], subtotal))
            
            conn.commit()
            cur.close()
            conn.close()
            
            return {'success': True, 'id_cotizacion': id_cotizacion, 'total': total_estimado}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def obtener_cotizaciones():
        """
        Obtiene todas las cotizaciones con información del cliente
        """
        conn = get_connection()
        if not conn:
            return []
        
        try:
            cur = conn.cursor()
            
            cur.execute("""
                SELECT 
                    c.id_cotizacion,
                    c.id_cliente,
                    cl.nombre_cliente,
                    c.fecha_emision,
                    c.total_estimado,
                    c.estado,
                    COUNT(dc.id_detalle) as cantidad_productos,
                    SUM(dc.cantidad) as cantidad_total
                FROM cotizaciones c
                LEFT JOIN clientes cl ON c.id_cliente = cl.id_cliente
                LEFT JOIN detalle_cotizacion dc ON c.id_cotizacion = dc.id_cotizacion
                GROUP BY c.id_cotizacion
                ORDER BY c.fecha_emision DESC
            """)
            
            cotizaciones = []
            for row in cur.fetchall():
                cotizaciones.append({
                    'id_cotizacion': row[0],
                    'id_cliente': row[1],
                    'nombre_cliente': row[2],
                    'fecha_emision': row[3],
                    'total_estimado': row[4],
                    'estado': row[5],
                    'cantidad_productos': row[6] or 0,
                    'cantidad_total': row[7] or 0
                })
            
            cur.close()
            conn.close()
            
            return cotizaciones
        
        except Exception as e:
            print(f"Error obteniendo cotizaciones: {e}")
            return []
    
    @staticmethod
    def obtener_cotizacion_detalle(id_cotizacion):
        """
        Obtiene el detalle completo de una cotización
        """
        conn = get_connection()
        if not conn:
            return None
        
        try:
            cur = conn.cursor()
            
            # Información general
            cur.execute("""
                SELECT 
                    c.id_cotizacion,
                    c.id_cliente,
                    cl.nombre_cliente,
                    cl.correo,
                    cl.telefono,
                    cl.direccion,
                    c.fecha_emision,
                    c.total_estimado,
                    c.estado
                FROM cotizaciones c
                LEFT JOIN clientes cl ON c.id_cliente = cl.id_cliente
                WHERE c.id_cotizacion = ?
            """, (id_cotizacion,))
            
            cotizacion_info = cur.fetchone()
            if not cotizacion_info:
                return None
            
            # Detalles de productos
            cur.execute("""
                SELECT 
                    dc.id_detalle,
                    dc.id_material as id_producto,
                    dc.cantidad,
                    dc.costo_unitario as precio_unitario,
                    dc.subtotal
                FROM detalle_cotizacion dc
                WHERE dc.id_cotizacion = ?
            """, (id_cotizacion,))
            
            productos = []
            for row in cur.fetchall():
                productos.append({
                    'id_detalle': row[0],
                    'id_producto': row[1],
                    'cantidad': row[2],
                    'precio_unitario': row[3],
                    'subtotal': row[4]
                })
            
            cur.close()
            conn.close()
            
            return {
                'id_cotizacion': cotizacion_info[0],
                'id_cliente': cotizacion_info[1],
                'nombre_cliente': cotizacion_info[2],
                'correo': cotizacion_info[3],
                'telefono': cotizacion_info[4],
                'direccion': cotizacion_info[5],
                'fecha_emision': cotizacion_info[6],
                'total_estimado': cotizacion_info[7],
                'estado': cotizacion_info[8],
                'productos': productos
            }
        
        except Exception as e:
            print(f"Error obteniendo detalle de cotización: {e}")
            return None
    
    @staticmethod
    def actualizar_estado_cotizacion(id_cotizacion, nuevo_estado):
        """
        Actualiza el estado de una cotización
        Estados: pendiente, aprobada, rechazada, completada
        """
        conn = get_connection()
        if not conn:
            return {'success': False, 'error': 'Error de conexión a BD'}
        
        try:
            cur = conn.cursor()
            
            cur.execute("""
                UPDATE cotizaciones
                SET estado = ?
                WHERE id_cotizacion = ?
            """, (nuevo_estado, id_cotizacion))
            
            conn.commit()
            cur.close()
            conn.close()
            
            return {'success': True}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def eliminar_cotizacion(id_cotizacion):
        """
        Elimina una cotización (cascade elimina detalles automáticamente)
        """
        conn = get_connection()
        if not conn:
            return {'success': False, 'error': 'Error de conexión a BD'}
        
        try:
            cur = conn.cursor()
            
            # SQLite no soporta CASCADE en DELETE directamente en todas las versiones
            # Eliminar detalles primero
            cur.execute("DELETE FROM detalle_cotizacion WHERE id_cotizacion = ?", (id_cotizacion,))
            
            # Eliminar cotización
            cur.execute("DELETE FROM cotizaciones WHERE id_cotizacion = ?", (id_cotizacion,))
            
            conn.commit()
            cur.close()
            conn.close()
            
            return {'success': True}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def duplicar_cotizacion(id_cotizacion):
        """
        Duplica una cotización existente
        """
        conn = get_connection()
        if not conn:
            return {'success': False, 'error': 'Error de conexión a BD'}
        
        try:
            cur = conn.cursor()
            
            # Obtener cotización original
            cur.execute("""
                SELECT id_cliente, total_estimado, estado
                FROM cotizaciones
                WHERE id_cotizacion = ?
            """, (id_cotizacion,))
            
            cotizacion_orig = cur.fetchone()
            if not cotizacion_orig:
                return {'success': False, 'error': 'Cotización no encontrada'}
            
            # Crear nueva cotización
            cur.execute("""
                INSERT INTO cotizaciones (id_cliente, total_estimado, estado)
                VALUES (?, ?, 'pendiente')
            """, (cotizacion_orig[0], cotizacion_orig[1]))
            
            nueva_id = cur.lastrowid
            
            # Copiar detalles
            cur.execute("""
                INSERT INTO detalle_cotizacion (
                    id_cotizacion, id_material, cantidad, 
                    costo_unitario, subtotal
                )
                SELECT ?, id_material, cantidad, costo_unitario, subtotal
                FROM detalle_cotizacion
                WHERE id_cotizacion = ?
            """, (nueva_id, id_cotizacion))
            
            conn.commit()
            cur.close()
            conn.close()
            
            return {'success': True, 'id_cotizacion': nueva_id}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def obtener_productos_disponibles():
        """
        Obtiene productos/combinaciones disponibles para cotización
        """
        conn = get_connection()
        if not conn:
            return []
        
        try:
            cur = conn.cursor()
            
            # Obtener combinaciones como productos
            cur.execute("""
                SELECT 
                    c.id_combinacion,
                    c.nombre_guardado,
                    mb.nombre_modelo,
                    mb.tipo,
                    180 as precio_base
                FROM combinaciones c
                JOIN modelos_bolsas mb ON c.id_modelo = mb.id_modelo
                ORDER BY c.fecha_creacion DESC
            """)
            
            productos = []
            for row in cur.fetchall():
                # Calcular precio según tipo
                precio_base = 180
                if row[3] == 'combinado':
                    precio_base = 220
                elif row[3] == 'especial':
                    precio_base = 250
                
                productos.append({
                    'id_combinacion': row[0],
                    'nombre': row[1],
                    'modelo': row[2],
                    'tipo': row[3],
                    'precio': precio_base
                })
            
            cur.close()
            conn.close()
            
            return productos
        
        except Exception as e:
            print(f"Error obteniendo productos: {e}")
            return []
    
    @staticmethod
    def generar_reporte_cotizaciones(fecha_inicio=None, fecha_fin=None):
        """
        Genera reporte de cotizaciones en un rango de fechas
        """
        conn = get_connection()
        if not conn:
            return None
        
        try:
            cur = conn.cursor()
            
            query = """
                SELECT 
                    COUNT(*) as total_cotizaciones,
                    SUM(total_estimado) as monto_total,
                    AVG(total_estimado) as promedio,
                    estado,
                    COUNT(*) as cantidad_por_estado
                FROM cotizaciones
            """
            
            params = []
            if fecha_inicio and fecha_fin:
                query += " WHERE fecha_emision BETWEEN ? AND ?"
                params = [fecha_inicio, fecha_fin]
            
            query += " GROUP BY estado"
            
            cur.execute(query, params)
            
            reporte = {
                'por_estado': [],
                'total_general': 0,
                'monto_total': 0
            }
            
            for row in cur.fetchall():
                reporte['por_estado'].append({
                    'estado': row[3],
                    'cantidad': row[4],
                    'monto': row[1]
                })
                reporte['total_general'] += row[4]
                reporte['monto_total'] += (row[1] or 0)
            
            cur.close()
            conn.close()
            
            return reporte
        
        except Exception as e:
            print(f"Error generando reporte: {e}")
            return None