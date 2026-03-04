@echo off
set "PYTHON_EXE=%LocalAppData%\Programs\Python\Python312\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"
echo ========================================
echo VEYON MAESTRO - Solo Actualizar
echo ========================================
echo.
echo Este script SOLO actualiza Veyon con WakeMeOnLAN
echo SIN BORRAR la configuracion existente.
echo.
pause
"%PYTHON_EXE%" scripts\principales\VEYON_MAESTRO.py
pause

