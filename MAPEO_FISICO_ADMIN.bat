@echo off
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
python scripts\principales\MAPEO_FISICO_ADMIN.py
pause

