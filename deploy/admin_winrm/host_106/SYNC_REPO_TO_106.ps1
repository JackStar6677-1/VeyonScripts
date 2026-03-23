param(
    [string]$ComputerName = "192.168.0.106",
    [string]$UserName = "Colegio",
    [string]$PasswordPlain = "administrativa",
    [string]$LocalRepoPath = "C:\Users\Profesor\Documents\GitHub\VeyonScripts",
    [string]$RemoteRepoPath = "C:\CastelAdmin\VeyonScripts",
    [string]$LocalMasterConfig = "C:\Users\Profesor\AppData\Roaming\Veyon\Config\VeyonMaster.json",
    [string]$LocalVeyonCli = "C:\Program Files\Veyon\veyon-cli.exe"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $LocalRepoPath)) { throw "No existe repo local: $LocalRepoPath" }
if (-not (Test-Path $LocalMasterConfig)) { throw "No existe config local: $LocalMasterConfig" }
if (-not (Test-Path $LocalVeyonCli)) { throw "No existe veyon-cli.exe local: $LocalVeyonCli" }

$reportsDir = Join-Path (Split-Path $PSScriptRoot -Parent | Split-Path -Parent | Split-Path -Parent) ("reports\runs\" + (Get-Date -Format "yyyy-MM-dd") + "\admin_winrm")
if (-not (Test-Path $reportsDir)) { New-Item -ItemType Directory -Path $reportsDir -Force | Out-Null }
$reportsDir = (Resolve-Path $reportsDir).Path
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$report = Join-Path $reportsDir ("sync_repo_106_" + $timestamp + ".txt")

function Write-Report {
    param([string]$Message)
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message
    Add-Content -Path $report -Value $line -Encoding UTF8
    Write-Host $line
}

Write-Report "Inicio de sincronizacion hacia $ComputerName"

if (-not (Test-NetConnection -ComputerName $ComputerName -Port 5985 -InformationLevel Quiet -WarningAction SilentlyContinue)) {
    Write-Report "Host no disponible por WinRM. Se omite esta pasada."
    exit 0
}

$pass = ConvertTo-SecureString $PasswordPlain -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential("$ComputerName\$UserName", $pass)
$session = $null
$zipPath = Join-Path $env:TEMP "VeyonScripts_sync_106.zip"
$veyonConfigExportPath = Join-Path $env:TEMP "VeyonGlobal_sync_106.json"

try {
    if (Test-Path $zipPath) {
        Remove-Item $zipPath -Force
    }
    if (Test-Path $veyonConfigExportPath) {
        Remove-Item $veyonConfigExportPath -Force
    }

    Compress-Archive -Path @(
        (Join-Path $LocalRepoPath "README.md"),
        (Join-Path $LocalRepoPath "requirements.txt"),
        (Join-Path $LocalRepoPath "apps"),
        (Join-Path $LocalRepoPath "data"),
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

    $session = New-PSSession -ComputerName $ComputerName -Credential $cred

    Invoke-Command -Session $session -ScriptBlock {
        param($RemoteRepoPath)

        foreach ($dir in @(
            "C:\CastelAdmin",
            "C:\CastelAdmin\staging",
            $RemoteRepoPath,
            "C:\Users\Alumno\AppData\Roaming\Veyon\Config",
            "C:\Users\Colegio\AppData\Roaming\Veyon\Config"
        )) {
            if (-not (Test-Path $dir)) {
                New-Item -ItemType Directory -Path $dir -Force | Out-Null
            }
        }
    } -ArgumentList $RemoteRepoPath

    Copy-Item -Path $zipPath -Destination "C:\CastelAdmin\staging\VeyonScripts_sync_106.zip" -ToSession $session -Force
    Copy-Item -Path $veyonConfigExportPath -Destination "C:\CastelAdmin\staging\VeyonGlobal_sync_106.json" -ToSession $session -Force
    Copy-Item -Path $LocalMasterConfig -Destination "C:\Users\Alumno\AppData\Roaming\Veyon\Config\VeyonMaster.json" -ToSession $session -Force
    Copy-Item -Path $LocalMasterConfig -Destination "C:\Users\Colegio\AppData\Roaming\Veyon\Config\VeyonMaster.json" -ToSession $session -Force

    $result = Invoke-Command -Session $session -ScriptBlock {
        param($RemoteRepoPath)

        $zip = "C:\CastelAdmin\staging\VeyonScripts_sync_106.zip"
        $veyonCfg = "C:\CastelAdmin\staging\VeyonGlobal_sync_106.json"

        if (Test-Path $RemoteRepoPath) {
            Get-ChildItem -Path $RemoteRepoPath -Force -ErrorAction SilentlyContinue |
                Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        }

        Expand-Archive -Path $zip -DestinationPath $RemoteRepoPath -Force

        # Algunas builds viejas de Veyon/Qt escriben warnings DPI a stderr
        # aunque el import termine bien. Los capturamos para no romper el sync.
        $importOutput = & "C:\Program Files\Veyon\veyon-cli.exe" config import $veyonCfg 2>&1
        $importExit = $LASTEXITCODE
        $importText = ($importOutput | ForEach-Object { "$_" }) -join "`n"
        $benignQtWarning = $importText -match "qt\.qpa\.window: SetProcessDpiAwarenessContext\(\) failed"

        if ($importExit -ne 0 -and -not $benignQtWarning) {
            throw "Import Veyon fallo (exit=$importExit): $importText"
        }

        $readmePath = Join-Path $RemoteRepoPath "README.md"

        [pscustomobject]@{
            RepoReadme = Test-Path $readmePath
            AlumnoConfig = Test-Path "C:\Users\Alumno\AppData\Roaming\Veyon\Config\VeyonMaster.json"
            ColegioConfig = Test-Path "C:\Users\Colegio\AppData\Roaming\Veyon\Config\VeyonMaster.json"
            ImportExit = $importExit
            ImportQtWarning = $benignQtWarning
        }
    } -ArgumentList $RemoteRepoPath

    Write-Report ("RepoReadme={0}; AlumnoConfig={1}; ColegioConfig={2}; ImportExit={3}; ImportQtWarning={4}" -f $result.RepoReadme, $result.AlumnoConfig, $result.ColegioConfig, $result.ImportExit, $result.ImportQtWarning)
    Write-Report "Sincronizacion OK"
}
catch {
    Write-Report ("ERROR: {0}" -f $_.Exception.Message)
    exit 1
}
finally {
    if ($session) {
        Remove-PSSession $session
    }
    if (Test-Path $zipPath) {
        Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
    }
    if (Test-Path $veyonConfigExportPath) {
        Remove-Item $veyonConfigExportPath -Force -ErrorAction SilentlyContinue
    }
}
