param(
    [string]$HostsFile = ".\hosts_castel.txt",
    [string[]]$UserCandidates = @("Colegio", "colegio", "Admin", "Usuario", "Alumno", "Estudiante", "Profesor"),
    [string]$PasswordPlain = "administrativa",
    [string]$EndDateIso = "2026-12-31T23:59:59"
)

$ErrorActionPreference = "Stop"

if (!(Test-Path $HostsFile)) {
    Write-Host "[ERROR] No existe hosts file: $HostsFile" -ForegroundColor Red
    exit 1
}

$hosts = Get-Content $HostsFile |
    ForEach-Object { $_.Trim() } |
    Where-Object { $_ -and -not $_.StartsWith("#") } |
    Select-Object -Unique

if ($hosts.Count -eq 0) {
    Write-Host "[ERROR] hosts_castel.txt sin destinos" -ForegroundColor Red
    exit 1
}

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

$scriptBlock = {
    param($EndDateIso)
    $taskName = "JackOptimized-AutoShutdown-1730"
    $action = New-ScheduledTaskAction -Execute "shutdown.exe" -Argument "/s /f /t 60 /c `"Apagado automatico 17:30 sala computacion`""
    $trigger = New-ScheduledTaskTrigger -Daily -At "17:30"
    $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
    # No usar StartWhenAvailable aqui: si el equipo estuvo apagado a las 17:30,
    # la tarea "perdida" puede ejecutarse al volver a encenderlo por la manana.
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null

    # EndBoundary no viene expuesto directamente en New-ScheduledTaskTrigger, se ajusta luego.
    $task = Get-ScheduledTask -TaskName $taskName
    if ($task.Triggers.Count -gt 0) {
        $task.Triggers[0].EndBoundary = $EndDateIso
        Set-ScheduledTask -InputObject $task | Out-Null
    }

    # Marcar evidencia local
    "OK $(Get-Date -Format s)" | Set-Content -Path "C:\Windows\Temp\jackoptimized_power_schedule.txt" -Encoding UTF8
    return "OK"
}

$results = @()
foreach ($h in $hosts) {
    $status = "FAIL"
    $userUsed = ""
    $detail = ""

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
        Invoke-Command -ComputerName $h -Credential $cred -ScriptBlock $scriptBlock -ArgumentList $EndDateIso -ErrorAction Stop | Out-Null
        $status = "OK"
        $detail = "Tarea diaria 17:30 creada"
    } catch {
        $status = "FAIL"
        $detail = $_.Exception.Message
    }

    $results += [pscustomobject]@{ Host = $h; Status = $status; User = $userUsed; Detail = $detail }
}

$dayDir = Join-Path (Split-Path -Parent $PSScriptRoot) "..\reports\runs\2026-03-05"
if (!(Test-Path $dayDir)) { New-Item -ItemType Directory -Path $dayDir -Force | Out-Null }
$dayDir = (Resolve-Path $dayDir).Path
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$csv = Join-Path $dayDir ("programar_energia_winrm_" + $ts + ".csv")
$txt = Join-Path $dayDir ("programar_energia_winrm_" + $ts + ".txt")

$results | Sort-Object Host | Export-Csv -Path $csv -NoTypeInformation -Encoding UTF8

$ok = ($results | Where-Object Status -eq "OK").Count
$no = ($results | Where-Object Status -eq "NO_5985").Count
$auth = ($results | Where-Object Status -eq "AUTH_FAIL").Count
$fail = ($results | Where-Object Status -eq "FAIL").Count

@(
    "TOTAL=$($results.Count)",
    "OK=$ok",
    "NO_5985=$no",
    "AUTH_FAIL=$auth",
    "FAIL=$fail",
    "CSV=$csv",
    "",
    "NO_5985:",
    ($results | Where-Object Status -eq "NO_5985" | Sort-Object Host | ForEach-Object { "- $($_.Host)" }),
    "",
    "AUTH_FAIL:",
    ($results | Where-Object Status -eq "AUTH_FAIL" | Sort-Object Host | ForEach-Object { "- $($_.Host)" }),
    "",
    "FAIL:",
    ($results | Where-Object Status -eq "FAIL" | Sort-Object Host | ForEach-Object { "- $($_.Host)" })
) | Set-Content -Path $txt -Encoding UTF8

Get-Content $txt
