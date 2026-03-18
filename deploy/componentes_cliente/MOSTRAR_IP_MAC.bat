@echo off
title IP y MAC del equipo
echo ==========================================
echo  IP Y MAC DEL EQUIPO
echo ==========================================
echo.
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-NetAdapter | Where-Object Status -eq 'Up' | ForEach-Object { $ip=(Get-NetIPAddress -AddressFamily IPv4 -InterfaceIndex $_.ifIndex -ErrorAction SilentlyContinue | Where-Object { $_.IPAddress -notlike '169.254*' } | Select-Object -ExpandProperty IPAddress -First 1); if($ip){ '{0}    {1}    {2}' -f $_.Name, $ip, $_.MacAddress } }"
echo.
pause
