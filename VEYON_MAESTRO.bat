@echo off
setlocal EnableExtensions
title VEYON MAESTRO - Actualizar dispositivos

set "ROOT=%~dp0"
set "SCRIPT=%ROOT%scripts\principales\VEYON_MAESTRO.py"
set "LOG=%TEMP%\VEYON_MAESTRO_launcher.log"

if /I "%~1"=="--elevated" goto run

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Solicitando permisos de administrador...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process '%~f0' -Verb RunAs -ArgumentList '--elevated'"
    exit /b
)

:run
if not exist "%SCRIPT%" (
    echo [ERROR] No se encontro el script: "%SCRIPT%"
    pause
    exit /b 1
)

set "PYTHON_EXE=%LocalAppData%\Programs\Python\Python312\python.exe"
if not exist "%PYTHON_EXE%" (
    py -3.12 -V >nul 2>&1 && set "PYTHON_EXE=py -3.12"
)
if not exist "%LocalAppData%\Programs\Python\Python312\python.exe" (
    if /I "%PYTHON_EXE%"=="%LocalAppData%\Programs\Python\Python312\python.exe" (
        py -3 -V >nul 2>&1 && set "PYTHON_EXE=py -3"
    )
)
if not exist "%LocalAppData%\Programs\Python\Python312\python.exe" (
    if /I "%PYTHON_EXE%"=="%LocalAppData%\Programs\Python\Python312\python.exe" (
        py -V >nul 2>&1 && set "PYTHON_EXE=py"
    )
)
if not exist "%LocalAppData%\Programs\Python\Python312\python.exe" (
    if /I "%PYTHON_EXE%"=="%LocalAppData%\Programs\Python\Python312\python.exe" (
        set "PYTHON_EXE=python"
    )
)

echo ========================================
echo VEYON MAESTRO - Solo Actualizar
echo ========================================
echo [LOG] %LOG%
echo.
echo Este script actualiza Veyon con WakeMeOnLAN
echo sin borrar la configuracion existente.
echo.

pushd "%ROOT%" >nul
echo ===== %date% %time% ===== > "%LOG%"
echo Script: %SCRIPT% >> "%LOG%"
echo Python: %PYTHON_EXE% >> "%LOG%"
echo. >> "%LOG%"

set "PYTHONUNBUFFERED=1"
call %PYTHON_EXE% "%SCRIPT%"
set "RC=%errorlevel%"
popd >nul

echo.
if not "%RC%"=="0" (
    echo [ERROR] Fallo VEYON_MAESTRO.py (codigo %RC%)
    echo Revisa: %LOG%
) else (
    echo [OK] Ejecucion completada.
    echo Log: %LOG%
)
echo.
pause
exit /b %RC%

