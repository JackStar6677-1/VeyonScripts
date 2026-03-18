param(
    [string]$HostsFile = ".\hosts_castel.txt",
    [string[]]$UserCandidates = @("Colegio", "colegio", "Admin", "Administrador", "Usuario", "Alumno", "Estudiante", "Profesor"),
    [string]$PasswordPlain = "administrativa",
    [string]$LocalAgentPath = "..\componentes_cliente\GUI_AGENTE_INTERACTIVO.ps1"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $HostsFile)) {
    Write-Host "[ERROR] No existe hosts file: $HostsFile" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $LocalAgentPath)) {
    Write-Host "[ERROR] No existe agente local: $LocalAgentPath" -ForegroundColor Red
    exit 1
}

$hosts = Get-Content $HostsFile |
    ForEach-Object { $_.Trim() } |
    Where-Object { $_ -and -not $_.StartsWith("#") } |
    Select-Object -Unique

$agentContent = Get-Content -Path $LocalAgentPath -Raw -Encoding UTF8
$pass = ConvertTo-SecureString $PasswordPlain -AsPlainText -Force

function Get-WorkingCredential {
    param(
        [string]$ComputerName,
        [string[]]$Candidates,
        [securestring]$Password
    )

    $variants = @()
    foreach ($u in $Candidates) {
        $variants += "$ComputerName\$u"
        $variants += ".\$u"
        $variants += $u
    }
    $variants = $variants | Select-Object -Unique

    foreach ($name in $variants) {
        try {
            $cred = New-Object System.Management.Automation.PSCredential($name, $Password)
            Invoke-Command -ComputerName $ComputerName -Credential $cred -ScriptBlock { "OK" } -ErrorAction Stop | Out-Null
            return $cred
        } catch {
            continue
        }
    }

    return $null
}

$remoteInstall = {
    param([string]$IncomingAgentContent)

    $baseDir = "C:\ProgramData\CastelRemote"
    $queueDir = Join-Path $baseDir "queue"
    $processingDir = Join-Path $baseDir "processing"
    $processedDir = Join-Path $baseDir "processed"
    $logDir = Join-Path $baseDir "logs"
    $agentPath = Join-Path $baseDir "GUI_AGENTE_INTERACTIVO.ps1"
    $startupDir = "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup"
    $launcherPath = Join-Path $startupDir "Castel GUI Agent.cmd"

    foreach ($dir in @($baseDir, $queueDir, $processingDir, $processedDir, $logDir, $startupDir)) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }

    Set-Content -Path $agentPath -Value $IncomingAgentContent -Encoding UTF8 -Force

    $launcher = @(
        "@echo off",
        "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File ""C:\ProgramData\CastelRemote\GUI_AGENTE_INTERACTIVO.ps1"""
    )
    Set-Content -Path $launcherPath -Value $launcher -Encoding ASCII -Force

    [pscustomobject]@{
        Computer = $env:COMPUTERNAME
        AgentPath = $agentPath
        StartupLauncher = $launcherPath
    }
}

$results = @()
foreach ($h in $hosts) {
    $status = "FAIL"
    $detail = ""
    $userUsed = ""

    $portOpen = Test-NetConnection -ComputerName $h -Port 5985 -InformationLevel Quiet -WarningAction SilentlyContinue
    if (-not $portOpen) {
        $results += [pscustomobject]@{ Host = $h; Status = "NO_5985"; User = ""; Detail = "WinRM cerrado" }
        continue
    }

    $cred = Get-WorkingCredential -ComputerName $h -Candidates $UserCandidates -Password $pass
    if ($null -eq $cred) {
        $results += [pscustomobject]@{ Host = $h; Status = "AUTH_FAIL"; User = ""; Detail = "Sin credencial valida" }
        continue
    }

    $userUsed = $cred.UserName
    try {
        $r = Invoke-Command -ComputerName $h -Credential $cred -ScriptBlock $remoteInstall -ArgumentList $agentContent -ErrorAction Stop
        $status = "OK"
        $detail = $r.AgentPath
    } catch {
        $status = "FAIL"
        $detail = $_.Exception.Message
    }

    $results += [pscustomobject]@{ Host = $h; Status = $status; User = $userUsed; Detail = $detail }
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$report = Join-Path $PSScriptRoot ("install_gui_agent_" + $timestamp + ".csv")
$results | Export-Csv -Path $report -NoTypeInformation -Encoding UTF8

$ok = ($results | Where-Object Status -eq "OK").Count
$no = ($results | Where-Object Status -eq "NO_5985").Count
$auth = ($results | Where-Object Status -eq "AUTH_FAIL").Count
$fail = ($results | Where-Object Status -eq "FAIL").Count

Write-Host "TOTAL   : $($results.Count)"
Write-Host "OK      : $ok"
Write-Host "NO_5985 : $no"
Write-Host "AUTH    : $auth"
Write-Host "FAIL    : $fail"
Write-Host "REPORTE : $report"
