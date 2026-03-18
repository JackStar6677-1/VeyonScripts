param(
    [string]$HostsFile = ".\hosts_castel.txt",
    [string[]]$UserCandidates = @("Colegio", "colegio", "Admin", "Administrador", "Usuario", "Alumno", "Estudiante", "Profesor"),
    [string]$PasswordPlain = "administrativa",
    [string]$PrinterName = "Brother Sala Computacion",
    [string]$PrinterIp = "192.168.0.208",
    [string]$PrinterMac = "30-05-5C-AA-AC-AE",
    [string]$PortName = "IP_192.168.0.208",
    [string]$DriverSourcePath = ""
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

if ($hosts.Count -eq 0) {
    Write-Host "[ERROR] hosts_castel.txt sin destinos" -ForegroundColor Red
    exit 1
}

if (-not [string]::IsNullOrWhiteSpace($DriverSourcePath) -and -not (Test-Path $DriverSourcePath)) {
    Write-Host "[ERROR] No existe DriverSourcePath: $DriverSourcePath" -ForegroundColor Red
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

$remotePrepareDriver = {
    param([string]$RemoteDriverDir)

    if (-not (Test-Path $RemoteDriverDir)) {
        New-Item -ItemType Directory -Path $RemoteDriverDir -Force | Out-Null
    }
}

$remoteInstall = {
    param(
        [string]$TargetPrinterName,
        [string]$TargetPrinterIp,
        [string]$TargetPrinterMac,
        [string]$TargetPortName,
        [string]$RemoteDriverDir
    )

    $existingPort = Get-PrinterPort -Name $TargetPortName -ErrorAction SilentlyContinue
    if ($null -eq $existingPort) {
        Add-PrinterPort -Name $TargetPortName -PrinterHostAddress $TargetPrinterIp -ErrorAction Stop
    }

    $installedDrivers = @(Get-PrinterDriver -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name)
    $preferredDrivers = @(
        "Brother DCP-L2540DW series",
        "Brother Laser Type1 Class Driver",
        "Microsoft IPP Class Driver"
    )

    $driverToUse = $null
    foreach ($driver in $preferredDrivers) {
        if ($installedDrivers -contains $driver) {
            $driverToUse = $driver
            break
        }
    }

    if ([string]::IsNullOrWhiteSpace($driverToUse) -and -not [string]::IsNullOrWhiteSpace($RemoteDriverDir) -and (Test-Path $RemoteDriverDir)) {
        & pnputil.exe /add-driver (Join-Path $RemoteDriverDir "*.inf") /subdirs /install | Out-Null
        $installedDrivers = @(Get-PrinterDriver -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name)
        foreach ($driver in $preferredDrivers) {
            if ($installedDrivers -contains $driver) {
                $driverToUse = $driver
                break
            }
        }
    }

    if ([string]::IsNullOrWhiteSpace($driverToUse)) {
        throw "No hay driver utilizable instalado. Drivers detectados: $($installedDrivers -join ', ')"
    }

    $existingPrinter = Get-Printer -Name $TargetPrinterName -ErrorAction SilentlyContinue
    if ($null -eq $existingPrinter) {
        Add-Printer -Name $TargetPrinterName -DriverName $driverToUse -PortName $TargetPortName -ErrorAction Stop | Out-Null
    } else {
        if ($existingPrinter.PortName -ne $TargetPortName) {
            Set-Printer -Name $TargetPrinterName -PortName $TargetPortName -ErrorAction Stop
        }
    }

    try {
        Set-Printer -Name $TargetPrinterName -Comment ("Brother DCP-L2540DW - IP " + $TargetPrinterIp + " - MAC " + $TargetPrinterMac) -ErrorAction SilentlyContinue
        Set-Printer -Name $TargetPrinterName -Location "Sala de Computacion" -ErrorAction SilentlyContinue
    } catch {}

    [pscustomobject]@{
        Computer = $env:COMPUTERNAME
        Printer = $TargetPrinterName
        Driver = $driverToUse
        Port = $TargetPortName
        Ip = $TargetPrinterIp
    }
}

$results = @()
foreach ($h in $hosts) {
    $portOpen = Test-NetConnection -ComputerName $h -Port 5985 -InformationLevel Quiet -WarningAction SilentlyContinue
    if (-not $portOpen) {
        $results += [pscustomobject]@{ Host = $h; Status = "NO_5985"; User = ""; Detail = "WinRM cerrado"; Driver = ""; Port = "" }
        continue
    }

    $cred = Get-WorkingCredential -ComputerName $h -Candidates $UserCandidates -Password $pass
    if ($null -eq $cred) {
        $results += [pscustomobject]@{ Host = $h; Status = "AUTH_FAIL"; User = ""; Detail = "Sin credencial valida"; Driver = ""; Port = "" }
        continue
    }

    $session = $null
    try {
        $session = New-PSSession -ComputerName $h -Credential $cred -ErrorAction Stop

        $remoteDriverDir = ""
        if (-not [string]::IsNullOrWhiteSpace($DriverSourcePath)) {
            $remoteDriverDir = "C:\ProgramData\CastelRemote\printer-driver-brother"
            Invoke-Command -Session $session -ScriptBlock $remotePrepareDriver -ArgumentList $remoteDriverDir -ErrorAction Stop | Out-Null
            Copy-Item -Path (Join-Path $DriverSourcePath "*") -Destination $remoteDriverDir -ToSession $session -Recurse -Force -ErrorAction Stop
        }

        $r = Invoke-Command -Session $session -ScriptBlock $remoteInstall -ArgumentList $PrinterName, $PrinterIp, $PrinterMac, $PortName, $remoteDriverDir -ErrorAction Stop
        $results += [pscustomobject]@{
            Host = $h
            Status = "OK"
            User = $cred.UserName
            Detail = $r.Printer
            Driver = $r.Driver
            Port = $r.Port
        }
    } catch {
        $results += [pscustomobject]@{
            Host = $h
            Status = "FAIL"
            User = $cred.UserName
            Detail = $_.Exception.Message
            Driver = ""
            Port = ""
        }
    } finally {
        if ($null -ne $session) {
            Remove-PSSession -Session $session -ErrorAction SilentlyContinue
        }
    }
}

$dayDir = Join-Path (Split-Path -Parent $PSScriptRoot) "..\reports\runs\$(Get-Date -Format 'yyyy-MM-dd')"
if (!(Test-Path $dayDir)) { New-Item -ItemType Directory -Path $dayDir -Force | Out-Null }
$dayDir = (Resolve-Path $dayDir).Path
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$csv = Join-Path $dayDir ("winrm_brother_printer_apply_" + $ts + ".csv")

$results | Sort-Object Host | Export-Csv -Path $csv -NoTypeInformation -Encoding UTF8

$ok = ($results | Where-Object Status -eq "OK").Count
$no = ($results | Where-Object Status -eq "NO_5985").Count
$auth = ($results | Where-Object Status -eq "AUTH_FAIL").Count
$fail = ($results | Where-Object Status -eq "FAIL").Count

Write-Host "TOTAL   : $($results.Count)"
Write-Host "OK      : $ok"
Write-Host "NO_5985 : $no"
Write-Host "AUTH    : $auth"
Write-Host "FAIL    : $fail"
Write-Host "REPORTE : $csv"
