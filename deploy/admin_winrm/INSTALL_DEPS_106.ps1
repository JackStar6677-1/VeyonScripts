param(
    [string]$ComputerName = "192.168.0.106",
    [string]$UserName = "Colegio",
    [string]$PasswordPlain = "administrativa",
    [string]$PythonInstallerPath = ""
)

$ErrorActionPreference = "Stop"

function Get-DefaultInstallerPath {
    $candidate = Join-Path $env:TEMP "python-3.12.9-amd64.exe"
    if (Test-Path $candidate) {
        return $candidate
    }
    throw "No existe el instalador local de Python. Descargalo primero a: $candidate"
}

if ([string]::IsNullOrWhiteSpace($PythonInstallerPath)) {
    $PythonInstallerPath = Get-DefaultInstallerPath
}

if (-not (Test-Path $PythonInstallerPath)) {
    throw "No existe PythonInstallerPath: $PythonInstallerPath"
}

$pass = ConvertTo-SecureString $PasswordPlain -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential("$ComputerName\$UserName", $pass)
$session = $null

try {
    $session = New-PSSession -ComputerName $ComputerName -Credential $cred

    Invoke-Command -Session $session -ScriptBlock {
        foreach ($dir in @("C:\CastelAdmin", "C:\CastelAdmin\staging")) {
            if (-not (Test-Path $dir)) {
                New-Item -ItemType Directory -Path $dir -Force | Out-Null
            }
        }
    }

    $remoteInstaller = "C:\CastelAdmin\staging\python-3.12.9-amd64.exe"
    Copy-Item -Path $PythonInstallerPath -Destination $remoteInstaller -ToSession $session -Force

    Invoke-Command -Session $session -ScriptBlock {
        param($RemoteInstaller)

        Start-Process -FilePath $RemoteInstaller -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 Include_test=0" -Wait

        $pyPath = Join-Path $env:LocalAppData "Programs\Python\Python312\python.exe"
        if (-not (Test-Path $pyPath)) {
            throw "Python no quedo instalado en la ruta esperada: $pyPath"
        }

        & $pyPath -m ensurepip --upgrade
        & $pyPath -m pip install --user "psutil>=5.9.0,<7"

        [pscustomobject]@{
            PythonVersion = (& $pyPath --version 2>&1 | Out-String).Trim()
            PsutilVersion = (& $pyPath -c "import psutil; print(psutil.__version__)" 2>&1 | Out-String).Trim()
            PythonPath    = $pyPath
            MasterScript  = Test-Path "C:\CastelAdmin\VeyonScripts\scripts\principales\VEYON_MAESTRO.py"
        }
    } -ArgumentList $remoteInstaller
}
finally {
    if ($session) {
        Remove-PSSession $session
    }
}
