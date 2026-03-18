param(
    [string]$HostsFile = ".\hosts_castel.txt",
    [string[]]$UserCandidates = @("Colegio", "colegio", "Admin", "Administrador", "Usuario", "Alumno", "Estudiante", "Profesor"),
    [string]$PasswordPlain = "administrativa",
    [string]$LocalHelperPath = "..\componentes_cliente\MOSTRAR_IP_MAC.bat"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $HostsFile)) {
    Write-Host "[ERROR] No existe hosts file: $HostsFile" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $LocalHelperPath)) {
    Write-Host "[ERROR] No existe helper local: $LocalHelperPath" -ForegroundColor Red
    exit 1
}

$hosts = Get-Content $HostsFile |
    ForEach-Object { $_.Trim() } |
    Where-Object { $_ -and -not $_.StartsWith("#") } |
    Select-Object -Unique

$helperContent = Get-Content -Path $LocalHelperPath -Raw -Encoding ASCII
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
    param([string]$IncomingContent)

    $publicDesktop = "C:\Users\Public\Desktop"
    $programDataDir = "C:\ProgramData\CastelRemote"
    $desktopPath = Join-Path $publicDesktop "MOSTRAR_IP_MAC.bat"
    $internalPath = Join-Path $programDataDir "MOSTRAR_IP_MAC.bat"

    foreach ($dir in @($publicDesktop, $programDataDir)) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }

    Set-Content -Path $desktopPath -Value $IncomingContent -Encoding ASCII -Force
    Set-Content -Path $internalPath -Value $IncomingContent -Encoding ASCII -Force

    [pscustomobject]@{
        Computer = $env:COMPUTERNAME
        DesktopPath = $desktopPath
        InternalPath = $internalPath
    }
}

$results = @()
foreach ($h in $hosts) {
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

    try {
        $r = Invoke-Command -ComputerName $h -Credential $cred -ScriptBlock $remoteInstall -ArgumentList $helperContent -ErrorAction Stop
        $results += [pscustomobject]@{ Host = $h; Status = "OK"; User = $cred.UserName; Detail = $r.DesktopPath }
    } catch {
        $results += [pscustomobject]@{ Host = $h; Status = "FAIL"; User = $cred.UserName; Detail = $_.Exception.Message }
    }
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$report = Join-Path $PSScriptRoot ("deploy_ip_mac_helper_" + $timestamp + ".csv")
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
