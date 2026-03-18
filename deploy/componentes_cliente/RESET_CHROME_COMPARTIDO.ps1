param(
    [switch]$IncludeEdge,
    [switch]$DisableChromeSignin,
    [string[]]$ExcludeUsers = @("Administrador", "Administrator", "Default", "Default User", "Public", "All Users")
)

$ErrorActionPreference = "Continue"
$logFile = "C:\Windows\Temp\reset_chrome_compartido.log"

function Write-Log {
    param([string]$Message)
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message
    Add-Content -Path $logFile -Value $line
}

function Stop-BrowserProcesses {
    param([string[]]$Names)
    foreach ($name in $Names) {
        try {
            Get-Process -Name $name -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
            Write-Log ("Proceso detenido: {0}" -f $name)
        } catch {
            Write-Log ("No se pudo detener {0}: {1}" -f $name, $_.Exception.Message)
        }
    }
}

function Remove-PathSafe {
    param([string]$Path)
    try {
        if (Test-Path $Path) {
            Remove-Item -Path $Path -Recurse -Force -ErrorAction SilentlyContinue
            Write-Log ("Eliminado: {0}" -f $Path)
            return $true
        }
    } catch {
        Write-Log ("Error eliminando {0}: {1}" -f $Path, $_.Exception.Message)
    }
    return $false
}

function Set-ChromeSharedPolicies {
    $policyPath = "HKLM:\SOFTWARE\Policies\Google\Chrome"
    try {
        if (-not (Test-Path $policyPath)) {
            New-Item -Path $policyPath -Force | Out-Null
        }
        New-ItemProperty -Path $policyPath -Name "BrowserSignin" -Value 0 -PropertyType DWord -Force | Out-Null
        New-ItemProperty -Path $policyPath -Name "SyncDisabled" -Value 1 -PropertyType DWord -Force | Out-Null
        New-ItemProperty -Path $policyPath -Name "PasswordManagerEnabled" -Value 0 -PropertyType DWord -Force | Out-Null
        Write-Log "Politicas Chrome compartido aplicadas"
    } catch {
        Write-Log ("No se pudieron aplicar politicas Chrome: {0}" -f $_.Exception.Message)
    }
}

Write-Log "=== RESET_CHROME_COMPARTIDO START ==="
Write-Log ("Host={0} IncludeEdge={1} DisableChromeSignin={2}" -f $env:COMPUTERNAME, $IncludeEdge, $DisableChromeSignin)

$browserProcesses = @("chrome")
if ($IncludeEdge) {
    $browserProcesses += "msedge"
}
Stop-BrowserProcesses -Names $browserProcesses
Start-Sleep -Seconds 2

$targets = @(
    @{ Name = "Chrome"; RelativePath = "AppData\Local\Google\Chrome\User Data" }
)

if ($IncludeEdge) {
    $targets += @{ Name = "Edge"; RelativePath = "AppData\Local\Microsoft\Edge\User Data" }
}

$profiles = Get-ChildItem -Path "C:\Users" -Directory -ErrorAction SilentlyContinue |
    Where-Object { $ExcludeUsers -notcontains $_.Name }

$summary = New-Object System.Collections.Generic.List[string]

foreach ($profile in $profiles) {
    foreach ($target in $targets) {
        $fullPath = Join-Path $profile.FullName $target.RelativePath
        $removed = Remove-PathSafe -Path $fullPath
        if ($removed) {
            $summary.Add(("{0}: {1}" -f $profile.Name, $target.Name))
        }
    }
}

if ($DisableChromeSignin) {
    Set-ChromeSharedPolicies
}

$report = @(
    "RESET CHROME COMPARTIDO OK",
    ("Host: {0}" -f $env:COMPUTERNAME),
    ("Date: {0}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss")),
    ("IncludeEdge: {0}" -f $IncludeEdge),
    ("DisableChromeSignin: {0}" -f $DisableChromeSignin),
    "Perfiles limpiados:",
    ($summary | Sort-Object)
)

$report | Set-Content -Path "C:\Windows\Temp\reset_chrome_compartido_done.txt" -Encoding UTF8
Write-Log "=== RESET_CHROME_COMPARTIDO END ==="
