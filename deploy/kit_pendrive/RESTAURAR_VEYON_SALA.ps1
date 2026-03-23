[CmdletBinding()]
param(
    [string]$PublicKeyPath = "D:\90-SENSIBLE\Credenciales veyon Castel\Sala-de-computacion_public_key.pem",
    [string]$PrivateKeyPath = "D:\90-SENSIBLE\Credenciales veyon Castel\Sala-de-computacion_private_key.pem",
    [string]$MasterConfigPath = "D:\10-RESPALDOS\Respaldo-Migracion-PC-2026-03-18\backup-safe\config\veyon\VeyonMaster.json",
    [string]$KeyName = "Sala-de-computacion"
)

$ErrorActionPreference = "Stop"

function Assert-Admin {
    $currentIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentIdentity)
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw "Este script debe ejecutarse como Administrador."
    }
}

function Assert-FileExists {
    param([string]$PathToCheck)
    if (-not (Test-Path -LiteralPath $PathToCheck -PathType Leaf)) {
        throw "No existe el archivo requerido: $PathToCheck"
    }
}

Assert-Admin

$veyonCli = "C:\Program Files\Veyon\veyon-cli.exe"
if (-not (Test-Path -LiteralPath $veyonCli -PathType Leaf)) {
    throw "No se encontro veyon-cli.exe en $veyonCli"
}

Assert-FileExists -PathToCheck $PublicKeyPath
Assert-FileExists -PathToCheck $PrivateKeyPath

Write-Host "== Restaurando claves de Veyon ==" -ForegroundColor Cyan
& $veyonCli authkeys import "$KeyName/private" $PrivateKeyPath
& $veyonCli authkeys import "$KeyName/public" $PublicKeyPath

$configDir = Join-Path $env:APPDATA "Veyon\Config"
if (-not (Test-Path -LiteralPath $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
}

if (Test-Path -LiteralPath $MasterConfigPath -PathType Leaf) {
    Copy-Item -LiteralPath $MasterConfigPath -Destination (Join-Path $configDir "VeyonMaster.json") -Force
    Write-Host "Config de maestro restaurada en $configDir" -ForegroundColor Green
}
else {
    Write-Warning "No se encontro VeyonMaster.json en $MasterConfigPath. Las claves si fueron importadas."
}

Write-Host ""
Write-Host "Claves disponibles:" -ForegroundColor Cyan
& $veyonCli authkeys list

Write-Host ""
Write-Host "Listo." -ForegroundColor Green
