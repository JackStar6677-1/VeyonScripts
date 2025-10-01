@echo off
echo ========================================
echo    Veyon - Mapeo Fisico GUI (Simple)
echo ========================================
echo.
echo Iniciando interfaz grafica simplificada...
echo.

REM Verificar si Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo Por favor instala Python 3.7 o superior
    pause
    exit /b 1
)

REM Verificar si Veyon esta instalado
if not exist "C:\Program Files\Veyon\veyon-cli.exe" (
    echo ERROR: Veyon no encontrado en la ubicacion predeterminada
    echo Por favor instala Veyon o verifica la ruta
    pause
    exit /b 1
)

REM Ejecutar la GUI simplificada
python physical_mapping_gui_simple.py

if errorlevel 1 (
    echo.
    echo ERROR: Error ejecutando la GUI
    echo Verifica que todos los archivos esten presentes
    pause
)

echo.
echo Presiona cualquier tecla para salir...
pause >nul
