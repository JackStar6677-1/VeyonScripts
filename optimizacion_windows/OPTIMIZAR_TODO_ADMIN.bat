@echo off
:: Optimizacion Windows 11 - Launcher con permisos de administrador
:: Ejecuta el script maestro de optimizacion

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
echo OPTIMIZACION COMPLETA DE WINDOWS 11
echo ========================================
echo.
echo Ejecutando script maestro de optimizacion...
echo.

:: Cambiar al directorio del script
cd /d "%~dp0"

:: Ejecutar script de Python
python OPTIMIZAR_TODO.py

:: Mantener ventana abierta si hay error
if %errorLevel% neq 0 (
    echo.
    echo ERROR: El script finalizo con errores
    pause
)

exit /b

