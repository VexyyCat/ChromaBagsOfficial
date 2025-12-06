"""
Script para inicializar y configurar la base de datos
Ejecuta: python init_database.py
"""
import os
from db_connection import get_connection
from modules.db_helpers import insertar_datos_ejemplo

# ========================= VERIFICAR ESTRUCTURA =========================
def verificar_estructura_db():
    """
    Verifica que todas las tablas necesarias existan
    """
    conn = get_connection()
    if not conn:
        print("❌ No se pudo conectar a la base de datos")
        return False
    
    try:
        cur = conn.cursor()
        
        tablas_requeridas = [
            'clientes', 'modelos_bolsas', 'colores', 
            'paletas_colores', 'combinaciones', 
            'productos_terminados', 'materiales',
            'cotizaciones', 'detalle_cotizacion',
            'pedidos', 'detalle_pedido', 'pagos', 'facturas'
        ]
        
        cur.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table'
        """)
        
        tablas_existentes = [row[0] for row in cur.fetchall()]
        
        print("\n📋 Verificando estructura de base de datos...")
        print("-" * 50)
        
        todas_ok = True
        for tabla in tablas_requeridas:
            existe = tabla in tablas_existentes
            icono = "✓" if existe else "✗"
            print(f"{icono} Tabla '{tabla}': {'OK' if existe else 'FALTA'}")
            if not existe:
                todas_ok = False
        
        print("-" * 50)
        
        if todas_ok:
            print("✅ Todas las tablas requeridas existen")
        else:
            print("⚠️  Algunas tablas faltan. Se crearán ahora...")
        
        return todas_ok
    
    finally:
        conn.close()

# ========================= ACTUALIZAR CLIENTES =========================
def actualizar_tabla_clientes():
    """
    Agrega columnas de datos fiscales a la tabla clientes
    """
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    print("\n🔧 Actualizando tabla clientes con campos fiscales...")
    
    columnas_fiscales = [
        ("rfc", "TEXT"),
        ("razon_social", "TEXT"),
        ("uso_cfdi", "TEXT"),
        ("regimen_fiscal", "TEXT"),
        ("correo_facturacion", "TEXT")
    ]
    
    for columna, tipo in columnas_fiscales:
        try:
            cur.execute(f"ALTER TABLE clientes ADD COLUMN {columna} {tipo};")
            print(f"  ✅ Columna '{columna}' agregada")
        except Exception as e:
            if "duplicate column" in str(e).lower():
                print(f"  ℹ️  Columna '{columna}' ya existe")
            else:
                print(f"  ⚠️  Error con '{columna}': {e}")
    
    conn.commit()
    conn.close()
    print("✅ Tabla clientes actualizada")
    return True

# ========================= CREAR TABLAS =========================
def crear_tablas():
    """
    Crea todas las tablas necesarias del sistema
    """
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    print("\n🧱 Creando tablas del sistema...")

    # -------- COTIZACIONES --------
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cotizaciones (
                id_cotizacion INTEGER PRIMARY KEY AUTOINCREMENT,
                id_cliente INTEGER NOT NULL,
                fecha_emision TEXT DEFAULT (datetime('now','localtime')),
                total_estimado REAL NOT NULL,
                estado TEXT DEFAULT 'pendiente',
                FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
            );
        """)
        print("  ✅ Tabla 'cotizaciones' lista")
    except Exception as e:
        print(f"  ⚠️  Error con 'cotizaciones': {e}")

    # -------- DETALLE_COTIZACION --------
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS detalle_cotizacion (
                id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
                id_cotizacion INTEGER NOT NULL,
                id_material INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                costo_unitario REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (id_cotizacion) REFERENCES cotizaciones(id_cotizacion)
            );
        """)
        print("  ✅ Tabla 'detalle_cotizacion' lista")
    except Exception as e:
        print(f"  ⚠️  Error con 'detalle_cotizacion': {e}")

    # -------- PEDIDOS --------
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
                id_cliente INTEGER NOT NULL,
                fecha_pedido TEXT DEFAULT (datetime('now','localtime')),
                fecha_entrega TEXT,
                estado TEXT DEFAULT 'pendiente',
                total REAL NOT NULL,
                FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
            );
        """)
        print("  ✅ Tabla 'pedidos' lista")
    except Exception as e:
        print(f"  ⚠️  Error con 'pedidos': {e}")

    # -------- DETALLE_PEDIDO --------
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS detalle_pedido (
                id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
                id_pedido INTEGER NOT NULL,
                id_producto INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido)
            );
        """)
        print("  ✅ Tabla 'detalle_pedido' lista")
    except Exception as e:
        print(f"  ⚠️  Error con 'detalle_pedido': {e}")

    # -------- PAGOS --------
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pagos (
                id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
                id_pedido INTEGER NOT NULL,
                fecha_pago TEXT DEFAULT (datetime('now','localtime')),
                monto REAL NOT NULL,
                metodo TEXT NOT NULL,
                referencia TEXT,
                observaciones TEXT,
                FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido)
            );
        """)
        print("  ✅ Tabla 'pagos' lista")
    except Exception as e:
        print(f"  ⚠️  Error con 'pagos': {e}")

    # -------- FACTURAS --------
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS facturas (
                id_factura INTEGER PRIMARY KEY AUTOINCREMENT,
                id_pedido INTEGER NOT NULL,
                fecha_factura TEXT DEFAULT (datetime('now','localtime')),
                folio TEXT NOT NULL,
                total REAL NOT NULL,
                rfc TEXT NOT NULL,
                razon_social TEXT NOT NULL,
                uso_cfdi TEXT NOT NULL,
                regimen_fiscal TEXT NOT NULL,
                correo_facturacion TEXT NOT NULL,
                estado TEXT DEFAULT 'emitida',
                ruta_pdf TEXT,
                FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido)
            );
        """)
        print("  ✅ Tabla 'facturas' lista")
    except Exception as e:
        print(f"  ⚠️  Error con 'facturas': {e}")

    conn.commit()
    conn.close()
    print("✅ Todas las tablas creadas correctamente")
    return True

# ========================= CONTAR REGISTROS =========================
def contar_registros():
    """
    Cuenta registros en las tablas principales
    """
    conn = get_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        
        print("\n📊 Resumen de datos en la base de datos:")
        print("-" * 50)
        
        tablas = [
            ('clientes', 'Clientes'),
            ('modelos_bolsas', 'Modelos de bolsas'),
            ('paletas_colores', 'Paletas de colores'),
            ('colores', 'Colores'),
            ('combinaciones', 'Combinaciones guardadas'),
            ('productos_terminados', 'Productos en catálogo'),
            ('cotizaciones', 'Cotizaciones'),
            ('pedidos', 'Pedidos'),
            ('pagos', 'Pagos registrados'),
            ('facturas', 'Facturas emitidas')
        ]
        
        for tabla, nombre in tablas:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = cur.fetchone()[0]
                print(f"  {nombre}: {count} registros")
            except Exception as e:
                print(f"  {nombre}: Tabla no existe")
        
        print("-" * 50)
    
    finally:
        conn.close()

def inicializar_datos_base():
    """
    Inicializa datos básicos si no existen
    """
    print("\n🔧 Inicializando datos básicos...")
    print("-" * 50)
    
    if insertar_datos_ejemplo():
        print("✅ Datos básicos insertados correctamente")
        print("   - Modelos: Simple, Combinado, Especial")
        print("   - Paleta básica con 7 colores")
    else:
        print("⚠️  Error al insertar datos básicos")
    
    print("-" * 50)

def verificar_permisos():
    """
    Verifica permisos de lectura/escritura en el directorio database
    """
    db_path = os.path.join('database', 'ChromaBags.db')
    db_dir = os.path.dirname(db_path)
    
    print("\n🔐 Verificando permisos...")
    print("-" * 50)
    
    # Verificar que existe el directorio
    if not os.path.exists(db_dir):
        print(f"❌ El directorio '{db_dir}' no existe")
        print(f"   Creando directorio...")
        try:
            os.makedirs(db_dir, exist_ok=True)
            print(f"✅ Directorio '{db_dir}' creado")
        except Exception as e:
            print(f"❌ Error creando directorio: {e}")
            return False
    
    # Verificar permisos de lectura
    if os.access(db_dir, os.R_OK):
        print(f"✓ Permisos de lectura: OK")
    else:
        print(f"✗ Permisos de lectura: FALTA")
        return False
    
    # Verificar permisos de escritura
    if os.access(db_dir, os.W_OK):
        print(f"✓ Permisos de escritura: OK")
    else:
        print(f"✗ Permisos de escritura: FALTA")
        return False
    
    # Verificar que existe el archivo .db
    if os.path.exists(db_path):
        size_mb = os.path.getsize(db_path) / (1024 * 1024)
        print(f"✓ Archivo de base de datos: {db_path} ({size_mb:.2f} MB)")
    else:
        print(f"⚠️  Archivo de base de datos no encontrado: {db_path}")
        print(f"   Se creará al ejecutar la aplicación")
    
    print("-" * 50)
    return True

def main():
    """
    Función principal de inicialización
    """
    print("\n" + "=" * 50)
    print("   INICIALIZACIÓN DE BASE DE DATOS - CHROMABAGS")
    print("=" * 50)
    
    # 1. Verificar permisos
    if not verificar_permisos():
        print("\n❌ Error: Problemas con permisos del sistema")
        return
    
    # 2. Actualizar tabla clientes con campos fiscales
    print("\n🔄 Actualizando estructura de la base de datos...")
    actualizar_tabla_clientes()
    
    # 3. Crear tablas nuevas (pagos, facturas, etc.)
    crear_tablas()
    
    # 4. Verificar estructura
    if not verificar_estructura_db():
        print("\n⚠️  Advertencia: La estructura de la BD está incompleta")
        print("   Asegúrate de que el archivo ChromaBags.db es correcto")
    
    # 5. Contar registros existentes
    contar_registros()
    
    # 6. Preguntar si insertar datos de ejemplo
    conn = get_connection()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute("SELECT COUNT(*) FROM modelos_bolsas")
            count = cur.fetchone()[0]
            conn.close()
            
            if count == 0:
                print("\n💡 No se encontraron modelos de bolsas.")
                respuesta = input("¿Deseas insertar datos de ejemplo? (s/n): ")
                if respuesta.lower() == 's':
                    inicializar_datos_base()
                    contar_registros()
            else:
                print("\n✅ La base de datos ya tiene datos iniciales")
        except Exception as e:
            print(f"\n⚠️  Error verificando datos: {e}")
            conn.close()
    
    print("\n" + "=" * 50)
    print("   ✅ INICIALIZACIÓN COMPLETADA")
    print("=" * 50)
    print("\n📌 Próximos pasos:")
    print("   1. Ejecuta: python app.py")
    print("   2. Abre: http://127.0.0.1:5050")
    print("   3. ¡Comienza a gestionar ChromaBags!")
    print("\n")

if __name__ == "__main__":
    main()