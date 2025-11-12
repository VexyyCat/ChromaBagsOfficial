import sqlite3
import os

def get_connection():
    """
    Establece conexión con la base de datos SQLite3
    """
    try:
        db_path = os.path.join('database', 'ChromaBags.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Para acceder a las columnas por nombre
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None