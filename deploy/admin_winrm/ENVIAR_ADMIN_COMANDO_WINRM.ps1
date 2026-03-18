param(
    [ValidateSet("powershell_file", "powershell_inline", "cmd")]
    [string]$Action,
    [string]$HostsFile = ".\hosts_castel.txt",
    [string[]]$UserCandidates = @("Colegio", "colegio", "Admin", "Administrador", "Usuario", "Alumno", "Estudiante", "Profesor"),
    [string]$PasswordPlain = "administrativa",
    [string]$Path = "",
    [string]$Arguments = "",
    [string]$Code = "",
    [string]$Command = ""
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
}

switch ($Action) {
    "powershell_file" {
        if ([string]::IsNullOrWhiteSpace($Path)) {
            Write-Host "[ERROR] powershell_file requiere -Path" -ForegroundColor Red
            exit 1
        }
        $commandObject.path = $Path
        $commandObject.arguments = $Arguments
    }
    "powershell_inline" {
        if ([string]::IsNullOrWhiteSpace($Code)) {
            Write-Host "[ERROR] powershell_inline requiere -Code" -ForegroundColor Red
            exit 1
        }
        $commandObject.code = $Code
    }
    "cmd" {
        if ([string]::IsNullOrWhiteSpace($Command)) {
            Write-Host "[ERROR] cmd requiere -Command" -ForegroundColor Red
            exit 1
        }
        $commandObject.command = $Command
    }
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
    $queueDir = Join-Path $baseDir "admin-queue"
    $taskName = "Castel-AdminBridge"

    if (-not (Test-Path $queueDir)) {
        New-Item -ItemType Directory -Path $queueDir -Force | Out-Null
    }

    $id = [guid]::NewGuid().ToString()
    $filePath = Join-Path $queueDir ("admin_" + (Get-Date -Format "yyyyMMdd_HHmmss") + "_" + $id + ".json")
    Set-Content -Path $filePath -Value $IncomingJson -Encoding UTF8 -Force

    schtasks.exe /Run /TN $taskName | Out-Null

    [pscustomobject]@{
        Computer = $env:COMPUTERNAME
        QueueFile = $filePath
        TaskName = $taskName
    }
}

$results = @()
foreach ($h in $hosts) {
    $status = "FAIL"
    $detail = ""

    $portOpen = Test-NetConnection -ComputerName $h -Port 5985 -InformationLevel Quiet -WarningAction SilentlyContinue
    if (-not $portOpen) {
        $results += [pscustomobject]@{ Host = $h; Status = "NO_5985"; Detail = "WinRM cerrado" }
        continue
    }

    $cred = Get-WorkingCredential -ComputerName $h -Candidates $UserCandidates -Password $pass
    if ($null -eq $cred) {
        $results += [pscustomobject]@{ Host = $h; Status = "AUTH_FAIL"; Detail = "Sin credencial valida" }
        continue
    }

    try {
        $r = Invoke-Command -ComputerName $h -Credential $cred -ScriptBlock $remoteQueue -ArgumentList $commandJson -ErrorAction Stop
        $status = "QUEUED"
        $detail = $r.QueueFile
    } catch {
        $status = "FAIL"
        $detail = $_.Exception.Message
    }

    $results += [pscustomobject]@{ Host = $h; Status = $status; Detail = $detail }
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$report = Join-Path $PSScriptRoot ("queue_admin_command_" + $timestamp + ".csv")
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
