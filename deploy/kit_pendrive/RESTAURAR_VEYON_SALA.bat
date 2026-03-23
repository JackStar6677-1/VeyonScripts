@echo off
setlocal
title Restaurar Veyon Sala
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0RESTAURAR_VEYON_SALA.ps1"
pause
