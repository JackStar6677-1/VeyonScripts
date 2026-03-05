@echo off
setlocal EnableExtensions
title WINRM MAESTRO - Escaneo y verificacion

set "ROOT=%~dp0"
set "REPO_ROOT=%ROOT%.."
set "SCRIPT=%REPO_ROOT%\scripts\principales\WINRM_MAESTRO.py"
set "LOG=%TEMP%\WINRM_MAESTRO_launcher.log"

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
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"

pushd "%REPO_ROOT%" >nul
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
    echo [ERROR] Fallo WINRM_MAESTRO.py (codigo %RC%)
    echo Revisa: %LOG%
) else (
    echo [OK] Ejecucion completada.
)
echo.
pause
exit /b %RC%
