"""
ChromaBags Desktop App
Aplicación de escritorio usando PyWebView
"""
import webview
import threading
import time
import sys
import os
from pathlib import Path

def run_flask():
    """Ejecuta Flask en un thread separado"""
    from app import app
    app.run(debug=False, host="127.0.0.1", port=5050, use_reloader=False)

class API:
    """API para comunicación entre JavaScript y Python"""
    
    def cerrar_aplicacion(self):
        """Permite cerrar desde JavaScript"""
        window.destroy()     # Cierra la ventana
        return True

def on_closing():
    result = window.create_confirmation_dialog(
        'Cerrar ChromaBags',
        '¿Estás seguro de que deseas cerrar la aplicación?'
    )
    return result

def main():
    global window
    
    # Buscar el icono en diferentes ubicaciones posibles
    icon_paths = [
        'logo.ico',                          # Raíz del proyecto
        'static/images/logo_chromabags.png',            # Carpeta static/images
        'static/logo.ico',                   # Carpeta static
        os.path.join(os.path.dirname(__file__), 'logo.ico'),  # Mismo directorio que launcher.py
    ]
    
    icon_path = None
    for path in icon_paths:
        if os.path.exists(path):
            icon_path = path
            print(f"✓ Icono encontrado: {path}")
            break
    
    if not icon_path:
        print("⚠ Advertencia: No se encontró logo.ico")
        print("  Coloca logo.ico en la raíz del proyecto o en static/images/")
    
    # Iniciar Flask en background
    print("🚀 Iniciando servidor Flask...")
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Esperar a que Flask inicie
    time.sleep(2)
    print("✓ Servidor Flask iniciado en http://127.0.0.1:5050")
    
    # Crear API para comunicación
    api = API()
    
    # Crear ventana de la aplicación
    print("🎨 Creando ventana de la aplicación...")
    window = webview.create_window(
        title='ChromaBags - Sistema de Gestión',
        url='http://127.0.0.1:5050',
        width=1400,
        height=900,
        resizable=True,
        fullscreen=False,
        min_size=(1200, 700),
        background_color='#FFE4E1',  # Color de fondo mientras carga
        text_select=True,             # Permitir seleccionar texto
        js_api=api                    # API para JavaScript
    )
    
    # Configurar el icono si existe
    if icon_path:
        try:
            # PyWebView acepta la ruta del icono directamente
            # Nota: esto debe hacerse antes de webview.start()
            pass  # El icono se configura en create_window en versiones nuevas
        except Exception as e:
            print(f"⚠ No se pudo configurar el icono: {e}")
    
    # Configurar el evento de cierre
    window.events.closing += on_closing
    
    print("✓ Ventana creada. Iniciando aplicación...")
    
    # Iniciar la aplicación
    webview.start(
        debug=False,  # Cambiar a True para debugging
        http_server=False  # Usar el servidor Flask
    )

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠ Aplicación interrumpida por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)