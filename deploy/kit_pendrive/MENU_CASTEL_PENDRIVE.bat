@echo off
setlocal EnableExtensions
set "ROOT=%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%ROOT%MENU_CASTEL_PENDRIVE.ps1" -RootPath "%ROOT%"
endlocal
