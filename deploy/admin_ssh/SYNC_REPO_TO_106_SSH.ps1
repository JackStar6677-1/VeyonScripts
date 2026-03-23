param(
    [string]$SshTarget = "Colegio@192.168.0.106",
    [string]$LocalRepoPath = "",
    [string]$RemoteRepoPath = "C:\CastelAdmin\VeyonScripts",
    [string]$LocalMasterConfig = "",
    [string]$LocalVeyonCli = "C:\Program Files\Veyon\veyon-cli.exe",
    [string]$IdentityFile = "",
    [int]$ConnectTimeoutSeconds = 8
)

$ErrorActionPreference = "Stop"

if (-not $LocalRepoPath) {
    $LocalRepoPath = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
}

if (-not $LocalMasterConfig) {
    $LocalMasterConfig = Join-Path $env:APPDATA "Veyon\Config\VeyonMaster.json"
}

if (-not (Test-Path $LocalRepoPath)) { throw "No existe repo local: $LocalRepoPath" }
if (-not (Test-Path $LocalMasterConfig)) { throw "No existe config local: $LocalMasterConfig" }
if (-not (Test-Path $LocalVeyonCli)) { throw "No existe veyon-cli.exe local: $LocalVeyonCli" }

$sshExe = (Get-Command ssh.exe -ErrorAction Stop).Source
$scpExe = (Get-Command scp.exe -ErrorAction Stop).Source

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$report = Join-Path $PSScriptRoot ("sync_repo_106_ssh_" + $timestamp + ".txt")
$zipPath = Join-Path $env:TEMP "VeyonScripts_sync_106_ssh.zip"
$veyonConfigExportPath = Join-Path $env:TEMP "VeyonGlobal_sync_106_ssh.json"

function Write-Report {
    param([string]$Message)
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message
    Add-Content -Path $report -Value $line -Encoding UTF8
    Write-Host $line
}

function Invoke-Ssh {
    param([string]$Command)

    $args = @(
        "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=accept-new",
        "-o", ("ConnectTimeout={0}" -f $ConnectTimeoutSeconds)
    )

    if ($IdentityFile) {
        $args += @("-i", $IdentityFile)
    }

    $args += $SshTarget
    $args += $Command

    & $sshExe @args
    if ($LASTEXITCODE -ne 0) {
        throw "SSH fallo con codigo $LASTEXITCODE"
    }
}

function Invoke-Scp {
    param(
        [string]$SourcePath,
        [string]$DestinationPath
    )

    $args = @(
        "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=accept-new",
        "-o", ("ConnectTimeout={0}" -f $ConnectTimeoutSeconds)
    )

    if ($IdentityFile) {
        $args += @("-i", $IdentityFile)
    }

    $args += $SourcePath
    $args += ("{0}:{1}" -f $SshTarget, $DestinationPath)

    & $scpExe @args
    if ($LASTEXITCODE -ne 0) {
        throw "SCP fallo con codigo $LASTEXITCODE"
    }
}

try {
    Write-Report "Inicio de sincronizacion SSH hacia $SshTarget"

    if (Test-Path $zipPath) {
        Remove-Item $zipPath -Force
    }
    if (Test-Path $veyonConfigExportPath) {
        Remove-Item $veyonConfigExportPath -Force
    }

    Compress-Archive -Path @(
        (Join-Path $LocalRepoPath "README.md"),
        (Join-Path $LocalRepoPath "apps"),
        (Join-Path $LocalRepoPath "deploy"),
        (Join-Path $LocalRepoPath "launchers"),
        (Join-Path $LocalRepoPath "scripts"),
        (Join-Path $LocalRepoPath "tools"),
        (Join-Path $LocalRepoPath ".gitignore")
    ) -DestinationPath $zipPath -Force

    & $LocalVeyonCli config export $veyonConfigExportPath
    if (-not (Test-Path $veyonConfigExportPath)) {
        throw "No se pudo exportar la configuracion global de Veyon"
    }

    Write-Report "ZIP preparado: $zipPath"

    Invoke-Ssh "powershell -NoProfile -ExecutionPolicy Bypass -Command `"& {
        foreach (`$dir in @(
            'C:\CastelAdmin',
            'C:\CastelAdmin\staging',
            '$RemoteRepoPath',
            'C:\Users\Alumno\AppData\Roaming\Veyon\Config',
            'C:\Users\Colegio\AppData\Roaming\Veyon\Config'
        )) {
            if (-not (Test-Path `$dir)) {
                New-Item -ItemType Directory -Path `$dir -Force | Out-Null
            }
        }
    }`""

    Invoke-Scp -SourcePath $zipPath -DestinationPath "C:/CastelAdmin/staging/VeyonScripts_sync_106_ssh.zip"
    Invoke-Scp -SourcePath $veyonConfigExportPath -DestinationPath "C:/CastelAdmin/staging/VeyonGlobal_sync_106_ssh.json"
    Invoke-Scp -SourcePath $LocalMasterConfig -DestinationPath "C:/Users/Alumno/AppData/Roaming/Veyon/Config/VeyonMaster.json"
    Invoke-Scp -SourcePath $LocalMasterConfig -DestinationPath "C:/Users/Colegio/AppData/Roaming/Veyon/Config/VeyonMaster.json"

    $remoteScript = @"
`$zip = 'C:\CastelAdmin\staging\VeyonScripts_sync_106_ssh.zip'
`$veyonCfg = 'C:\CastelAdmin\staging\VeyonGlobal_sync_106_ssh.json'
`$remoteRepo = '$RemoteRepoPath'

if (Test-Path `$remoteRepo) {
    Get-ChildItem -Path `$remoteRepo -Force -ErrorAction SilentlyContinue |
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
} else {
    New-Item -ItemType Directory -Path `$remoteRepo -Force | Out-Null
}

Expand-Archive -Path `$zip -DestinationPath `$remoteRepo -Force
& 'C:\Program Files\Veyon\veyon-cli.exe' config import `$veyonCfg | Out-Null

[pscustomobject]@{
    RepoReadme = Test-Path (Join-Path `$remoteRepo 'README.md')
    AlumnoConfig = Test-Path 'C:\Users\Alumno\AppData\Roaming\Veyon\Config\VeyonMaster.json'
    ColegioConfig = Test-Path 'C:\Users\Colegio\AppData\Roaming\Veyon\Config\VeyonMaster.json'
} | ConvertTo-Json -Compress
"@

    $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($remoteScript))
    $result = & $sshExe @(
        "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=accept-new",
        "-o", ("ConnectTimeout={0}" -f $ConnectTimeoutSeconds)
    ) $(if ($IdentityFile) { @("-i", $IdentityFile) }) $SshTarget "powershell -NoProfile -ExecutionPolicy Bypass -EncodedCommand $encoded"

    if ($LASTEXITCODE -ne 0) {
        throw "Ejecucion remota por SSH fallo con codigo $LASTEXITCODE"
    }

    Write-Report ("Resultado remoto: {0}" -f ($result -join " "))
    Write-Report "Sincronizacion SSH OK"
}
catch {
    Write-Report ("ERROR: {0}" -f $_.Exception.Message)
    exit 1
}
finally {
    if (Test-Path $zipPath) {
        Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
    }
    if (Test-Path $veyonConfigExportPath) {
        Remove-Item $veyonConfigExportPath -Force -ErrorAction SilentlyContinue
    }
}
