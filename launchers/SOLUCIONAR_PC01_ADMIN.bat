@echo off
echo ================================================================
echo SOLUCIONADOR DE PROBLEMAS PC-01 - CON PERMISOS DE ADMINISTRADOR
echo ================================================================
echo.

echo Verificando permisos de administrador...
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Este script debe ejecutarse como administrador
    echo.
    echo Haciendo clic derecho en este archivo y seleccionar "Ejecutar como administrador"
    pause
    exit /b 1
)

echo Permisos de administrador verificados
echo.

echo Ejecutando solucionador de problemas PC-01...
python scripts\soluciones\solucionar_clon_pc01.py

echo.
echo ================================================================
echo SOLUCIÓN COMPLETADA
echo ================================================================
pause
