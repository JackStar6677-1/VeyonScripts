param(
    [string]$TargetScript = ".\payload.ps1",
    [string]$HostsFile = ".\hosts_castel.txt",
    [string[]]$UserCandidates = @("Admin", "Profesor", "Usuario")
)

$ErrorActionPreference = "Stop"

Write-Host "==============================================="
Write-Host " EJECUCION MASIVA (AUTO USUARIO + MISMA CLAVE)"
Write-Host "==============================================="
Write-Host "Hosts    : $HostsFile"
Write-Host "Script   : $TargetScript"
Write-Host "Usuarios : $($UserCandidates -join ', ')"
Write-Host ""

if (!(Test-Path $HostsFile)) {
    Write-Host "[ERROR] No existe el archivo de hosts: $HostsFile" -ForegroundColor Red
    exit 1
}

if (!(Test-Path $TargetScript)) {
    Write-Host "[ERROR] No existe el script objetivo: $TargetScript" -ForegroundColor Red
    Write-Host "Crea payload.ps1 o payload.bat en esta misma carpeta." -ForegroundColor Yellow
    exit 1
}

$hosts = Get-Content $HostsFile |
    ForEach-Object { $_.Trim() } |
    Where-Object { $_ -and -not $_.StartsWith("#") } |
    Select-Object -Unique

if ($hosts.Count -eq 0) {
    Write-Host "[ERROR] Hosts vacio: $HostsFile" -ForegroundColor Red
    exit 1
}

# Una sola clave para todos (ej: administrativa)
$passSecure = Read-Host "Contrasena comun (ej: administrativa)" -AsSecureString

$ext = [IO.Path]::GetExtension((Resolve-Path $TargetScript).Path).ToLowerInvariant()
$scriptPath = (Resolve-Path $TargetScript).Path
$reportsDir = Join-Path (Split-Path $PSScriptRoot -Parent | Split-Path -Parent) ("reports\runs\" + (Get-Date -Format "yyyy-MM-dd") + "\admin_winrm")
if (-not (Test-Path $reportsDir)) { New-Item -ItemType Directory -Path $reportsDir -Force | Out-Null }
$reportsDir = (Resolve-Path $reportsDir).Path
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$report = Join-Path $reportsDir ("reporte_auto_cred_" + $timestamp + ".csv")
$results = @()

function Invoke-BatRemote {
    param(
        [string]$ComputerName,
        [pscredential]$Credential,
        [string]$BatPath
    )
    $content = Get-Content $BatPath -Raw -Encoding UTF8
    Invoke-Command -ComputerName $ComputerName -Credential $Credential -ErrorAction Stop -ScriptBlock {
        param($batContent)
        $tmp = Join-Path $env:TEMP ("payload_" + [guid]::NewGuid().ToString() + ".bat")
        Set-Content -Path $tmp -Value $batContent -Encoding ASCII -Force
        cmd.exe /c $tmp
        $rc = $LASTEXITCODE
        Remove-Item $tmp -Force -ErrorAction SilentlyContinue
        return $rc
    } -ArgumentList $content
}

function Get-WorkingCredential {
    param(
        [string]$ComputerName,
        [string[]]$Candidates,
        [securestring]$Password
    )

    $nameVariants = @()
    foreach ($u in $Candidates) {
        $nameVariants += "$ComputerName\$u"
        $nameVariants += ".\$u"
        $nameVariants += $u
    }
    $nameVariants = $nameVariants | Select-Object -Unique

    foreach ($name in $nameVariants) {
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

foreach ($h in $hosts) {
    $start = Get-Date
    $status = "OK"
    $detail = ""
    $duration = 0
    $userUsed = ""

    Write-Host "[$h] Verificando WinRM (5985)..."
    $portOpen = Test-NetConnection -ComputerName $h -Port 5985 -InformationLevel Quiet -WarningAction SilentlyContinue
    if (-not $portOpen) {
        $status = "NO_WINRM"
        $detail = "Puerto 5985 cerrado o host no accesible"
        $duration = [math]::Round(((Get-Date) - $start).TotalSeconds, 2)
        Write-Host "[$h] $status - $detail" -ForegroundColor Yellow
        $results += [pscustomobject]@{
            Host = $h; User = $userUsed; Status = $status; Detail = $detail; DurationSec = $duration
        }
        continue
    }

    Write-Host "[$h] Buscando usuario valido..."
    $cred = Get-WorkingCredential -ComputerName $h -Candidates $UserCandidates -Password $passSecure
    if ($null -eq $cred) {
        $status = "AUTH_FAIL"
        $detail = "No funciono ningun usuario candidato con la clave indicada"
        $duration = [math]::Round(((Get-Date) - $start).TotalSeconds, 2)
        Write-Host "[$h] $status - $detail" -ForegroundColor Red
        $results += [pscustomobject]@{
            Host = $h; User = $userUsed; Status = $status; Detail = $detail; DurationSec = $duration
        }
        continue
    }

    $userUsed = $cred.UserName

    try {
        if ($ext -eq ".ps1") {
            Write-Host "[$h] Ejecutando PS1 remoto con $userUsed ..."
            Invoke-Command -ComputerName $h -Credential $cred -FilePath $scriptPath -ErrorAction Stop | Out-Null
        }
        elseif ($ext -eq ".bat" -or $ext -eq ".cmd") {
            Write-Host "[$h] Ejecutando BAT/CMD remoto con $userUsed ..."
            $rc = Invoke-BatRemote -ComputerName $h -Credential $cred -BatPath $scriptPath
            if ($rc -ne 0) {
                throw "BAT remoto devolvio codigo $rc"
            }
        }
        else {
            throw "Extension no soportada: $ext (usa .ps1, .bat o .cmd)"
        }
    }
    catch {
        $status = "ERROR"
        $detail = $_.Exception.Message
    }

    $duration = [math]::Round(((Get-Date) - $start).TotalSeconds, 2)
    if ($status -eq "OK") {
        Write-Host "[$h] OK ($duration s) [$userUsed]" -ForegroundColor Green
    } else {
        Write-Host "[$h] $status - $detail [$userUsed]" -ForegroundColor Red
    }

    $results += [pscustomobject]@{
        Host = $h
        User = $userUsed
        Status = $status
        Detail = $detail
        DurationSec = $duration
    }
}

$results | Export-Csv -Path $report -NoTypeInformation -Encoding UTF8

$ok = ($results | Where-Object { $_.Status -eq "OK" }).Count
$nowinrm = ($results | Where-Object { $_.Status -eq "NO_WINRM" }).Count
$auth = ($results | Where-Object { $_.Status -eq "AUTH_FAIL" }).Count
$err = ($results | Where-Object { $_.Status -eq "ERROR" }).Count

Write-Host ""
Write-Host "==============================================="
Write-Host " RESUMEN"
Write-Host "==============================================="
Write-Host "Total    : $($results.Count)"
Write-Host "OK       : $ok"
Write-Host "NO_WINRM : $nowinrm"
Write-Host "AUTH_FAIL: $auth"
Write-Host "ERROR    : $err"
Write-Host "Reporte  : $report"
Write-Host "==============================================="
