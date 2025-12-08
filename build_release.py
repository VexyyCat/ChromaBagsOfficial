"""
Script para crear paquetes de distribución de ChromaBags
Genera archivos .zip listos para distribución
"""
import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

VERSION = "1.0.0"
APP_NAME = "ChromaBags"

def create_release_package():
    """Crea el paquete de distribución"""
    
    print("🎁 Creando paquete de distribución de ChromaBags")
    print("=" * 50)
    
    # Nombre del paquete
    timestamp = datetime.now().strftime("%Y%m%d")
    package_name = f"{APP_NAME}-v{VERSION}-{timestamp}"
    
    # Crear directorio temporal
    temp_dir = Path("dist") / package_name
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📦 Creando: {package_name}.zip")
    
    # Archivos y carpetas a incluir
    items_to_include = [
        # Archivos principales
        'app.py',
        'launcher.py',
        'launcher_webview.py',
        'db_connection.py',
        'requirements.txt',
        'README.md',
        'LICENSE',
        
        # Scripts de inicio
        'start_chromabags.bat',
        'start_chromabags.sh',
        'install.bat',
        'convert_icon.py',
        
        # Carpetas
        'modules/',
        'templates/',
        'static/',
        
        # Archivos opcionales
        'logo.ico',
        'chromabags.db',
    ]
    
    # Copiar archivos
    print("\n📋 Copiando archivos...")
    for item in items_to_include:
        src = Path(item)
        if src.exists():
            if src.is_file():
                dest = temp_dir / src.name
                shutil.copy2(src, dest)
                print(f"  ✓ {item}")
            elif src.is_dir():
                dest = temp_dir / src.name
                shutil.copytree(src, dest, dirs_exist_ok=True)
                print(f"  ✓ {item}")
        else:
            print(f"  ⚠ No encontrado: {item}")
    
    # Crear README de distribución
    create_distribution_readme(temp_dir)
    
    # Crear archivo ZIP
    print("\n📦 Comprimiendo archivos...")
    zip_path = Path("dist") / f"{package_name}.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            # Excluir __pycache__ y .pyc
            dirs[:] = [d for d in dirs if d != '__pycache__']
            
            for file in files:
                if not file.endswith('.pyc'):
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(temp_dir.parent)
                    zipf.write(file_path, arcname)
    
    # Limpiar directorio temporal
    shutil.rmtree(temp_dir)
    
    # Calcular tamaño
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    
    print("\n✅ Paquete creado exitosamente!")
    print(f"📍 Ubicación: {zip_path}")
    print(f"📊 Tamaño: {size_mb:.2f} MB")
    print("\n🚀 Listo para subir a GitHub Releases")

def create_distribution_readme(dest_dir):
    """Crea un README específico para distribución"""
    readme_content = f"""# ChromaBags v{VERSION}

## 🚀 Instalación Rápida

### Windows
1. Extrae este archivo ZIP
2. Ejecuta `start_chromabags.bat`
3. ¡Listo! El sistema se abrirá automáticamente

### Linux/macOS
1. Extrae este archivo ZIP
2. Abre terminal en la carpeta extraída
3. Ejecuta: `chmod +x start_chromabags.sh`
4. Ejecuta: `./start_chromabags.sh`

## 📋 Requisitos

- **Python 3.8 o superior**
- Si no tienes Python, el instalador te ayudará a instalarlo

## 📖 Documentación Completa

Visita: https://github.com/tu-usuario/chromabags

## 🆘 Soporte

- GitHub Issues: https://github.com/tu-usuario/chromabags/issues
- Email: contacto@chromabags.com

## 📄 Licencia

MIT License - Ver archivo LICENSE para más detalles

---

**ChromaBags v{VERSION}** - Desarrollado con ❤️ para confeccionistas
"""
    
    readme_path = dest_dir / "LEEME.txt"
    readme_path.write_text(readme_content, encoding='utf-8')
    print(f"  ✓ LEEME.txt")

def create_github_release_notes():
    """Crea notas de release para GitHub"""
    notes = f"""# ChromaBags v{VERSION}

## 🎉 Novedades

- ✨ Sistema completo de gestión para confeccionistas
- 🎨 Editor de diseño con teoría del color
- 💰 Cotizaciones automáticas con IVA
- 📦 Control de inventario en tiempo real
- 📊 Dashboard con reportes visuales
- 📄 Generación de facturas PDF

## 📦 Descargas

### Windows
- `ChromaBags-v{VERSION}-windows.zip` - Incluye instalador automático

### Linux/macOS
- `ChromaBags-v{VERSION}-unix.zip` - Script de instalación incluido

### Código Fuente
- `Source code (zip)`
- `Source code (tar.gz)`

## 📋 Requisitos

- Python 3.8 o superior
- 500 MB de espacio en disco
- Conexión a internet para instalación inicial

## 🚀 Instalación

### Windows
```batch
# Descomprimir y ejecutar:
start_chromabags.bat
```

### Linux/macOS
```bash
# Descomprimir y ejecutar:
chmod +x start_chromabags.sh
./start_chromabags.sh
```

## 📖 Documentación

- [Manual de Usuario](https://github.com/tu-usuario/chromabags/wiki)
- [Guía de Instalación](https://github.com/tu-usuario/chromabags/blob/main/docs/installation.md)
- [API Documentation](https://github.com/tu-usuario/chromabags/blob/main/docs/api.md)

## 🐛 Problemas Conocidos

Ninguno reportado en esta versión.

## 📝 Changelog

Ver [CHANGELOG.md](https://github.com/tu-usuario/chromabags/blob/main/CHANGELOG.md) para el historial completo de cambios.

## 🙏 Agradecimientos

Gracias a todos los que contribuyeron a esta release.

---

**Fecha de Release:** {datetime.now().strftime("%Y-%m-%d")}
"""
    
    release_notes_path = Path("dist") / "RELEASE_NOTES.md"
    release_notes_path.write_text(notes, encoding='utf-8')
    print(f"\n📝 Notas de release creadas: {release_notes_path}")

if __name__ == "__main__":
    try:
        # Crear directorio dist si no existe
        Path("dist").mkdir(exist_ok=True)
        
        # Crear paquete
        create_release_package()
        
        # Crear notas de release
        create_github_release_notes()
        
        print("\n" + "=" * 50)
        print("✅ ¡Paquete listo para distribución!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()