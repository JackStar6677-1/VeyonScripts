param(
    [switch]$IncludeMachinePolicies,
    [switch]$AlsoDeleteEdge,
    [string[]]$ExcludeUsers = @("Administrador", "Administrator", "Default", "Default User", "Public", "All Users", "defaultuser0")
)

$ErrorActionPreference = "Continue"
$logDir = "C:\Windows\Temp"
$logFile = Join-Path $logDir "reset_chrome_total_portable.log"
$doneFile = Join-Path $logDir "reset_chrome_total_portable_done.txt"

if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

function Write-Log {
    param([string]$Message)
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message
    Add-Content -Path $logFile -Value $line
}

function Stop-ProcessesByName {
    param([string[]]$Names)
    foreach ($name in $Names | Select-Object -Unique) {
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
            Remove-Item -LiteralPath $Path -Recurse -Force -ErrorAction SilentlyContinue
            Write-Log ("Eliminado: {0}" -f $Path)
            return $true
        }
    } catch {
        Write-Log ("Error eliminando {0}: {1}" -f $Path, $_.Exception.Message)
    }

    return $false
}

function Remove-RegistryTreeSafe {
    param([string]$RegistryPath)

    try {
        if (Test-Path $RegistryPath) {
            Remove-Item -Path $RegistryPath -Recurse -Force -ErrorAction SilentlyContinue
            Write-Log ("Clave eliminada: {0}" -f $RegistryPath)
            return $true
        }
    } catch {
        Write-Log ("Error eliminando clave {0}: {1}" -f $RegistryPath, $_.Exception.Message)
    }

    return $false
}

function Remove-UserChromeData {
    param([System.IO.DirectoryInfo]$Profile)

    $targets = @(
        "AppData\Local\Google\Chrome",
        "AppData\Local\Google\CrashReports",
        "AppData\Roaming\Google\Chrome"
    )

    if ($AlsoDeleteEdge) {
        $targets += @(
            "AppData\Local\Microsoft\Edge",
            "AppData\Roaming\Microsoft\Edge"
        )
    }

    $removed = New-Object System.Collections.Generic.List[string]
    foreach ($relative in $targets) {
        $fullPath = Join-Path $Profile.FullName $relative
        if (Remove-PathSafe -Path $fullPath) {
            $removed.Add($relative)
        }
    }

    return $removed
}

Write-Log "=== RESET_CHROME_TOTAL_PORTABLE START ==="
Write-Log ("Host={0} IncludeMachinePolicies={1} AlsoDeleteEdge={2}" -f $env:COMPUTERNAME, $IncludeMachinePolicies, $AlsoDeleteEdge)

$processNames = @("chrome", "googlecrashhandler", "googlecrashhandler64")
if ($AlsoDeleteEdge) {
    $processNames += "msedge"
}

Stop-ProcessesByName -Names $processNames
Start-Sleep -Seconds 2

$profiles = Get-ChildItem -Path "C:\Users" -Directory -ErrorAction SilentlyContinue |
    Where-Object { $ExcludeUsers -notcontains $_.Name }

$summary = New-Object System.Collections.Generic.List[string]

foreach ($profile in $profiles) {
    $removed = Remove-UserChromeData -Profile $profile
    if ($removed.Count -gt 0) {
        $summary.Add(("{0}: {1}" -f $profile.Name, ($removed -join ", ")))
    }
}

$machineTargets = @(
    "C:\ProgramData\Google\Chrome",
    "C:\ProgramData\Google\Update"
)

if ($AlsoDeleteEdge) {
    $machineTargets += "C:\ProgramData\Microsoft\Edge"
}

foreach ($target in $machineTargets) {
    if (Remove-PathSafe -Path $target) {
        $summary.Add(("Machine: {0}" -f $target))
    }
}

if ($IncludeMachinePolicies) {
    $policyKeys = @(
        "HKLM:\SOFTWARE\Policies\Google\Chrome",
        "HKLM:\SOFTWARE\Policies\Google\Update"
    )

    if ($AlsoDeleteEdge) {
        $policyKeys += "HKLM:\SOFTWARE\Policies\Microsoft\Edge"
    }

    foreach ($key in $policyKeys) {
        if (Remove-RegistryTreeSafe -RegistryPath $key) {
            $summary.Add(("Policy: {0}" -f $key))
        }
    }
}

$report = @(
    "RESET CHROME TOTAL PORTABLE OK",
    ("Host: {0}" -f $env:COMPUTERNAME),
    ("Date: {0}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss")),
    ("IncludeMachinePolicies: {0}" -f [bool]$IncludeMachinePolicies),
    ("AlsoDeleteEdge: {0}" -f [bool]$AlsoDeleteEdge),
    "",
    "Elementos limpiados:"
)

if ($summary.Count -gt 0) {
    $report += ($summary | Sort-Object)
} else {
    $report += "No se encontraron datos de Chrome para limpiar."
}

$report | Set-Content -Path $doneFile -Encoding UTF8
Write-Log "=== RESET_CHROME_TOTAL_PORTABLE END ==="

Write-Host "Chrome limpiado." -ForegroundColor Green
Write-Host ("Log: {0}" -f $logFile)
Write-Host ("Resumen: {0}" -f $doneFile)
