param(
    [string]$HostsFile = ".\hosts_castel.txt",
    [string[]]$UserCandidates = @("Colegio", "colegio", "Admin", "Administrador", "Usuario", "Alumno", "Estudiante", "Profesor"),
    [string]$PasswordPlain = "administrativa"
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
    $removed = New-Object System.Collections.Generic.List[string]
    $remaining = New-Object System.Collections.Generic.List[string]

    $targetNames = @(
        "JackOptimized-AutoShutdown-1730",
        "JackOptimized-AutoLogoff-1730"
    )

    foreach ($taskName in $targetNames) {
        $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
        if ($null -ne $task) {
            try {
                Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction Stop
                $removed.Add($taskName)
            } catch {
                $remaining.Add($taskName)
            }
        }
    }

    $otherTasks = Get-ScheduledTask -ErrorAction SilentlyContinue | Where-Object {
        $_.TaskPath -notlike "\Microsoft\*" -and (
            $_.Actions.Execute -match "(?i)shutdown(\.exe)?$" -or
            $_.Actions.Execute -match "(?i)logoff(\.exe)?$" -or
            $_.Actions.Arguments -match "(?i)(^|\s)/s(\s|$)" -or
            $_.Actions.Arguments -match "(?i)\blogoff\b"
        )
    }

    foreach ($task in $otherTasks) {
        if ($removed.Contains($task.TaskName)) {
            continue
        }

        try {
            Unregister-ScheduledTask -TaskName $task.TaskName -TaskPath $task.TaskPath -Confirm:$false -ErrorAction Stop
            $removed.Add(($task.TaskPath + $task.TaskName))
        } catch {
            $remaining.Add(($task.TaskPath + $task.TaskName))
        }
    }

    [pscustomobject]@{
        Computer = $env:COMPUTERNAME
        Removed = ($removed -join "; ")
        Remaining = ($remaining -join "; ")
    }
}

$results = @()
foreach ($h in $hosts) {
    $portOpen = Test-NetConnection -ComputerName $h -Port 5985 -InformationLevel Quiet -WarningAction SilentlyContinue
    if (-not $portOpen) {
        $results += [pscustomobject]@{ Host = $h; Status = "NO_5985"; Detail = "WinRM cerrado"; Removed = ""; Remaining = "" }
        continue
    }

    $cred = Get-WorkingCredential -ComputerName $h -Candidates $UserCandidates -Password $pass
    if ($null -eq $cred) {
        $results += [pscustomobject]@{ Host = $h; Status = "AUTH_FAIL"; Detail = "Sin credencial valida"; Removed = ""; Remaining = "" }
        continue
    }

    try {
        $r = Invoke-Command -ComputerName $h -Credential $cred -ScriptBlock $scriptBlock -ErrorAction Stop
        $results += [pscustomobject]@{
            Host = $h
            Status = "OK"
            Detail = $r.Computer
            Removed = $r.Removed
            Remaining = $r.Remaining
        }
    } catch {
        $results += [pscustomobject]@{
            Host = $h
            Status = "FAIL"
            Detail = $_.Exception.Message
            Removed = ""
            Remaining = ""
        }
    }
}

$dayDir = Join-Path (Split-Path -Parent $PSScriptRoot) "..\reports\runs\$(Get-Date -Format 'yyyy-MM-dd')"
if (!(Test-Path $dayDir)) { New-Item -ItemType Directory -Path $dayDir -Force | Out-Null }
$dayDir = (Resolve-Path $dayDir).Path
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$csv = Join-Path $dayDir ("winrm_remove_shutdown_tasks_" + $ts + ".csv")

$results | Sort-Object Host | Export-Csv -Path $csv -NoTypeInformation -Encoding UTF8

$ok = ($results | Where-Object Status -eq "OK").Count
$removedHosts = ($results | Where-Object { $_.Removed }).Count
$no = ($results | Where-Object Status -eq "NO_5985").Count
$auth = ($results | Where-Object Status -eq "AUTH_FAIL").Count
$fail = ($results | Where-Object Status -eq "FAIL").Count

Write-Host "TOTAL          : $($results.Count)"
Write-Host "OK             : $ok"
Write-Host "REMOVED_HOSTS  : $removedHosts"
Write-Host "NO_5985        : $no"
Write-Host "AUTH_FAIL      : $auth"
Write-Host "FAIL           : $fail"
Write-Host "REPORTE        : $csv"
