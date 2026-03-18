param(
    [switch]$EnableAggressive
)

$ErrorActionPreference = "SilentlyContinue"
$log = "C:\Windows\Temp\jackoptimized.log"

function Log($msg) {
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $msg
    Add-Content -Path $log -Value $line
}

function Set-ServiceMode {
    param(
        [string]$Name,
        [string]$Mode
    )
    try {
        if ($Mode -eq "Disabled") {
            sc.exe stop $Name | Out-Null
            sc.exe config $Name start= disabled | Out-Null
        } elseif ($Mode -eq "Manual") {
            sc.exe config $Name start= demand | Out-Null
        } elseif ($Mode -eq "Automatic") {
            sc.exe config $Name start= auto | Out-Null
            sc.exe start $Name | Out-Null
        }
        Log "Service $Name => $Mode"
    } catch {
        Log "Service $Name failed: $($_.Exception.Message)"
    }
}

function Set-Reg {
    param(
        [string]$Path,
        [string]$Name,
        [int]$Value
    )
    try {
        if (-not (Test-Path $Path)) { New-Item -Path $Path -Force | Out-Null }
        New-ItemProperty -Path $Path -Name $Name -Value $Value -PropertyType DWord -Force | Out-Null
        Log "Reg $Path\\$Name=$Value"
    } catch {
        Log ("Reg failed {0}\\{1}: {2}" -f $Path, $Name, $_.Exception.Message)
    }
}

function Clear-TempSafe {
    param([string]$Path)
    try {
        if (Test-Path $Path) {
            Get-ChildItem -Path $Path -Recurse -Force -ErrorAction SilentlyContinue |
                Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
            Log "Cleaned $Path"
        }
    } catch {
        Log ("Clean failed {0}: {1}" -f $Path, $_.Exception.Message)
    }
}

Log "=== JACKOPTIMIZED START ==="
Log "Computer=$env:COMPUTERNAME User=$env:USERNAME Aggressive=$EnableAggressive"

# Servicios a deshabilitar (seguros para laboratorio general)
$disableServices = @(
    "DiagTrack",
    "dmwappushservice",
    "XblAuthManager",
    "XblGameSave",
    "XboxGipSvc",
    "XboxNetApiSvc",
    "MapsBroker",
    "Fax",
    "WbioSrvc",
    "HomeGroupListener",
    "HomeGroupProvider"
)

# En HDD conviene desactivar indexación + sysmain.
$disableServices += @("WSearch", "SysMain")

foreach ($s in $disableServices) { Set-ServiceMode -Name $s -Mode "Disabled" }

# Servicios a manual (evita carga continua, pero disponibles bajo demanda)
$manualServices = @(
    "wuauserv",
    "TabletInputService",
    "PcaSvc"
)
foreach ($s in $manualServices) { Set-ServiceMode -Name $s -Mode "Manual" }

# Mantener servicios remotos activos para administración masiva
Set-ServiceMode -Name "WinRM" -Mode "Automatic"
Set-ServiceMode -Name "RemoteRegistry" -Mode "Automatic"
Set-ServiceMode -Name "LanmanServer" -Mode "Automatic"

# Politicas visuales base (HKCU del usuario remoto actual)
Set-Reg -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "TaskbarAnimations" -Value 0
Set-Reg -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "ListviewAlphaSelect" -Value 0
Set-Reg -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" -Name "VisualFXSetting" -Value 2
Set-Reg -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Search" -Name "BingSearchEnabled" -Value 0
Set-Reg -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Search" -Name "SearchboxTaskbarMode" -Value 0

# Energia alto rendimiento
try {
    powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c | Out-Null
    powercfg /change disk-timeout-ac 0 | Out-Null
    powercfg /change disk-timeout-dc 0 | Out-Null
    Log "Power profile optimized"
} catch {
    Log "Power profile failed: $($_.Exception.Message)"
}

# Limpieza temporal
Clear-TempSafe -Path "$env:TEMP"
Clear-TempSafe -Path "C:\Windows\Temp"

# Opciones agresivas (opt-in)
if ($EnableAggressive) {
    try {
        powercfg /hibernate off | Out-Null
        Log "Aggressive: hibernation disabled"
    } catch {
        Log "Aggressive hibernate off failed: $($_.Exception.Message)"
    }
}

try {
    $summary = @(
        "JACKOPTIMIZED OK",
        "Host: $env:COMPUTERNAME",
        "User: $env:USERNAME",
        "Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
        "Aggressive: $EnableAggressive"
    )
    $summary | Set-Content -Path "C:\Windows\Temp\jackoptimized_done.txt" -Encoding UTF8
} catch {}

Log "=== JACKOPTIMIZED END ==="
