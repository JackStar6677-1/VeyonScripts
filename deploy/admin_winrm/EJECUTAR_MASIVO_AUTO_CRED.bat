@echo off
setlocal EnableExtensions
title Ejecutar Masivo (Auto usuario + misma clave)

if /I not "%~1"=="--elevated" (
    net session >nul 2>&1
    if not %errorlevel%==0 (
        echo [INFO] Solicitando permisos de administrador...
        powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -Verb RunAs -FilePath '%~f0' -ArgumentList '--elevated'"
        if errorlevel 1 (
            echo [ERROR] UAC cancelado.
            pause
        )
        exit /b
    )
)

set "ROOT=%~dp0"
set "PS1=%ROOT%EJECUTAR_MASIVO_AUTO_CRED.ps1"

if not exist "%PS1%" (
    echo [ERROR] No se encontro: %PS1%
    pause
    exit /b 1
)

pushd "%ROOT%" >nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%"
set "RC=%errorlevel%"
popd >nul

echo.
if "%RC%"=="0" (
    echo [OK] Proceso finalizado.
) else (
    echo [ERROR] El proceso termino con codigo %RC%.
)
echo.
pause
exit /b %RC%
