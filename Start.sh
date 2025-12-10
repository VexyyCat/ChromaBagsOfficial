#!/bin/bash

# ChromaBags - Sistema Integral de Gestión (Linux)
# Script de inicio para Linux (LF + rutas correctas)

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

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

# Función para verificar comandos
command_exists() { command -v "$1" >/dev/null 2>&1; }

echo -e "${CYAN}[INFO]${NC} Sistema operativo detectado: Linux"
echo ""

# ------------------------------
# Verificar Python 3
# ------------------------------
echo -e "${CYAN}[*]${NC} Verificando instalación de Python..."

if command_exists python3; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    echo -e "${GREEN}[OK]${NC} Python encontrado: ${PYTHON_VERSION}"
else
    echo -e "${RED}[ERROR]${NC} Python3 no está instalado."
    echo "Instálalo con:"
    echo "  sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

# Verificar versión
REQUIRED_VERSION="3.8"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}[ERROR]${NC} Se requiere Python >= 3.8"
    exit 1
fi

# ------------------------------
# Crear / Activar entorno virtual
# ------------------------------
echo -e "${CYAN}[*]${NC} Verificando entorno virtual..."

if [ ! -d "venv" ]; then
    echo -e "${CYAN}[*]${NC} Creando entorno virtual..."
    $PYTHON_CMD -m venv venv || {
        echo -e "${RED}[ERROR]${NC} No se pudo crear venv"
        exit 1
    }
else
    echo -e "${GREEN}[OK]${NC} venv encontrado"
fi

echo -e "${CYAN}[*]${NC} Activando entorno virtual..."
source venv/bin/activate || {
    echo -e "${RED}[ERROR]${NC} No se pudo activar venv"
    exit 1
}

# ------------------------------
# Dependencias
# ------------------------------
echo ""
echo "========================================"
echo " Instalando/Actualizando dependencias"
echo "========================================"

pip install --upgrade pip --quiet

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet || \
        echo -e "${YELLOW}[ADVERTENCIA]${NC} Algunas dependencias fallaron"
else
    pip install flask reportlab openpyxl pywebview --quiet
fi

# ------------------------------
# Iniciar aplicación
# ------------------------------
echo ""
echo "========================================"
echo "   Iniciando ChromaBags"
echo "========================================"
echo ""

if [ -f "launcher.py" ]; then
    $PYTHON_CMD launcher.py
elif [ -f "app.py" ]; then
    $PYTHON_CMD app.py
else
    echo -e "${RED}[ERROR]${NC} No existe launcher.py ni app.py"
    exit 1
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR]${NC} Error ejecutando la aplicación"
    exit 1
fi

echo -e "${GREEN}Aplicación cerrada correctamente${NC}"
