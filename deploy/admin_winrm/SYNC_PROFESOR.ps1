param(
    [Parameter(Mandatory=$true)]
    [string]$ComputerName,

    [string]$UserName = "Colegio",
    [SecureString]$Password,
    [string]$LocalRepoPath,
    [string]$RemoteRepoPath = "C:\CastelAdmin\VeyonScripts",
    [string]$LocalMasterConfig = (Join-Path $env:APPDATA "Veyon\Config\VeyonMaster.json"),
    [string]$LocalVeyonCli = "C:\Program Files\Veyon\veyon-cli.exe"
)

$ErrorActionPreference = "Stop"

if (-not $LocalRepoPath) {
    $LocalRepoPath = Resolve-Path (Join-Path $PSScriptRoot "..\..")
}

if (-not $Password) {
    $Password = Read-Host "Clave local para $ComputerName\$UserName" -AsSecureString
}

# Validaciones locales
if (-not (Test-Path $LocalRepoPath)) { throw "No existe repo local: $LocalRepoPath" }
if (-not (Test-Path $LocalMasterConfig)) { Write-Warning "No existe config de Master local: $LocalMasterConfig" }
if (-not (Test-Path $LocalVeyonCli)) { throw "No existe veyon-cli.exe local: $LocalVeyonCli" }

# Directorio de reportes
$reportsDir = Join-Path (Split-Path $PSScriptRoot -Parent | Split-Path -Parent) ("reports\runs\" + (Get-Date -Format "yyyy-MM-dd") + "\admin_winrm")
if (-not (Test-Path $reportsDir)) { New-Item -ItemType Directory -Path $reportsDir -Force | Out-Null }
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$report = Join-Path $reportsDir ("sync_profesor_" + $timestamp + ".txt")

function Write-Report {
    param([string]$Message)
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message
    Add-Content -Path $report -Value $line -Encoding UTF8
    Write-Host $line
}

Write-Report "Inicio de sincronizacion hacia PC Profesor: $ComputerName"

# Verificar conexion
if (-not (Test-NetConnection -ComputerName $ComputerName -Port 5985 -InformationLevel Quiet -WarningAction SilentlyContinue)) {
    Write-Report "ERROR: Host $ComputerName no disponible por WinRM (5985)."
    exit 1
}

$cred = New-Object System.Management.Automation.PSCredential("$ComputerName\$UserName", $Password)
$session = $null
$zipPath = Join-Path $env:TEMP "VeyonScripts_sync_prof.zip"
$veyonConfigExportPath = Join-Path $env:TEMP "VeyonGlobal_sync_prof.json"

try {
    # Limpieza previa
    if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
    if (Test-Path $veyonConfigExportPath) { Remove-Item $veyonConfigExportPath -Force }

    Write-Report "Preparando archivos..."

    # Comprimir repositorio (excluyendo carpetas pesadas o temporales si es necesario)
    $excludeList = @(".git", "__pycache__", "logs", "backups", "reports")
    $filesToZip = Get-ChildItem -Path $LocalRepoPath | Where-Object { $_.Name -notin $excludeList }
    Compress-Archive -Path $filesToZip.FullName -DestinationPath $zipPath -Force

    # Exportar configuracion global de Veyon
    & $LocalVeyonCli config export $veyonConfigExportPath
    if (-not (Test-Path $veyonConfigExportPath)) {
        throw "No se pudo exportar la configuracion global de Veyon"
    }

    Write-Report "Paquetes listos. Iniciando sesion WinRM..."
    $session = New-PSSession -ComputerName $ComputerName -Credential $cred -ErrorAction Stop

    # Crear estructura remota
    Invoke-Command -Session $session -ScriptBlock {
        param($RemoteRepoPath)
        $dirs = @(
            "C:\CastelAdmin",
            "C:\CastelAdmin\staging",
            $RemoteRepoPath,
            "C:\Users\Alumno\AppData\Roaming\Veyon\Config",
            "C:\Users\Colegio\AppData\Roaming\Veyon\Config",
            "C:\ProgramData\Veyon\keys"
        )
        foreach ($dir in $dirs) {
            if (-not (Test-Path $dir)) {
                New-Item -ItemType Directory -Path $dir -Force | Out-Null
            }
        }
    } -ArgumentList $RemoteRepoPath

    Write-Report "Copiando archivos al PC remoto..."
    Copy-Item -Path $zipPath -Destination "C:\CastelAdmin\staging\VeyonScripts_sync.zip" -ToSession $session -Force
    Copy-Item -Path $veyonConfigExportPath -Destination "C:\CastelAdmin\staging\VeyonGlobal_sync.json" -ToSession $session -Force

    if (Test-Path $LocalMasterConfig) {
        Copy-Item -Path $LocalMasterConfig -Destination "C:\Users\Alumno\AppData\Roaming\Veyon\Config\VeyonMaster.json" -ToSession $session -Force
        Copy-Item -Path $LocalMasterConfig -Destination "C:\Users\Colegio\AppData\Roaming\Veyon\Config\VeyonMaster.json" -ToSession $session -Force
    }

    Write-Report "Aplicando configuracion en el PC remoto..."
    $result = Invoke-Command -Session $session -ScriptBlock {
        param($RemoteRepoPath)

        $zip = "C:\CastelAdmin\staging\VeyonScripts_sync.zip"
        $veyonCfg = "C:\CastelAdmin\staging\VeyonGlobal_sync.json"

        # Descomprimir repo
        if (Test-Path $RemoteRepoPath) {
            Get-ChildItem -Path $RemoteRepoPath -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        }
        Expand-Archive -Path $zip -DestinationPath $RemoteRepoPath -Force

        # Importar configuracion global
        $importOutput = & "C:\Program Files\Veyon\veyon-cli.exe" config import $veyonCfg 2>&1
        $importExit = $LASTEXITCODE

        return [pscustomobject]@{
            ImportExit = $importExit
            RepoStatus = (Test-Path (Join-Path $RemoteRepoPath "README.md"))
        }
    } -ArgumentList $RemoteRepoPath

    Write-Report "Resultado remoto: ExitCode=$($result.ImportExit), RepoStatus=$($result.RepoStatus)"
    Write-Report "Sincronizacion completada con exito."
}
catch {
    Write-Report "ERROR durante la sincronizacion: $($_.Exception.Message)"
    exit 1
}
finally {
    if ($session) { Remove-PSSession $session }
    if (Test-Path $zipPath) { Remove-Item $zipPath -Force -ErrorAction SilentlyContinue }
    if (Test-Path $veyonConfigExportPath) { Remove-Item $veyonConfigExportPath -Force -ErrorAction SilentlyContinue }
}
