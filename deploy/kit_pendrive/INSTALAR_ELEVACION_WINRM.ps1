param(
    [string]$HostsFile = ".\hosts_castel.txt",
    [string[]]$UserCandidates = @("Colegio", "colegio", "Admin", "Administrador", "Usuario", "Alumno", "Estudiante", "Profesor"),
    [string]$PasswordPlain = "administrativa",
    [string]$LocalBridgePath = ".\ADMIN_ELEVATION_BRIDGE.ps1",
    [string[]]$LocalPayloadPaths = @(
        ".\RESET_CHROME_COMPARTIDO.ps1",
        ".\PROTEGER_MATERIALES_SALA.ps1",
        ".\CREAR_CARPETA_ENTREGA_SALA.ps1"
    )
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $HostsFile)) {
    Write-Host "[ERROR] No existe hosts file: $HostsFile" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $LocalBridgePath)) {
    Write-Host "[ERROR] No existe bridge local: $LocalBridgePath" -ForegroundColor Red
    exit 1
}

$hosts = Get-Content $HostsFile |
    ForEach-Object { $_.Trim() } |
    Where-Object { $_ -and -not $_.StartsWith("#") } |
    Select-Object -Unique

$bridgeContent = Get-Content -Path $LocalBridgePath -Raw -Encoding UTF8
$payloads = @()
foreach ($payloadPath in $LocalPayloadPaths) {
    if (Test-Path $payloadPath) {
        $payloads += [pscustomobject]@{
            Name = [IO.Path]::GetFileName($payloadPath)
            Content = Get-Content -Path $payloadPath -Raw -Encoding UTF8
        }
    }
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

$remoteInstall = {
    param(
        [string]$IncomingBridgeContent,
        [object[]]$IncomingPayloads
    )

    $baseDir = "C:\ProgramData\CastelRemote"
    $queueDir = Join-Path $baseDir "admin-queue"
    $processedDir = Join-Path $baseDir "admin-processed"
    $logDir = Join-Path $baseDir "logs"
    $bridgePath = Join-Path $baseDir "ADMIN_ELEVATION_BRIDGE.ps1"
    $taskName = "Castel-AdminBridge"

    foreach ($dir in @($baseDir, $queueDir, $processedDir, $logDir)) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }

    Set-Content -Path $bridgePath -Value $IncomingBridgeContent -Encoding UTF8 -Force

    foreach ($payload in $IncomingPayloads) {
        if ($payload.Name -and $payload.Content) {
            $payloadPath = Join-Path $baseDir $payload.Name
            Set-Content -Path $payloadPath -Value $payload.Content -Encoding UTF8 -Force
        }
    }

    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$bridgePath`""
    $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

    Register-ScheduledTask -TaskName $taskName -Action $action -Principal $principal -Settings $settings -Force | Out-Null

    [pscustomobject]@{
        Computer = $env:COMPUTERNAME
        BridgePath = $bridgePath
        TaskName = $taskName
        Payloads = ($IncomingPayloads | ForEach-Object { $_.Name }) -join "; "
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
        $r = Invoke-Command -ComputerName $h -Credential $cred -ScriptBlock $remoteInstall -ArgumentList $bridgeContent, $payloads -ErrorAction Stop
        $status = "OK"
        $detail = ($r.TaskName + " | Payloads: " + $r.Payloads)
    } catch {
        $status = "FAIL"
        $detail = $_.Exception.Message
    }

    $results += [pscustomobject]@{ Host = $h; Status = $status; User = $userUsed; Detail = $detail }
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$report = Join-Path $PSScriptRoot ("install_admin_bridge_" + $timestamp + ".csv")
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
