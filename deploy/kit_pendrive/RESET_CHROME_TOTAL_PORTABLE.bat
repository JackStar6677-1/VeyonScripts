@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0RESET_CHROME_TOTAL_PORTABLE.ps1" -IncludeMachinePolicies
pause
