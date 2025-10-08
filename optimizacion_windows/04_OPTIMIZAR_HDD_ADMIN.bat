@echo off
:: Optimizar HDD - Launcher con permisos de administrador

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
echo OPTIMIZAR DISCO DURO (HDD)
echo ========================================
echo.

:: Cambiar al directorio del script
cd /d "%~dp0"

:: Ejecutar script de Python
python 04_optimizar_hdd.py

:: Mantener ventana abierta
if %errorLevel% neq 0 (
    echo.
    echo ERROR: El script finalizo con errores
    pause
)

exit /b

