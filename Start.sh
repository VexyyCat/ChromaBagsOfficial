#!/bin/bash

# ChromaBags - Sistema Integral de Gestión
# Script de inicio para Linux/macOS

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
clear
echo -e "${PURPLE}"
cat << "EOF"
  ========================================
    ____  _                              
   / ___|| |__  _ __ ___  _ __ ___   ___ 
  | |    | '_ \| '__/ _ \| '_ ` _ \ / _ \
  | |___ | | | | | | (_) | | | | | |  __/
   \____||_| |_|_|  \___/|_| |_| |_|\___|
      ____                                
     |  _ \                               
     | |_) |  __ _   __ _  ___           
     |  _ <  / _` | / _` |/ __|          
     | |_) | (_| | (_| |\__ \          
     |____/ \__,_|\__, |___/          
                   __/ |                  
                  |___/                   
  ========================================
  Sistema Integral de Gestión
  ========================================
EOF
echo -e "${NC}"

# Función para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Función para detectar el sistema operativo
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

OS=$(detect_os)

echo -e "${CYAN}[INFO]${NC} Sistema operativo detectado: $OS"
echo ""

# Verificar Python
echo -e "${CYAN}[*]${NC} Verificando instalación de Python..."

PYTHON_CMD=""

# Buscar Python 3
if command_exists python3; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}[OK]${NC} Python 3 encontrado: $PYTHON_VERSION"
elif command_exists python; then
    # Verificar si es Python 3
    PY_VERSION=$(python --version 2>&1)
    if [[ $PY_VERSION == *"Python 3"* ]]; then
        PYTHON_CMD="python"
        PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
        echo -e "${GREEN}[OK]${NC} Python encontrado: $PYTHON_VERSION"
    else
        echo -e "${RED}[ERROR]${NC} Python 2 detectado. Se requiere Python 3.8+"
        PYTHON_CMD=""
    fi
fi

# Si no hay Python, intentar instalarlo
if [ -z "$PYTHON_CMD" ]; then
    echo -e "${YELLOW}[ADVERTENCIA]${NC} Python 3 no está instalado"
    echo ""
    echo "Para instalar Python 3:"
    echo ""
    
    if [ "$OS" == "linux" ]; then
        echo "Ubuntu/Debian:"
        echo "  sudo apt update"
        echo "  sudo apt install python3 python3-pip python3-venv"
        echo ""
        echo "Fedora/RHEL:"
        echo "  sudo dnf install python3 python3-pip"
        echo ""
        echo "Arch Linux:"
        echo "  sudo pacman -S python python-pip"
    elif [ "$OS" == "macos" ]; then
        echo "macOS (usando Homebrew):"
        echo "  brew install python3"
        echo ""
        echo "O descarga desde: https://www.python.org/downloads/"
    fi
    
    echo ""
    read -p "¿Deseas que el script intente instalar Python automáticamente? (s/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        if [ "$OS" == "linux" ]; then
            echo -e "${CYAN}[*]${NC} Intentando instalar Python 3..."
            
            # Detectar el gestor de paquetes
            if command_exists apt-get; then
                sudo apt-get update
                sudo apt-get install -y python3 python3-pip python3-venv
            elif command_exists dnf; then
                sudo dnf install -y python3 python3-pip
            elif command_exists yum; then
                sudo yum install -y python3 python3-pip
            elif command_exists pacman; then
                sudo pacman -S --noconfirm python python-pip
            else
                echo -e "${RED}[ERROR]${NC} No se pudo detectar el gestor de paquetes"
                exit 1
            fi
            
            # Verificar instalación
            if command_exists python3; then
                PYTHON_CMD="python3"
                echo -e "${GREEN}[OK]${NC} Python 3 instalado correctamente"
            else
                echo -e "${RED}[ERROR]${NC} Falló la instalación de Python 3"
                exit 1
            fi
            
        elif [ "$OS" == "macos" ]; then
            if command_exists brew; then
                echo -e "${CYAN}[*]${NC} Instalando Python 3 con Homebrew..."
                brew install python3
                PYTHON_CMD="python3"
            else
                echo -e "${RED}[ERROR]${NC} Homebrew no está instalado"
                echo "Instala Homebrew desde: https://brew.sh/"
                exit 1
            fi
        fi
    else
        echo -e "${RED}[ERROR]${NC} Python 3 es requerido para ejecutar ChromaBags"
        exit 1
    fi
fi

echo ""

# Verificar versión de Python (debe ser 3.8+)
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}[ERROR]${NC} Se requiere Python $REQUIRED_VERSION o superior"
    echo "Versión actual: $PYTHON_VERSION"
    exit 1
fi

# Verificar/Crear entorno virtual
echo -e "${CYAN}[*]${NC} Verificando entorno virtual..."

if [ ! -d "venv" ]; then
    echo -e "${CYAN}[*]${NC} Creando entorno virtual..."
    $PYTHON_CMD -m venv venv
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[OK]${NC} Entorno virtual creado"
    else
        echo -e "${RED}[ERROR]${NC} No se pudo crear el entorno virtual"
        exit 1
    fi
else
    echo -e "${GREEN}[OK]${NC} Entorno virtual encontrado"
fi

# Activar entorno virtual
echo -e "${CYAN}[*]${NC} Activando entorno virtual..."
source venv/bin/activate

if [ $? -eq 0 ]; then
    echo -e "${GREEN}[OK]${NC} Entorno virtual activado"
else
    echo -e "${RED}[ERROR]${NC} No se pudo activar el entorno virtual"
    exit 1
fi

echo ""
echo "========================================"
echo "  Instalando/Actualizando dependencias"
echo "========================================"
echo ""

# Actualizar pip
echo -e "${CYAN}[*]${NC} Actualizando pip..."
pip install --upgrade pip --quiet

# Instalar dependencias
if [ -f "requirements.txt" ]; then
    echo -e "${CYAN}[*]${NC} Instalando dependencias desde requirements.txt..."
    pip install -r requirements.txt --quiet
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[OK]${NC} Dependencias instaladas correctamente"
    else
        echo -e "${YELLOW}[ADVERTENCIA]${NC} Hubo problemas instalando algunas dependencias"
        echo "Intentando continuar..."
    fi
else
    echo -e "${YELLOW}[ADVERTENCIA]${NC} No se encontró requirements.txt"
    echo -e "${CYAN}[*]${NC} Instalando dependencias básicas..."
    pip install flask reportlab openpyxl pywebview --quiet
fi

echo ""
echo "========================================"
echo "  Iniciando ChromaBags"
echo "========================================"
echo ""

# Verificar si existe el logo
if [ -f "logo.ico" ] || [ -f "static/images/logo.ico" ]; then
    echo -e "${GREEN}[OK]${NC} Icono encontrado"
else
    echo -e "${YELLOW}[ADVERTENCIA]${NC} No se encontró logo.ico"
fi

# Verificar archivos necesarios
if [ ! -f "launcher.py" ] && [ ! -f "app.py" ]; then
    echo -e "${RED}[ERROR]${NC} No se encontró launcher.py ni app.py"
    echo "Asegúrate de estar en el directorio correcto"
    exit 1
fi

# Iniciar aplicación
if [ -f "launcher.py" ]; then
    echo -e "${CYAN}[*]${NC} Iniciando ChromaBags con launcher..."
    echo ""
    $PYTHON_CMD launcher.py
else
    echo -e "${CYAN}[*]${NC} Iniciando ChromaBags con app.py..."
    echo ""
    $PYTHON_CMD app.py
fi

# Verificar si hubo error
if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}[ERROR]${NC} Hubo un problema al ejecutar la aplicación"
    echo "Revisa los mensajes de error arriba"
    exit 1
fi

echo ""
echo -e "${GREEN}Aplicación cerrada correctamente${NC}"