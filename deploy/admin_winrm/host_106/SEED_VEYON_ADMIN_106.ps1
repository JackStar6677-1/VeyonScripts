param(
    [string]$ComputerName = "192.168.0.106",
    [string]$UserName = "Colegio",
    [string]$PasswordPlain = "administrativa",
    [string]$LocalRepoPath = "C:\Users\Profesor\Documents\GitHub\VeyonScripts",
    [string]$LocalMasterConfig = "C:\Users\Profesor\AppData\Roaming\Veyon\Config\VeyonMaster.json",
    [string]$LocalPrivateKey = "C:\ProgramData\Veyon\keys\private\Sala-de-computacion\key",
    [string]$LocalPublicKey = "C:\ProgramData\Veyon\keys\public\Sala-de-computacion\key",
    [string]$LocalMasterExe = "C:\Program Files\Veyon\veyon-master.exe",
    [string]$LocalVeyonCli = "C:\Program Files\Veyon\veyon-cli.exe"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $LocalRepoPath)) { throw "No existe repo local: $LocalRepoPath" }
if (-not (Test-Path $LocalMasterConfig)) { throw "No existe config local: $LocalMasterConfig" }
if (-not (Test-Path $LocalPrivateKey)) { throw "No existe clave privada local: $LocalPrivateKey" }
if (-not (Test-Path $LocalPublicKey)) { throw "No existe clave publica local: $LocalPublicKey" }
if (-not (Test-Path $LocalMasterExe)) { throw "No existe veyon-master.exe local: $LocalMasterExe" }
if (-not (Test-Path $LocalVeyonCli)) { throw "No existe veyon-cli.exe local: $LocalVeyonCli" }

$pass = ConvertTo-SecureString $PasswordPlain -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential("$ComputerName\$UserName", $pass)
$session = $null
$exportConfigPath = Join-Path $env:TEMP "veyon_seed_config_106.json"

try {
    if (Test-Path $exportConfigPath) {
        Remove-Item $exportConfigPath -Force
    }

    & $LocalVeyonCli config export $exportConfigPath
    if (-not (Test-Path $exportConfigPath)) {
        throw "No se pudo exportar la configuracion global de Veyon"
    }

    $session = New-PSSession -ComputerName $ComputerName -Credential $cred

    Invoke-Command -Session $session -ScriptBlock {
        $dirs = @(
            "C:\CastelAdmin",
            "C:\CastelAdmin\VeyonScripts",
            "C:\Users\Alumno\AppData\Roaming\Veyon\Config",
            "C:\Users\Colegio\AppData\Roaming\Veyon\Config",
            "C:\ProgramData\Veyon\keys\private\Sala-de-computacion",
            "C:\ProgramData\Veyon\keys\public\Sala-de-computacion",
            "C:\Users\Public\Desktop"
        )

        foreach ($dir in $dirs) {
            if (-not (Test-Path $dir)) {
                New-Item -ItemType Directory -Path $dir -Force | Out-Null
            }
        }
    }

    Copy-Item -Path $LocalMasterExe -Destination "C:\Program Files\Veyon\veyon-master.exe" -ToSession $session -Force
    Copy-Item -Path $LocalPrivateKey -Destination "C:\ProgramData\Veyon\keys\private\Sala-de-computacion\key" -ToSession $session -Force
    Copy-Item -Path $LocalPublicKey -Destination "C:\ProgramData\Veyon\keys\public\Sala-de-computacion\key" -ToSession $session -Force
    Copy-Item -Path $exportConfigPath -Destination "C:\Temp\veyon_seed_config_106.json" -ToSession $session -Force
    Copy-Item -Path $LocalMasterConfig -Destination "C:\Users\Alumno\AppData\Roaming\Veyon\Config\VeyonMaster.json" -ToSession $session -Force
    Copy-Item -Path $LocalMasterConfig -Destination "C:\Users\Colegio\AppData\Roaming\Veyon\Config\VeyonMaster.json" -ToSession $session -Force

    foreach ($item in @("README.md", "apps", "data", "deploy", "launchers", "scripts", "tools", ".gitignore")) {
        $source = Join-Path $LocalRepoPath $item
        if (Test-Path $source) {
            Copy-Item -Path $source -Destination "C:\CastelAdmin\VeyonScripts" -ToSession $session -Recurse -Force
        }
    }

    Invoke-Command -Session $session -ScriptBlock {
        & "C:\Program Files\Veyon\veyon-cli.exe" config import "C:\Temp\veyon_seed_config_106.json" | Out-Null

        Set-Content -Path "C:\Users\Public\Desktop\ABRIR_VEYON_MAESTRO.bat" -Encoding ASCII -Force -Value @(
            "@echo off",
            "start """" ""C:\Program Files\Veyon\veyon-master.exe"""
        )

        Set-Content -Path "C:\Users\Public\Desktop\ABRIR_REPO_VEYON.bat" -Encoding ASCII -Force -Value @(
            "@echo off",
            "start """" ""C:\CastelAdmin\VeyonScripts"""
        )

        Set-Content -Path "C:\CastelAdmin\LEEME_VEYON_ADMIN.txt" -Encoding UTF8 -Force -Value @(
            "PC maestro secundario para la sala de computacion.",
            "",
            "Abrir Veyon maestro: C:\Users\Public\Desktop\ABRIR_VEYON_MAESTRO.bat",
            "Abrir repo: C:\Users\Public\Desktop\ABRIR_REPO_VEYON.bat",
            "Repo local: C:\CastelAdmin\VeyonScripts"
        )

        [pscustomobject]@{
            MasterExe = Test-Path "C:\Program Files\Veyon\veyon-master.exe"
            PrivateKey = Test-Path "C:\ProgramData\Veyon\keys\private\Sala-de-computacion\key"
            PublicKey = Test-Path "C:\ProgramData\Veyon\keys\public\Sala-de-computacion\key"
            AlumnoConfig = Test-Path "C:\Users\Alumno\AppData\Roaming\Veyon\Config\VeyonMaster.json"
            ColegioConfig = Test-Path "C:\Users\Colegio\AppData\Roaming\Veyon\Config\VeyonMaster.json"
            RepoReadme = Test-Path "C:\CastelAdmin\VeyonScripts\README.md"
            LaunchBat = Test-Path "C:\Users\Public\Desktop\ABRIR_VEYON_MAESTRO.bat"
            RepoBat = Test-Path "C:\Users\Public\Desktop\ABRIR_REPO_VEYON.bat"
        }
    }
}
finally {
    if ($session) {
        Remove-PSSession $session
    }
    if (Test-Path $exportConfigPath) {
        Remove-Item $exportConfigPath -Force -ErrorAction SilentlyContinue
    }
}
