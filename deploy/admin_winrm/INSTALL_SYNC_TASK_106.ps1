param(
    [string]$TaskName = "CastelSyncRepo106",
    [string]$SyncScriptPath = "C:\Users\Profesor\Documents\GitHub\VeyonScripts\deploy\admin_winrm\SYNC_REPO_TO_106.ps1",
    [int]$IntervalMinutes = 15
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $SyncScriptPath)) {
    throw "No existe script de sincronizacion: $SyncScriptPath"
}

$taskCommand = 'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{0}"' -f $SyncScriptPath

schtasks /Create /SC MINUTE /MO $IntervalMinutes /TN $TaskName /TR $taskCommand /F | Out-Null
schtasks /Run /TN $TaskName | Out-Null

Write-Host "TASK    : $TaskName"
Write-Host "SCRIPT  : $SyncScriptPath"
Write-Host "CADA    : $IntervalMinutes minutos"
