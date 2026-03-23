param(
    [string]$TaskName = "CastelSyncRepo106SSH",
    [string]$SyncScriptPath = "",
    [int]$IntervalMinutes = 15,
    [string]$IdentityFile = ""
)

$ErrorActionPreference = "Stop"

if (-not $SyncScriptPath) {
    $SyncScriptPath = Join-Path $PSScriptRoot "SYNC_REPO_TO_106_SSH.ps1"
}

if (-not (Test-Path $SyncScriptPath)) {
    throw "No existe script de sincronizacion: $SyncScriptPath"
}

$extraArgs = ""
if ($IdentityFile) {
    $extraArgs = (' -IdentityFile "{0}"' -f $IdentityFile)
}

$taskCommand = 'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{0}"{1}' -f $SyncScriptPath, $extraArgs

schtasks /Create /SC MINUTE /MO $IntervalMinutes /TN $TaskName /TR $taskCommand /F | Out-Null
schtasks /Run /TN $TaskName | Out-Null

Write-Host "TASK    : $TaskName"
Write-Host "SCRIPT  : $SyncScriptPath"
Write-Host "CADA    : $IntervalMinutes minutos"
if ($IdentityFile) {
    Write-Host "KEY     : $IdentityFile"
}
