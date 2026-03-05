@echo off
setlocal EnableExtensions
set "ROOT=%~dp0"
set "REPO_ROOT=%ROOT%.."
set "PYTHON_EXE=%LocalAppData%\Programs\Python\Python312\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"
echo ========================================
echo MAPEO FISICO DE PCs - Veyon (CON ADMIN)
echo ========================================
echo.
echo Este script mapea las IPs a los numeros fisicos reales
echo de los PCs en la sala de computacion.
echo.
echo Los nombres en Veyon reflejaran el orden fisico real (PC-00 a PC-15).
echo.
pause
pushd "%REPO_ROOT%" >nul
"%PYTHON_EXE%" scripts\principales\MAPEO_FISICO_ADMIN.py
popd >nul
pause

