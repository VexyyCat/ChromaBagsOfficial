"""
Script para agregar campos fiscales a la tabla clientes
Ejecutar: python actualizar_db_clientes.py
"""
from db_connection import get_connection

def agregar_campos_fiscales():
    """Agrega campos fiscales a la tabla clientes si no existen"""
    conn = get_connection()
    if not conn:
        print("❌ No se pudo conectar a la base de datos")
        return False
    
    try:
        cur = conn.cursor()
        
        # Lista de campos a agregar
        campos_fiscales = [
            ("rfc", "TEXT"),
            ("razon_social", "TEXT"),
            ("uso_cfdi", "TEXT"),
            ("regimen_fiscal", "TEXT"),
            ("correo_facturacion", "TEXT")
        ]
        
        print("📋 Verificando campos fiscales en tabla clientes...")
        print("-" * 50)
        
        for campo, tipo in campos_fiscales:
            try:
                cur.execute(f"ALTER TABLE clientes ADD COLUMN {campo} {tipo}")
                conn.commit()
                print(f"✅ Campo '{campo}' agregado correctamente")
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    print(f"ℹ️  Campo '{campo}' ya existe")
                else:
                    print(f"⚠️  Error con campo '{campo}': {e}")
        
        print("-" * 50)
        print("✅ Actualización completada")
        
        # Verificar estructura final
        cur.execute("PRAGMA table_info(clientes)")
        columnas = cur.fetchall()
        
        print("\n📊 Estructura actual de la tabla clientes:")
        print("-" * 50)
        for col in columnas:
            print(f"  • {col[1]} ({col[2]})")
        print("-" * 50)
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error actualizando base de datos: {e}")
        if conn:
            conn.close()
        return False

if __name__ == "__main__":
    print("🔧 Actualizando base de datos - Campos Fiscales")
    print("=" * 50)
    agregar_campos_fiscales()
    print("\n✅ Proceso terminado. Puedes ejecutar tu aplicación ahora.")
