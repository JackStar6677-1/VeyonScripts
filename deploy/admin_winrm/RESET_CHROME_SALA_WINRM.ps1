param(
    [string]$HostsFile = ".\hosts_castel.txt",
    [string[]]$UserCandidates = @("Colegio", "colegio", "Admin", "Administrador", "Usuario", "Alumno", "Estudiante", "Profesor"),
    [string]$PasswordPlain = "administrativa",
    [switch]$IncludeEdge,
    [switch]$DisableChromeSignin,
    [switch]$SkipBridgeInstall,
    [switch]$WhatIfMode
)

$ErrorActionPreference = "Stop"
$kitRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

function Resolve-KitPath {
    param([string]$Name)
    Join-Path $kitRoot $Name
}

function Resolve-InputPath {
    param([string]$InputPath)

    if ([string]::IsNullOrWhiteSpace($InputPath)) {
        return $InputPath
    }

    if ([System.IO.Path]::IsPathRooted($InputPath)) {
        return $InputPath
    }

    Join-Path $kitRoot $InputPath
}

function Require-File {
    param([string]$FilePath)

    if (-not (Test-Path $FilePath)) {
        throw "No existe archivo requerido: $FilePath"
    }
}

function Invoke-KitScript {
    param(
        [string]$ScriptPath,
        [string[]]$ScriptArguments = @()
    )

    Require-File -FilePath $ScriptPath

    if ($WhatIfMode) {
        Write-Host "[WHATIF] powershell -File `"$ScriptPath`" $($ScriptArguments -join ' ')" -ForegroundColor Yellow
        return
    }

    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ScriptPath @ScriptArguments
    if ($LASTEXITCODE -ne 0) {
        throw "Fallo ejecutando $ScriptPath"
    }
}

$resolvedHostsFile = Resolve-InputPath -InputPath $HostsFile
Require-File -FilePath $resolvedHostsFile

if (-not $SkipBridgeInstall) {
    Write-Host "Paso 1/2: instalando/actualizando bridge admin en la sala..." -ForegroundColor Cyan
    Invoke-KitScript -ScriptPath (Resolve-KitPath "INSTALAR_ELEVACION_WINRM.ps1") -ScriptArguments @(
        "-HostsFile", $resolvedHostsFile,
        "-PasswordPlain", $PasswordPlain
    )
} else {
    Write-Host "Paso 1/2: omitido bridge admin por -SkipBridgeInstall" -ForegroundColor DarkYellow
}

$queueArgs = @(
    "-Action", "powershell_file",
    "-HostsFile", $resolvedHostsFile,
    "-PasswordPlain", $PasswordPlain,
    "-Path", "C:\ProgramData\CastelRemote\RESET_CHROME_COMPARTIDO.ps1"
)

if ($DisableChromeSignin -and $IncludeEdge) {
    $queueArgs += @("-Arguments", '"-DisableChromeSignin -IncludeEdge"')
} elseif ($DisableChromeSignin) {
    $queueArgs += @("-Arguments", '"-DisableChromeSignin"')
} elseif ($IncludeEdge) {
    $queueArgs += @("-Arguments", '"-IncludeEdge"')
}

Write-Host "Paso 2/2: encolando reset de Chrome en toda la sala..." -ForegroundColor Cyan
Invoke-KitScript -ScriptPath (Resolve-KitPath "ENVIAR_ADMIN_COMANDO_WINRM.ps1") -ScriptArguments $queueArgs

Write-Host ""
Write-Host "Reset Chrome lanzado." -ForegroundColor Green
Write-Host "Flags activos:" -ForegroundColor Green
Write-Host ("- IncludeEdge: {0}" -f [bool]$IncludeEdge)
Write-Host ("- DisableChromeSignin: {0}" -f [bool]$DisableChromeSignin)
Write-Host ("- SkipBridgeInstall: {0}" -f [bool]$SkipBridgeInstall)
