@echo off
setlocal EnableExtensions
title Preparar Gestion Remota - Windows 10

rem ==========================================================
rem CONFIGURACION OPCIONAL
rem ==========================================================
set "CREATE_SUPPORT_USER=0"
set "SUPPORT_USER=SoporteTI"
set "SUPPORT_PASS=Cambia_Esta_Clave_123!"

rem ==========================================================
rem VALIDAR ADMIN
rem ==========================================================
if /I not "%~1"=="--elevated" (
    net session >nul 2>&1
    if not %errorlevel%==0 (
        echo [INFO] Solicitando permisos de administrador...
        powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -Verb RunAs -FilePath 'cmd.exe' -ArgumentList '/c ""%~f0" --elevated""'"
        if errorlevel 1 (
            echo.
            echo [ERROR] No se pudo elevar o se cancelo el UAC.
            pause
        )
        exit /b
    )
)

echo.
echo ==========================================================
echo  PREPARANDO PC PARA GESTION REMOTA (WIN10)
echo ==========================================================
echo.

rem 1) Habilitar WinRM
echo [1/7] Habilitando WinRM...
winrm quickconfig -q >nul 2>&1
winrm set winrm/config/service "@{AllowUnencrypted=""false""}" >nul 2>&1
winrm set winrm/config/service/auth "@{Basic=""false""}" >nul 2>&1
sc config WinRM start= auto >nul 2>&1
sc start WinRM >nul 2>&1

rem 2) Habilitar WMI / Administracion remota en firewall
echo [2/7] Abriendo reglas de firewall necesarias...
netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=Yes >nul 2>&1
netsh advfirewall firewall set rule group="Windows Remote Management" new enable=Yes >nul 2>&1
netsh advfirewall firewall set rule group="File and Printer Sharing" new enable=Yes >nul 2>&1
netsh advfirewall firewall set rule group="Remote Service Management" new enable=Yes >nul 2>&1

rem 3) Servicios utiles para gestion remota
echo [3/7] Ajustando servicios...
sc config RemoteRegistry start= auto >nul 2>&1
sc start RemoteRegistry >nul 2>&1
sc config LanmanServer start= auto >nul 2>&1
sc start LanmanServer >nul 2>&1

rem 4) Permitir admin local remoto (token UAC)
echo [4/7] Aplicando politica de token UAC remoto...
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v LocalAccountTokenFilterPolicy /t REG_DWORD /d 1 /f >nul 2>&1

rem 5) Usuario tecnico opcional
echo [5/7] Usuario de soporte (opcional)...
if "%CREATE_SUPPORT_USER%"=="1" (
    net user "%SUPPORT_USER%" "%SUPPORT_PASS%" /add >nul 2>&1
    net localgroup Administradores "%SUPPORT_USER%" /add >nul 2>&1
    echo     Usuario "%SUPPORT_USER%" creado/agregado a Administradores.
) else (
    echo     Omitido (CREATE_SUPPORT_USER=0).
)

rem 6) Mostrar datos de red utiles
echo [6/7] Datos utiles del equipo:
for /f "tokens=2 delims==" %%A in ('wmic computersystem get name /value ^| find "="') do set "PC_NAME=%%A"
echo     Nombre PC: %PC_NAME%
for /f "tokens=2 delims=:" %%A in ('ipconfig ^| findstr /R /C:"IPv4"') do (
    set "IP_RAW=%%A"
    goto :showip
)
:showip
set "IP_RAW=%IP_RAW: =%"
echo     IPv4 (primera): %IP_RAW%

rem 7) Prueba local WinRM
echo [7/7] Probando WinRM local...
winrm id >nul 2>&1
if %errorlevel%==0 (
    echo     WinRM OK.
) else (
    echo     WinRM no respondio. Revisa politicas/firewall.
)

echo.
echo ==========================================================
echo  LISTO
echo ==========================================================
echo Recomendado: reiniciar este PC al terminar.
echo.
pause
exit /b 0
