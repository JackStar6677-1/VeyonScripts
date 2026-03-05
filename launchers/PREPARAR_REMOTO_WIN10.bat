@echo off
setlocal EnableExtensions
title Preparar Gestion Remota - Windows 10

set "LOG_FILE=%TEMP%\PREPARAR_REMOTO_WIN10.log"
set "CREATE_SUPPORT_USER=0"
set "SUPPORT_USER=SoporteTI"
set "SUPPORT_PASS=214526867"

if /I not "%~1"=="--elevated" (
    net session >nul 2>&1
    if not %errorlevel%==0 (
        echo [INFO] Solicitando permisos de administrador...
        powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -Verb RunAs -FilePath '%~f0' -ArgumentList '--elevated'"
        if errorlevel 1 (
            echo [ERROR] UAC cancelado o fallo al elevar.
            echo [ERROR] UAC cancelado o fallo al elevar.>> "%LOG_FILE%"
            pause
        )
        exit /b
    )
)

echo ========================================================== > "%LOG_FILE%"
echo INICIO: %date% %time% >> "%LOG_FILE%"
echo EQUIPO: %COMPUTERNAME% >> "%LOG_FILE%"
echo ========================================================== >> "%LOG_FILE%"

echo.
echo ==========================================================
echo  PREPARANDO PC PARA GESTION REMOTA (WIN10)
echo ==========================================================
echo [LOG] %LOG_FILE%
echo.

echo [0/7] Ajustando perfil de red a Privado (si aplica)...
echo [CMD] Set-NetConnectionProfile Private>> "%LOG_FILE%"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-NetConnectionProfile | ForEach-Object { Set-NetConnectionProfile -InterfaceIndex $_.InterfaceIndex -NetworkCategory Private -ErrorAction SilentlyContinue }" >> "%LOG_FILE%" 2>&1

echo [1/7] Habilitando WinRM...
echo [CMD] Enable-PSRemoting -SkipNetworkProfileCheck -Force>> "%LOG_FILE%"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Enable-PSRemoting -SkipNetworkProfileCheck -Force" >> "%LOG_FILE%" 2>&1
echo [CMD] sc config WinRM start= auto>> "%LOG_FILE%"
sc config WinRM start= auto >> "%LOG_FILE%" 2>&1
echo [CMD] sc start WinRM>> "%LOG_FILE%"
sc start WinRM >> "%LOG_FILE%" 2>&1

echo [2/7] Abriendo reglas de firewall...
echo [CMD] netsh WMI>> "%LOG_FILE%"
netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=Yes >> "%LOG_FILE%" 2>&1
echo [CMD] netsh WinRM>> "%LOG_FILE%"
netsh advfirewall firewall set rule group="Windows Remote Management" new enable=Yes >> "%LOG_FILE%" 2>&1
echo [CMD] netsh File/Printer>> "%LOG_FILE%"
netsh advfirewall firewall set rule group="File and Printer Sharing" new enable=Yes >> "%LOG_FILE%" 2>&1
echo [CMD] netsh Remote Service Mgmt>> "%LOG_FILE%"
netsh advfirewall firewall set rule group="Remote Service Management" new enable=Yes >> "%LOG_FILE%" 2>&1

echo [3/7] Ajustando servicios...
echo [CMD] sc config/start RemoteRegistry>> "%LOG_FILE%"
sc config RemoteRegistry start= auto >> "%LOG_FILE%" 2>&1
sc start RemoteRegistry >> "%LOG_FILE%" 2>&1
echo [CMD] sc config/start LanmanServer>> "%LOG_FILE%"
sc config LanmanServer start= auto >> "%LOG_FILE%" 2>&1
sc start LanmanServer >> "%LOG_FILE%" 2>&1

echo [4/7] Aplicando politica UAC remota...
echo [CMD] reg add LocalAccountTokenFilterPolicy>> "%LOG_FILE%"
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v LocalAccountTokenFilterPolicy /t REG_DWORD /d 1 /f >> "%LOG_FILE%" 2>&1

echo [5/7] Usuario de soporte (opcional)...
if "%CREATE_SUPPORT_USER%"=="1" (
    echo [CMD] net user + admin group>> "%LOG_FILE%"
    net user "%SUPPORT_USER%" "%SUPPORT_PASS%" /add >> "%LOG_FILE%" 2>&1
    net localgroup Administradores "%SUPPORT_USER%" /add >> "%LOG_FILE%" 2>&1
    echo     Usuario "%SUPPORT_USER%" creado/agregado.
) else (
    echo     Omitido ^(CREATE_SUPPORT_USER=0^).
)

echo [6/7] Datos utiles del equipo...
for /f "tokens=2 delims==" %%A in ('wmic computersystem get name /value ^| find "="') do set "PC_NAME=%%A"
echo     Nombre PC: %PC_NAME%
echo Nombre PC: %PC_NAME%>> "%LOG_FILE%"
for /f "tokens=2 delims=:" %%A in ('ipconfig ^| findstr /R /C:"IPv4"') do (
    set "IP_RAW=%%A"
    goto :showip
)
:showip
set "IP_RAW=%IP_RAW: =%"
echo     IPv4 (primera): %IP_RAW%
echo IPv4 (primera): %IP_RAW%>> "%LOG_FILE%"

echo [7/7] Probando WinRM local...
call winrm id >> "%LOG_FILE%" 2>&1
set "WR_ERR=%errorlevel%"
if "%WR_ERR%"=="0" goto :wr_ok
echo     WinRM no respondio.
echo WinRM no respondio>> "%LOG_FILE%"
goto :wr_done
:wr_ok
echo     WinRM OK.
echo WinRM OK>> "%LOG_FILE%"
:wr_done

echo.
echo ==========================================================
echo  LISTO
echo ==========================================================
echo LOG: %LOG_FILE%
echo FIN: %date% %time%>> "%LOG_FILE%"
echo.
pause
exit /b 0
