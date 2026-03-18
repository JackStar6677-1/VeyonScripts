param(
    [string]$ReservasCsv = "..\..\data\reservas_dhcp_castel.csv",
    [string]$TaskName = "JackOptimized-WOL-0800",
    [string]$EndDateIso = "2026-12-31T23:59:59"
)

$ErrorActionPreference = "Stop"

function Ensure-Admin {
    $isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).
        IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        throw "Ejecuta este script como Administrador."
    }
}

Ensure-Admin

$root = Split-Path -Parent $PSScriptRoot
$repo = Resolve-Path (Join-Path $root "..")
$repo = $repo.Path
$csvPath = Resolve-Path (Join-Path $PSScriptRoot $ReservasCsv)
$csvPath = $csvPath.Path
$wolScript = Join-Path $PSScriptRoot "ENVIAR_WOL_CASTEL.ps1"

# Script de envio WOL (se ejecuta diario a las 08:00 en el admin)
$wolContent = @'
param(
  [string]$ReservasCsvPath
)
$ErrorActionPreference = "SilentlyContinue"

function Send-Wol {
  param([string]$Mac,[string]$Broadcast='192.168.0.255',[int]$Port=9)
  $macBytes = ($Mac -replace '[:-]','' -split '(.{2})' | ? { $_ }) | % { [byte]("0x$_") }
  if($macBytes.Count -ne 6){ return $false }
  $packet = [byte[]](,0xFF * 6 + ($macBytes * 16))
  $udp = New-Object System.Net.Sockets.UdpClient
  $udp.Connect($Broadcast,$Port)
  [void]$udp.Send($packet,$packet.Length)
  $udp.Close()
  return $true
}

$rows = Import-Csv $ReservasCsvPath
$ok=0
foreach($r in $rows){
  if(Send-Wol -Mac $r.MAC){ $ok++ }
}
"WOL enviado: $ok equipos - $(Get-Date -Format s)" | Set-Content C:\Windows\Temp\jackoptimized_wol.log -Encoding UTF8
'@
Set-Content -Path $wolScript -Value $wolContent -Encoding UTF8

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$wolScript`" -ReservasCsvPath `"$csvPath`""
$trigger = New-ScheduledTaskTrigger -Daily -At "08:00"
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
$task = Get-ScheduledTask -TaskName $TaskName
if ($task.Triggers.Count -gt 0) {
    $task.Triggers[0].EndBoundary = $EndDateIso
    Set-ScheduledTask -InputObject $task | Out-Null
}

Write-Host "[OK] Tarea WOL creada: $TaskName"
Write-Host "     Hora: 08:00 diaria"
Write-Host "     Fin:  $EndDateIso"
