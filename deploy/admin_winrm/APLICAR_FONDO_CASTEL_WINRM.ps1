param(
    [string]$HostsFile = ".\hosts_castel.txt",
    [string[]]$UserCandidates = @("Colegio", "colegio", "Admin", "Administrador", "Usuario", "Alumno", "Estudiante", "Profesor"),
    [string]$PasswordPlain = "administrativa",
    [string]$SourceImagePath = "C:\Users\Profesor\Downloads\Fondo De pantalla Castel.jpg",
    [string]$RemoteImagePath = "C:\ProgramData\CastelRemote\wallpapers\CastelWallpaper.jpg"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $HostsFile)) {
    Write-Host "[ERROR] No existe hosts file: $HostsFile" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $SourceImagePath)) {
    Write-Host "[ERROR] No existe imagen local: $SourceImagePath" -ForegroundColor Red
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

$remotePrepare = {
    param([string]$TargetImagePath)

    $dir = Split-Path -Parent $TargetImagePath
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }

    [pscustomobject]@{
        Computer = $env:COMPUTERNAME
        TargetDir = $dir
    }
}

$remoteApply = {
    param([string]$TargetImagePath)

function Set-WallpaperValues {
        param(
            [Microsoft.Win32.RegistryKey]$RootKey,
            [string]$RelativePath,
            [string]$ImagePath
        )

        $desktop = $RootKey.CreateSubKey($RelativePath + "\Control Panel\Desktop")
        $desktop.SetValue("Wallpaper", $ImagePath, [Microsoft.Win32.RegistryValueKind]::String)
        $desktop.SetValue("WallpaperStyle", "10", [Microsoft.Win32.RegistryValueKind]::String)
        $desktop.SetValue("TileWallpaper", "0", [Microsoft.Win32.RegistryValueKind]::String)
        $desktop.Close()
    }

    function Clear-WallpaperPolicyValues {
        param(
            [Microsoft.Win32.RegistryKey]$RootKey,
            [string]$RelativePath
        )

        $policyPath = $RelativePath + "\Software\Microsoft\Windows\CurrentVersion\Policies\System"
        $policy = $RootKey.OpenSubKey($policyPath, $true)
        if ($null -ne $policy) {
            foreach ($name in @("Wallpaper", "WallpaperStyle", "NoChangingWallPaper")) {
                if ($null -ne $policy.GetValue($name, $null)) {
                    $policy.DeleteValue($name, $false)
                }
            }
            $policy.Close()
        }
    }

    if (-not (Test-Path $TargetImagePath)) {
        throw "No existe imagen remota: $TargetImagePath"
    }

    $localMachine = [Microsoft.Win32.RegistryKey]::OpenBaseKey([Microsoft.Win32.RegistryHive]::LocalMachine, [Microsoft.Win32.RegistryView]::Default)
    $usersRoot = [Microsoft.Win32.RegistryKey]::OpenBaseKey([Microsoft.Win32.RegistryHive]::Users, [Microsoft.Win32.RegistryView]::Default)

    Clear-WallpaperPolicyValues -RootKey $localMachine -RelativePath "SOFTWARE"

    $profileListPath = "SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList"
    $profileList = $localMachine.OpenSubKey($profileListPath)
    $loadedSids = @($usersRoot.GetSubKeyNames())
    $updatedProfiles = New-Object System.Collections.Generic.List[string]

    foreach ($sid in $profileList.GetSubKeyNames()) {
        if ($sid -notmatch '^S-1-5-21-') {
            continue
        }

        $profileKey = $profileList.OpenSubKey($sid)
        if ($null -eq $profileKey) {
            continue
        }

        $profileImagePath = $profileKey.GetValue("ProfileImagePath")
        $profileKey.Close()

        if ([string]::IsNullOrWhiteSpace($profileImagePath)) {
            continue
        }

        if ($loadedSids -contains $sid) {
            Set-WallpaperValues -RootKey $usersRoot -RelativePath $sid -ImagePath $TargetImagePath
            Clear-WallpaperPolicyValues -RootKey $usersRoot -RelativePath $sid
            $updatedProfiles.Add($profileImagePath)
            continue
        }

        $ntUserDat = Join-Path $profileImagePath "NTUSER.DAT"
        if (-not (Test-Path $ntUserDat)) {
            continue
        }

        $tempHive = "CastelTemp_" + ([guid]::NewGuid().ToString("N"))
        & reg.exe load ("HKU\" + $tempHive) $ntUserDat | Out-Null
        if ($LASTEXITCODE -eq 0) {
            try {
                Set-WallpaperValues -RootKey $usersRoot -RelativePath $tempHive -ImagePath $TargetImagePath
                Clear-WallpaperPolicyValues -RootKey $usersRoot -RelativePath $tempHive
                $updatedProfiles.Add($profileImagePath)
            } finally {
                & reg.exe unload ("HKU\" + $tempHive) | Out-Null
            }
        }
    }

    $defaultNtUser = "C:\Users\Default\NTUSER.DAT"
    if (Test-Path $defaultNtUser) {
        $defaultHive = "CastelDefault_" + ([guid]::NewGuid().ToString("N"))
        & reg.exe load ("HKU\" + $defaultHive) $defaultNtUser | Out-Null
        if ($LASTEXITCODE -eq 0) {
            try {
                Set-WallpaperValues -RootKey $usersRoot -RelativePath $defaultHive -ImagePath $TargetImagePath
                Clear-WallpaperPolicyValues -RootKey $usersRoot -RelativePath $defaultHive
            } finally {
                & reg.exe unload ("HKU\" + $defaultHive) | Out-Null
            }
        }
    }

    try {
        Start-Process -FilePath "RUNDLL32.EXE" -ArgumentList "USER32.DLL,UpdatePerUserSystemParameters" -WindowStyle Hidden | Out-Null
    } catch {}

    [pscustomobject]@{
        Computer = $env:COMPUTERNAME
        UpdatedProfiles = ($updatedProfiles | Select-Object -Unique) -join "; "
        RemoteImagePath = $TargetImagePath
    }
}

$results = @()
foreach ($h in $hosts) {
    $portOpen = Test-NetConnection -ComputerName $h -Port 5985 -InformationLevel Quiet -WarningAction SilentlyContinue
    if (-not $portOpen) {
        $results += [pscustomobject]@{ Host = $h; Status = "NO_5985"; User = ""; Detail = "WinRM cerrado"; RemoteImage = "" }
        continue
    }

    $cred = Get-WorkingCredential -ComputerName $h -Candidates $UserCandidates -Password $pass
    if ($null -eq $cred) {
        $results += [pscustomobject]@{ Host = $h; Status = "AUTH_FAIL"; User = ""; Detail = "Sin credencial valida"; RemoteImage = "" }
        continue
    }

    $session = $null
    try {
        $session = New-PSSession -ComputerName $h -Credential $cred -ErrorAction Stop
        Invoke-Command -Session $session -ScriptBlock $remotePrepare -ArgumentList $RemoteImagePath -ErrorAction Stop | Out-Null
        Copy-Item -Path $SourceImagePath -Destination $RemoteImagePath -ToSession $session -Force -ErrorAction Stop
        $r = Invoke-Command -Session $session -ScriptBlock $remoteApply -ArgumentList $RemoteImagePath -ErrorAction Stop
        $results += [pscustomobject]@{
            Host = $h
            Status = "OK"
            User = $cred.UserName
            Detail = $r.UpdatedProfiles
            RemoteImage = $r.RemoteImagePath
        }
    } catch {
        $results += [pscustomobject]@{
            Host = $h
            Status = "FAIL"
            User = if ($cred) { $cred.UserName } else { "" }
            Detail = $_.Exception.Message
            RemoteImage = ""
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
$csv = Join-Path $dayDir ("winrm_wallpaper_apply_" + $ts + ".csv")

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
