@echo off
:: Informacion del Sistema - No requiere permisos de administrador

echo ========================================
echo INFORMACION DEL SISTEMA
echo ========================================
echo.

:: Cambiar al directorio del script
cd /d "%~dp0"

:: Verificar si psutil esta instalado
python -c "import psutil" 2>nul
if %errorLevel% neq 0 (
    echo ADVERTENCIA: psutil no esta instalado
    echo.
    echo Instalando psutil...
    pip install psutil
    echo.
)

:: Ejecutar script de Python
python INFO_SISTEMA.py

:: Mantener ventana abierta
pause

exit /b

