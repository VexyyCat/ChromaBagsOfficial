@echo off
title ChromaBags - Sistema de Gestion
color 0D
cls
echo.
echo  ========================================
echo     ChromaBags - Sistema Integral
echo  ========================================
echo.
echo  Verificando entorno...
echo.

:: Verificar si Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo  [ERROR] Python no esta instalado o no esta en el PATH
    echo  Por favor, instala Python desde https://www.python.org/
    echo.
    pause
    exit /b 1
)

:: Activar entorno virtual si existe
if exist venv\Scripts\activate.bat (
    echo  [OK] Activando entorno virtual...
    call venv\Scripts\activate.bat
) else (
    echo  [INFO] No se encontro entorno virtual
    echo  [INFO] Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        color 0C
        echo  [ERROR] No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
    call venv\Scripts\activate.bat
    echo  [OK] Entorno virtual creado
)

echo.
echo  ========================================
echo     Instalando/Actualizando dependencias
echo  ========================================
echo.

:: Actualizar pip
echo  [*] Actualizando pip...
python -m pip install --upgrade pip --quiet

:: Instalar dependencias desde requirements.txt
if exist requirements.txt (
    echo  [*] Instalando dependencias desde requirements.txt...
    pip install -r requirements.txt --quiet
    if errorlevel 1 (
        color 0E
        echo  [ADVERTENCIA] Hubo problemas instalando algunas dependencias
        echo  Intentando continuar...
    ) else (
        echo  [OK] Dependencias instaladas correctamente
    )
) else (
    color 0E
    echo  [ADVERTENCIA] No se encontro requirements.txt
    echo  Instalando dependencias basicas...
    pip install flask reportlab openpyxl pywebview --quiet
)

echo.
echo  ========================================
echo     Iniciando aplicacion ChromaBags
echo  ========================================
echo.

:: Verificar si existe launcher.py
if not exist launcher.py (
    if not exist app.py (
        color 0C
        echo  [ERROR] No se encontro launcher.py ni app.py
        echo  Asegurate de estar en el directorio correcto
        pause
        exit /b 1
    )
    echo  [INFO] Usando app.py directamente...
    python app.py
) else (
    echo  [*] Iniciando launcher...
    python launcher.py
)

:: Si hay error al ejecutar
if errorlevel 1 (
    color 0C
    echo.
    echo  [ERROR] Hubo un problema al ejecutar la aplicacion
    echo  Revisa los mensajes de error arriba
    echo.
)

pause