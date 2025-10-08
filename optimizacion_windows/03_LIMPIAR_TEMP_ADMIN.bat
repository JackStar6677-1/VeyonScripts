@echo off
:: Limpiar Archivos Temporales - Launcher con permisos de administrador

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
echo LIMPIAR ARCHIVOS TEMPORALES
echo ========================================
echo.

:: Cambiar al directorio del script
cd /d "%~dp0"

:: Ejecutar script de Python
python 03_limpiar_archivos_temp.py

:: Mantener ventana abierta
if %errorLevel% neq 0 (
    echo.
    echo ERROR: El script finalizo con errores
    pause
)

exit /b

