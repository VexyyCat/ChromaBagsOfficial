"""
Script para inicializar y configurar la base de datos
Ejecuta: python init_database.py
"""
import os
from db_connection import get_connection
from modules.db_helpers import insertar_datos_ejemplo

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
            'productos_terminados', 'materiales'
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
            print("⚠️  Algunas tablas faltan. Verifica tu archivo .db")
        
        return todas_ok
    
    finally:
        conn.close()

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
            ('productos_terminados', 'Productos en catálogo')
        ]
        
        for tabla, nombre in tablas:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = cur.fetchone()[0]
                print(f"  {nombre}: {count} registros")
            except Exception as e:
                print(f"  {nombre}: Error - {e}")
        
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
    
    # 2. Verificar estructura
    if not verificar_estructura_db():
        print("\n⚠️  Advertencia: La estructura de la BD está incompleta")
        print("   Asegúrate de que el archivo ChromaBags.db es correcto")
        return
    
    # 3. Contar registros existentes
    contar_registros()
    
    # 4. Preguntar si insertar datos de ejemplo
    conn = get_connection()
    if conn:
        cur = conn.cursor()
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
    
    print("\n" + "=" * 50)
    print("   ✅ INICIALIZACIÓN COMPLETADA")
    print("=" * 50)
    print("\n📌 Próximos pasos:")
    print("   1. Ejecuta: python app.py")
    print("   2. Abre: http://127.0.0.1:5050/diseno_color")
    print("   3. Comienza a diseñar tus bolsas!")
    print("\n")

if __name__ == "__main__":
    main()