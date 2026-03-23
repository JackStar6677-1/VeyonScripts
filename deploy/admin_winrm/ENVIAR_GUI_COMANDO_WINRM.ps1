param(
    [ValidateSet("launch", "keys")]
    [string]$Action,
    [string]$HostsFile = ".\hosts_castel.txt",
    [string[]]$UserCandidates = @("Colegio", "colegio", "Admin", "Administrador", "Usuario", "Alumno", "Estudiante", "Profesor"),
    [string]$PasswordPlain = "administrativa",
    [string]$Path = "",
    [string]$Arguments = "",
    [string]$WorkingDirectory = "",
    [string]$WindowTitle = "",
    [string]$Keys = "",
    [int]$DelayMs = 500,
    [int]$TimeoutSec = 15
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $HostsFile)) {
    Write-Host "[ERROR] No existe hosts file: $HostsFile" -ForegroundColor Red
    exit 1
}

$hosts = Get-Content $HostsFile |
    ForEach-Object { $_.Trim() } |
    Where-Object { $_ -and -not $_.StartsWith("#") } |
    Select-Object -Unique

$commandObject = [ordered]@{
    id = [guid]::NewGuid().ToString()
    createdAt = (Get-Date).ToString("s")
    action = $Action
    delayMs = $DelayMs
    timeoutSec = $TimeoutSec
}

if ($Action -eq "launch") {
    if ([string]::IsNullOrWhiteSpace($Path)) {
        Write-Host "[ERROR] launch requiere -Path" -ForegroundColor Red
        exit 1
    }
    $commandObject.path = $Path
    $commandObject.arguments = $Arguments
    $commandObject.workingDirectory = $WorkingDirectory
}

if ($Action -eq "keys") {
    if ([string]::IsNullOrWhiteSpace($WindowTitle) -or [string]::IsNullOrWhiteSpace($Keys)) {
        Write-Host "[ERROR] keys requiere -WindowTitle y -Keys" -ForegroundColor Red
        exit 1
    }
    $commandObject.windowTitle = $WindowTitle
    $commandObject.keys = $Keys
}

$commandJson = $commandObject | ConvertTo-Json -Depth 5
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

$remoteQueue = {
    param([string]$IncomingJson)

    $baseDir = "C:\ProgramData\CastelRemote"
    $queueDir = Join-Path $baseDir "queue"
    if (-not (Test-Path $queueDir)) {
        New-Item -ItemType Directory -Path $queueDir -Force | Out-Null
    }

    $activeUser = ""
    try {
        $line = (quser 2>$null | Select-String "Active" | Select-Object -First 1).ToString()
        if ($line) {
            $activeUser = (($line -split "\s+")[1]).Trim()
        }
    } catch {}

    $id = [guid]::NewGuid().ToString()
    $filePath = Join-Path $queueDir ("cmd_" + (Get-Date -Format "yyyyMMdd_HHmmss") + "_" + $id + ".json")
    Set-Content -Path $filePath -Value $IncomingJson -Encoding UTF8 -Force

    [pscustomobject]@{
        Computer = $env:COMPUTERNAME
        QueueFile = $filePath
        ActiveUser = $activeUser
    }
}

$results = @()
foreach ($h in $hosts) {
    $status = "FAIL"
    $detail = ""
    $activeUser = ""

    $portOpen = Test-NetConnection -ComputerName $h -Port 5985 -InformationLevel Quiet -WarningAction SilentlyContinue
    if (-not $portOpen) {
        $results += [pscustomobject]@{ Host = $h; Status = "NO_5985"; ActiveUser = ""; Detail = "WinRM cerrado" }
        continue
    }

    $cred = Get-WorkingCredential -ComputerName $h -Candidates $UserCandidates -Password $pass
    if ($null -eq $cred) {
        $results += [pscustomobject]@{ Host = $h; Status = "AUTH_FAIL"; ActiveUser = ""; Detail = "Sin credencial valida" }
        continue
    }

    try {
        $r = Invoke-Command -ComputerName $h -Credential $cred -ScriptBlock $remoteQueue -ArgumentList $commandJson -ErrorAction Stop
        $status = "QUEUED"
        $detail = $r.QueueFile
        $activeUser = $r.ActiveUser
    } catch {
        $status = "FAIL"
        $detail = $_.Exception.Message
    }

    $results += [pscustomobject]@{ Host = $h; Status = $status; ActiveUser = $activeUser; Detail = $detail }
}

$reportsDir = Join-Path (Split-Path $PSScriptRoot -Parent | Split-Path -Parent) ("reports\runs\" + (Get-Date -Format "yyyy-MM-dd") + "\admin_winrm")
if (-not (Test-Path $reportsDir)) { New-Item -ItemType Directory -Path $reportsDir -Force | Out-Null }
$reportsDir = (Resolve-Path $reportsDir).Path
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$report = Join-Path $reportsDir ("queue_gui_command_" + $timestamp + ".csv")
$results | Export-Csv -Path $report -NoTypeInformation -Encoding UTF8

$queued = ($results | Where-Object Status -eq "QUEUED").Count
$no = ($results | Where-Object Status -eq "NO_5985").Count
$auth = ($results | Where-Object Status -eq "AUTH_FAIL").Count
$fail = ($results | Where-Object Status -eq "FAIL").Count

Write-Host "TOTAL   : $($results.Count)"
Write-Host "QUEUED  : $queued"
Write-Host "NO_5985 : $no"
Write-Host "AUTH    : $auth"
Write-Host "FAIL    : $fail"
Write-Host "REPORTE : $report"
