"""
Módulo para gestión de inventario de materiales
"""
from db_connection import get_connection
from datetime import datetime

class InventoryManager:
    """Gestiona el inventario de materiales"""
    
    @staticmethod
    def agregar_material(nombre, tipo, unidad_medida, costo_unitario, descripcion=None):
        """
        Agrega un nuevo material al catálogo
        """
        conn = get_connection()
        if not conn:
            return {'success': False, 'error': 'Error de conexión a BD'}
        
        try:
            cur = conn.cursor()
            
            # Insertar material
            cur.execute("""
                INSERT INTO materiales (nombre_material, tipo, unidad_medida, costo_unitario, descripcion)
                VALUES (?, ?, ?, ?, ?)
            """, (nombre, tipo, unidad_medida, costo_unitario, descripcion))
            
            id_material = cur.lastrowid
            
            # Inicializar inventario en 0
            cur.execute("""
                INSERT INTO inventario_materiales (id_material, cantidad)
                VALUES (?, 0)
            """, (id_material,))
            
            conn.commit()
            cur.close()
            conn.close()
            
            return {'success': True, 'id_material': id_material}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def actualizar_stock(id_material, cantidad_cambio):
        """
        Actualiza el stock de un material (puede ser positivo o negativo)
        cantidad_cambio: cantidad a sumar (positivo) o restar (negativo)
        """
        conn = get_connection()
        if not conn:
            return {'success': False, 'error': 'Error de conexión a BD'}
        
        try:
            cur = conn.cursor()
            
            # Verificar si existe registro en inventario
            cur.execute("""
                SELECT id_inventario, cantidad FROM inventario_materiales 
                WHERE id_material = ?
            """, (id_material,))
            
            resultado = cur.fetchone()
            
            if resultado:
                # Actualizar existente
                id_inventario, cantidad_actual = resultado[0], resultado[1]
                nueva_cantidad = cantidad_actual + cantidad_cambio
                
                if nueva_cantidad < 0:
                    return {'success': False, 'error': 'Stock insuficiente'}
                
                cur.execute("""
                    UPDATE inventario_materiales 
                    SET cantidad = ?, fecha_actualizacion = datetime('now')
                    WHERE id_inventario = ?
                """, (nueva_cantidad, id_inventario))
            else:
                # Crear nuevo registro
                if cantidad_cambio < 0:
                    return {'success': False, 'error': 'No se puede iniciar con stock negativo'}
                
                cur.execute("""
                    INSERT INTO inventario_materiales (id_material, cantidad)
                    VALUES (?, ?)
                """, (id_material, cantidad_cambio))
            
            conn.commit()
            cur.close()
            conn.close()
            
            return {'success': True, 'nueva_cantidad': nueva_cantidad if resultado else cantidad_cambio}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def obtener_inventario_completo():
        """
        Obtiene todo el inventario con información de materiales
        """
        conn = get_connection()
        if not conn:
            return []
        
        try:
            cur = conn.cursor()
            
            cur.execute("""
                SELECT 
                    m.id_material,
                    m.nombre_material,
                    m.tipo,
                    m.unidad_medida,
                    m.costo_unitario,
                    COALESCE(i.cantidad, 0) as stock_actual,
                    COALESCE(i.cantidad * m.costo_unitario, 0) as valor_total,
                    i.fecha_actualizacion
                FROM materiales m
                LEFT JOIN inventario_materiales i ON m.id_material = i.id_material
                ORDER BY m.nombre_material
            """)
            
            inventario = []
            for row in cur.fetchall():
                inventario.append({
                    'id_material': row[0],
                    'nombre_material': row[1],
                    'tipo': row[2],
                    'unidad_medida': row[3],
                    'costo_unitario': row[4],
                    'stock_actual': row[5],
                    'valor_total': row[6],
                    'fecha_actualizacion': row[7]
                })
            
            cur.close()
            conn.close()
            
            return inventario
        
        except Exception as e:
            print(f"Error obteniendo inventario: {e}")
            return []
    
    @staticmethod
    def obtener_materiales():
        """
        Obtiene lista de materiales para selectores
        """
        conn = get_connection()
        if not conn:
            return []
        
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id_material, nombre_material, tipo, unidad_medida
                FROM materiales
                ORDER BY nombre_material
            """)
            
            materiales = []
            for row in cur.fetchall():
                materiales.append({
                    'id_material': row[0],
                    'nombre_material': row[1],
                    'tipo': row[2],
                    'unidad_medida': row[3]
                })
            
            cur.close()
            conn.close()
            
            return materiales
        
        except Exception as e:
            print(f"Error obteniendo materiales: {e}")
            return []
    
    @staticmethod
    def verificar_disponibilidad(id_material, cantidad_requerida):
        """
        Verifica si hay suficiente stock de un material
        """
        conn = get_connection()
        if not conn:
            return False
        
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT cantidad FROM inventario_materiales
                WHERE id_material = ?
            """, (id_material,))
            
            resultado = cur.fetchone()
            cur.close()
            conn.close()
            
            if not resultado:
                return False
            
            return resultado[0] >= cantidad_requerida
        
        except Exception as e:
            print(f"Error verificando disponibilidad: {e}")
            return False
    
    @staticmethod
    def obtener_materiales_bajo_stock(umbral=100):
        """
        Obtiene materiales con stock por debajo del umbral
        """
        conn = get_connection()
        if not conn:
            return []
        
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT 
                    m.nombre_material,
                    m.unidad_medida,
                    i.cantidad
                FROM materiales m
                JOIN inventario_materiales i ON m.id_material = i.id_material
                WHERE i.cantidad < ?
                ORDER BY i.cantidad ASC
            """, (umbral,))
            
            materiales_bajo = []
            for row in cur.fetchall():
                materiales_bajo.append({
                    'nombre': row[0],
                    'unidad': row[1],
                    'cantidad': row[2]
                })
            
            cur.close()
            conn.close()
            
            return materiales_bajo
        
        except Exception as e:
            print(f"Error obteniendo materiales bajo stock: {e}")
            return []
    
    @staticmethod
    def calcular_costo_produccion(materiales_necesarios):
        """
        Calcula el costo de producción dado un diccionario de materiales
        materiales_necesarios: {id_material: cantidad_requerida, ...}
        """
        conn = get_connection()
        if not conn:
            return None
        
        try:
            cur = conn.cursor()
            costo_total = 0
            
            for id_material, cantidad in materiales_necesarios.items():
                cur.execute("""
                    SELECT costo_unitario FROM materiales
                    WHERE id_material = ?
                """, (id_material,))
                
                resultado = cur.fetchone()
                if resultado:
                    costo_total += resultado[0] * cantidad
            
            cur.close()
            conn.close()
            
            return round(costo_total, 2)
        
        except Exception as e:
            print(f"Error calculando costo: {e}")
            return None
    
    @staticmethod
    def eliminar_material(id_material):
        """
        Elimina un material del sistema
        """
        conn = get_connection()
        if not conn:
            return {'success': False, 'error': 'Error de conexión a BD'}
        
        try:
            cur = conn.cursor()
            
            # Eliminar de inventario primero (por foreign key)
            cur.execute("DELETE FROM inventario_materiales WHERE id_material = ?", (id_material,))
            
            # Eliminar material
            cur.execute("DELETE FROM materiales WHERE id_material = ?", (id_material,))
            
            conn.commit()
            cur.close()
            conn.close()
            
            return {'success': True}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}