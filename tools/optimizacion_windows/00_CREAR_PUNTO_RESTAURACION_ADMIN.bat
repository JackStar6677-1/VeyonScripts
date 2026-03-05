@echo off
:: Crear Punto de Restauracion - Launcher con permisos de administrador

:: Verificar si se ejecuta como administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :admin
) else (
    goto :solicitar_admin
)

:solicitar_admin
echo Solicitando permisos de administrador...
powershell -Command "Start-Process '%~f0' -Verb RunAs"
exit /b

:admin
echo ========================================
echo CREAR PUNTO DE RESTAURACION
echo ========================================
echo.

:: Cambiar al directorio del script
cd /d "%~dp0"

:: Ejecutar script de Python
python 00_CREAR_PUNTO_RESTAURACION.py

:: Mantener ventana abierta
if %errorLevel% neq 0 (
    echo.
    echo ERROR: El script finalizo con errores
    pause
)

exit /b

