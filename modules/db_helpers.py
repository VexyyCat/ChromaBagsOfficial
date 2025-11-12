"""
Funciones auxiliares para operaciones de base de datos
"""
from db_connection import get_connection

def insertar_color_si_no_existe(nombre, codigo_hex, id_paleta=None):
    """
    Inserta un color en la BD si no existe, retorna su ID
    """
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cur = conn.cursor()
        
        # Verificar si existe
        cur.execute("SELECT id_color FROM colores WHERE codigo_hex = ?", (codigo_hex,))
        resultado = cur.fetchone()
        
        if resultado:
            return resultado[0]
        
        # Insertar nuevo
        cur.execute("""
            INSERT INTO colores (nombre_color, codigo_hex, id_paleta)
            VALUES (?, ?, ?)
        """, (nombre, codigo_hex, id_paleta))
        conn.commit()
        
        return cur.lastrowid
    
    finally:
        conn.close()

def guardar_combinacion(id_modelo, esquema, colores, nombre_guardado):
    """
    Guarda una combinación completa en la BD
    colores: dict con keys: principal, secundario, hilo, asa
    """
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cur = conn.cursor()
        
        # Insertar o recuperar IDs de colores
        id_principal = insertar_color_si_no_existe(
            f"Color_{colores.get('principal', '')}", 
            colores.get('principal')
        ) if colores.get('principal') else None
        
        id_secundario = insertar_color_si_no_existe(
            f"Color_{colores.get('secundario', '')}", 
            colores.get('secundario')
        ) if colores.get('secundario') else None
        
        id_hilo = insertar_color_si_no_existe(
            f"Color_{colores.get('hilo', '')}", 
            colores.get('hilo')
        ) if colores.get('hilo') else None
        
        id_asa = insertar_color_si_no_existe(
            f"Color_{colores.get('asa', '')}", 
            colores.get('asa')
        ) if colores.get('asa') else None
        
        # Insertar combinación
        cur.execute("""
            INSERT INTO combinaciones (
                id_modelo, esquema, id_color_principal, 
                id_color_secundario, id_color_hilo, 
                id_color_asa, nombre_guardado
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (id_modelo, esquema, id_principal, id_secundario, 
              id_hilo, id_asa, nombre_guardado))
        
        conn.commit()
        return cur.lastrowid
    
    finally:
        conn.close()

def obtener_combinacion(id_combinacion):
    """
    Obtiene una combinación completa con sus colores
    """
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                c.*,
                mb.nombre_modelo,
                mb.tipo,
                cp.codigo_hex as hex_principal,
                cs.codigo_hex as hex_secundario,
                ch.codigo_hex as hex_hilo,
                ca.codigo_hex as hex_asa
            FROM combinaciones c
            JOIN modelos_bolsas mb ON c.id_modelo = mb.id_modelo
            LEFT JOIN colores cp ON c.id_color_principal = cp.id_color
            LEFT JOIN colores cs ON c.id_color_secundario = cs.id_color
            LEFT JOIN colores ch ON c.id_color_hilo = ch.id_color
            LEFT JOIN colores ca ON c.id_color_asa = ca.id_color
            WHERE c.id_combinacion = ?
        """, (id_combinacion,))
        
        return cur.fetchone()
    
    finally:
        conn.close()

def obtener_productos_catalogo():
    """
    Obtiene todos los productos con sus detalles para el catálogo
    """
    conn = get_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                pt.id_producto,
                pt.nombre_producto,
                mb.nombre_modelo,
                mb.tipo,
                cp.nombre_color AS color_principal,
                cp.codigo_hex AS hex_principal,
                cs.codigo_hex AS hex_secundario,
                pt.precio_sugerido,
                pt.stock,
                c.esquema,
                pt.id_combinacion
            FROM productos_terminados pt
            JOIN modelos_bolsas mb ON pt.id_modelo = mb.id_modelo
            LEFT JOIN combinaciones c ON pt.id_combinacion = c.id_combinacion
            LEFT JOIN colores cp ON c.id_color_principal = cp.id_color
            LEFT JOIN colores cs ON c.id_color_secundario = cs.id_color
            ORDER BY pt.fecha_registro DESC
        """)
        
        return cur.fetchall()
    
    finally:
        conn.close()

def crear_producto_desde_combinacion(id_combinacion, nombre_producto, 
                                     precio_sugerido, stock=0):
    """
    Crea un producto terminado a partir de una combinación guardada
    """
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cur = conn.cursor()
        
        # Obtener id_modelo de la combinación
        cur.execute("SELECT id_modelo FROM combinaciones WHERE id_combinacion = ?", 
                   (id_combinacion,))
        resultado = cur.fetchone()
        
        if not resultado:
            return None
        
        id_modelo = resultado[0]
        
        # Insertar producto
        cur.execute("""
            INSERT INTO productos_terminados (
                id_modelo, id_combinacion, nombre_producto, 
                precio_sugerido, stock
            ) VALUES (?, ?, ?, ?, ?)
        """, (id_modelo, id_combinacion, nombre_producto, 
              precio_sugerido, stock))
        
        conn.commit()
        return cur.lastrowid
    
    finally:
        conn.close()

def obtener_paletas():
    """
    Obtiene todas las paletas con sus colores
    """
    conn = get_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                p.id_paleta,
                p.nombre,
                p.esquema,
                p.descripcion,
                GROUP_CONCAT(c.codigo_hex) as colores_hex,
                COUNT(c.id_color) as num_colores
            FROM paletas_colores p
            LEFT JOIN colores c ON p.id_paleta = c.id_paleta
            GROUP BY p.id_paleta
            ORDER BY p.nombre
        """)
        
        return cur.fetchall()
    
    finally:
        conn.close()

def obtener_colores_paleta(id_paleta):
    """
    Obtiene todos los colores de una paleta específica
    """
    conn = get_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id_color, nombre_color, codigo_hex
            FROM colores
            WHERE id_paleta = ?
            ORDER BY nombre_color
        """, (id_paleta,))
        
        return cur.fetchall()
    
    finally:
        conn.close()

def insertar_datos_ejemplo():
    """
    Inserta datos de ejemplo para pruebas
    """
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        
        # Insertar modelos básicos si no existen
        modelos = [
            ('Simple', 'simple', 'Bolsa de un solo color con asas', 30.0, 40.0),
            ('Combinado', 'combinado', 'Bolsa de dos colores 1/4 y 3/4', 30.0, 40.0),
            ('Especial', 'especial', 'Bolsa personalizada', 30.0, 40.0)
        ]
        
        for modelo in modelos:
            cur.execute("""
                INSERT OR IGNORE INTO modelos_bolsas 
                (nombre_modelo, tipo, descripcion, ancho, alto)
                VALUES (?, ?, ?, ?, ?)
            """, modelo)
        
        # Insertar paleta de ejemplo
        cur.execute("""
            INSERT OR IGNORE INTO paletas_colores (nombre, esquema, descripcion)
            VALUES ('Básica', 'armonico', 'Colores básicos')
        """)
        
        id_paleta = cur.lastrowid or 1
        
        # Colores básicos
        colores_basicos = [
            ('Rojo', '#FF0000'),
            ('Verde', '#00FF00'),
            ('Azul', '#0000FF'),
            ('Amarillo', '#FFFF00'),
            ('Rosa', '#FF69B4'),
            ('Blanco', '#FFFFFF'),
            ('Negro', '#000000')
        ]
        
        for nombre, hex_code in colores_basicos:
            cur.execute("""
                INSERT OR IGNORE INTO colores (nombre_color, codigo_hex, id_paleta)
                VALUES (?, ?, ?)
            """, (nombre, hex_code, id_paleta))
        
        conn.commit()
        return True
    
    except Exception as e:
        print(f"Error insertando datos de ejemplo: {e}")
        return False
    
    finally:
        conn.close()