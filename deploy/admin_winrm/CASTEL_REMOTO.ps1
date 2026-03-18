param(
    [ValidateSet(
        "status",
        "wol",
        "remove-auto-shutdown",
        "install-admin-bridge",
        "install-gui-agent",
        "reset-chrome",
        "protect-materials",
        "create-entrega",
        "gui-launch",
        "gui-keys",
        "admin-inline",
        "admin-cmd",
        "admin-file"
    )]
    [string]$Action = "status",
    [string]$HostsFile = ".\hosts_castel.txt",
    [string[]]$UserCandidates = @("Colegio", "colegio", "Admin", "Administrador", "Usuario", "Alumno", "Estudiante", "Profesor"),
    [string]$PasswordPlain = "administrativa",
    [switch]$WhatIfMode,
    [string]$Path = "",
    [string]$Arguments = "",
    [string]$WindowTitle = "",
    [string]$Keys = "",
    [string]$Code = "",
    [string]$Command = "",
    [switch]$DisableChromeSignin,
    [switch]$IncludeEdge
)

$ErrorActionPreference = "Stop"
$kitRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

function Resolve-KitPath {
    param([string]$Name)
    return Join-Path $kitRoot $Name
}

function Resolve-InputPath {
    param([string]$InputPath)

    if ([string]::IsNullOrWhiteSpace($InputPath)) {
        return $InputPath
    }

    if ([System.IO.Path]::IsPathRooted($InputPath)) {
        return $InputPath
    }

    return Join-Path $kitRoot $InputPath
}

function Require-File {
    param([string]$FilePath)
    if (-not (Test-Path $FilePath)) {
        throw "No existe archivo requerido: $FilePath"
    }
}

function Invoke-KitScript {
    param(
        [string]$ScriptPath,
        [string[]]$ScriptArguments = @()
    )

    Require-File -FilePath $ScriptPath

    if ($WhatIfMode) {
        Write-Host "[WHATIF] powershell -File `"$ScriptPath`" $($ScriptArguments -join ' ')" -ForegroundColor Yellow
        return
    }

    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ScriptPath @ScriptArguments
    if ($LASTEXITCODE -ne 0) {
        throw "Fallo ejecutando $ScriptPath"
    }
}

function Get-Hosts {
    param([string]$FilePath)
    $resolved = Resolve-InputPath -InputPath $FilePath
    Require-File -FilePath $resolved
    return Get-Content $resolved |
        ForEach-Object { $_.Trim() } |
        Where-Object { $_ -and -not $_.StartsWith("#") } |
        Select-Object -Unique
}

function Get-StatusReport {
    param(
        [string]$FilePath,
        [string[]]$Candidates,
        [string]$PlainPassword
    )

    $hosts = Get-Hosts -FilePath $FilePath
    $password = ConvertTo-SecureString $PlainPassword -AsPlainText -Force
    $results = @()

    function Get-WorkingCredential {
        param(
            [string]$ComputerName,
            [string[]]$LocalCandidates,
            [securestring]$SecurePassword
        )

        $variants = @()
        foreach ($u in $LocalCandidates) {
            $variants += "$ComputerName\$u"
            $variants += ".\$u"
            $variants += $u
        }
        $variants = $variants | Select-Object -Unique

        foreach ($name in $variants) {
            try {
                $cred = New-Object System.Management.Automation.PSCredential($name, $SecurePassword)
                Invoke-Command -ComputerName $ComputerName -Credential $cred -ScriptBlock { "OK" } -ErrorAction Stop | Out-Null
                return $cred
            } catch {
                continue
            }
        }

        return $null
    }

    $remoteCheck = {
        $activeUser = ""
        try {
            $line = (quser 2>$null | Select-String "Active" | Select-Object -First 1).ToString()
            if ($line) {
                $activeUser = (($line -split "\s+")[1]).Trim()
            }
        } catch {}

        $taskNames = @()
        try {
            $taskNames = Get-ScheduledTask -TaskName "Castel-AdminBridge" -ErrorAction SilentlyContinue | ForEach-Object { $_.TaskName }
        } catch {}

        [pscustomobject]@{
            Computer = $env:COMPUTERNAME
            ActiveUser = $activeUser
            AdminBridgeInstalled = [bool]($taskNames -contains "Castel-AdminBridge")
            GuiAgentInstalled = Test-Path "C:\ProgramData\CastelRemote\GUI_AGENTE_INTERACTIVO.ps1"
            ChromeResetAvailable = Test-Path "C:\ProgramData\CastelRemote\RESET_CHROME_COMPARTIDO.ps1"
            EntregaScriptAvailable = Test-Path "C:\ProgramData\CastelRemote\CREAR_CARPETA_ENTREGA_SALA.ps1"
        }
    }

    foreach ($targetHost in $hosts) {
        $portOpen = Test-NetConnection -ComputerName $targetHost -Port 5985 -InformationLevel Quiet -WarningAction SilentlyContinue
        if (-not $portOpen) {
            $results += [pscustomobject]@{
                Host = $targetHost
                Status = "NO_5985"
                ActiveUser = ""
                AdminBridgeInstalled = $false
                GuiAgentInstalled = $false
                ChromeResetAvailable = $false
                EntregaScriptAvailable = $false
            }
            continue
        }

        $cred = Get-WorkingCredential -ComputerName $targetHost -LocalCandidates $Candidates -SecurePassword $password
        if ($null -eq $cred) {
            $results += [pscustomobject]@{
                Host = $targetHost
                Status = "AUTH_FAIL"
                ActiveUser = ""
                AdminBridgeInstalled = $false
                GuiAgentInstalled = $false
                ChromeResetAvailable = $false
                EntregaScriptAvailable = $false
            }
            continue
        }

        try {
            $r = Invoke-Command -ComputerName $targetHost -Credential $cred -ScriptBlock $remoteCheck -ErrorAction Stop
            $results += [pscustomobject]@{
                Host = $targetHost
                Status = "OK"
                ActiveUser = $r.ActiveUser
                AdminBridgeInstalled = $r.AdminBridgeInstalled
                GuiAgentInstalled = $r.GuiAgentInstalled
                ChromeResetAvailable = $r.ChromeResetAvailable
                EntregaScriptAvailable = $r.EntregaScriptAvailable
            }
        } catch {
            $results += [pscustomobject]@{
                Host = $targetHost
                Status = "FAIL"
                ActiveUser = ""
                AdminBridgeInstalled = $false
                GuiAgentInstalled = $false
                ChromeResetAvailable = $false
                EntregaScriptAvailable = $false
            }
        }
    }

    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $report = Join-Path $kitRoot ("castel_status_" + $stamp + ".csv")
    $results | Export-Csv -Path $report -NoTypeInformation -Encoding UTF8

    Write-Host "REPORTE: $report" -ForegroundColor Cyan
    $results | Group-Object Status | Sort-Object Name | ForEach-Object {
        Write-Host ("{0}: {1}" -f $_.Name, $_.Count)
    }
}

switch ($Action) {
    "status" {
        Get-StatusReport -FilePath (Resolve-InputPath -InputPath $HostsFile) -Candidates $UserCandidates -PlainPassword $PasswordPlain
    }
    "wol" {
        Invoke-KitScript -ScriptPath (Resolve-KitPath "ENVIAR_WOL_CASTEL.ps1") -ScriptArguments @("-ReservasCsvPath", (Join-Path (Split-Path $kitRoot -Parent | Split-Path -Parent) "data\reservas_dhcp_castel.csv"))
    }
    "remove-auto-shutdown" {
        Invoke-KitScript -ScriptPath (Resolve-KitPath "REMOVE_APAGADO_AUTOMATICO_WINRM.ps1") -ScriptArguments @("-HostsFile", (Resolve-InputPath -InputPath $HostsFile), "-PasswordPlain", $PasswordPlain)
    }
    "install-admin-bridge" {
        Invoke-KitScript -ScriptPath (Resolve-KitPath "INSTALAR_ELEVACION_WINRM.ps1") -ScriptArguments @("-HostsFile", (Resolve-InputPath -InputPath $HostsFile), "-PasswordPlain", $PasswordPlain)
    }
    "install-gui-agent" {
        Invoke-KitScript -ScriptPath (Resolve-KitPath "INSTALAR_GUI_AGENTE_WINRM.ps1") -ScriptArguments @("-HostsFile", (Resolve-InputPath -InputPath $HostsFile), "-PasswordPlain", $PasswordPlain)
    }
    "reset-chrome" {
        $args = @("-Action", "powershell_file", "-HostsFile", (Resolve-InputPath -InputPath $HostsFile), "-PasswordPlain", $PasswordPlain, "-Path", "C:\ProgramData\CastelRemote\RESET_CHROME_COMPARTIDO.ps1")
        if ($DisableChromeSignin -and $IncludeEdge) {
            $args += @("-Arguments", '"-DisableChromeSignin -IncludeEdge"')
        } elseif ($DisableChromeSignin) {
            $args += @("-Arguments", '"-DisableChromeSignin"')
        } elseif ($IncludeEdge) {
            $args += @("-Arguments", '"-IncludeEdge"')
        }
        Invoke-KitScript -ScriptPath (Resolve-KitPath "ENVIAR_ADMIN_COMANDO_WINRM.ps1") -ScriptArguments $args
    }
    "protect-materials" {
        Invoke-KitScript -ScriptPath (Resolve-KitPath "ENVIAR_ADMIN_COMANDO_WINRM.ps1") -ScriptArguments @("-Action", "powershell_file", "-HostsFile", (Resolve-InputPath -InputPath $HostsFile), "-PasswordPlain", $PasswordPlain, "-Path", "C:\ProgramData\CastelRemote\PROTEGER_MATERIALES_SALA.ps1")
    }
    "create-entrega" {
        Invoke-KitScript -ScriptPath (Resolve-KitPath "ENVIAR_ADMIN_COMANDO_WINRM.ps1") -ScriptArguments @("-Action", "powershell_file", "-HostsFile", (Resolve-InputPath -InputPath $HostsFile), "-PasswordPlain", $PasswordPlain, "-Path", "C:\ProgramData\CastelRemote\CREAR_CARPETA_ENTREGA_SALA.ps1")
    }
    "gui-launch" {
        if ([string]::IsNullOrWhiteSpace($Path)) { throw "gui-launch requiere -Path" }
        $guiArgs = @("-Action", "launch", "-HostsFile", (Resolve-InputPath -InputPath $HostsFile), "-PasswordPlain", $PasswordPlain, "-Path", $Path)
        if (-not [string]::IsNullOrWhiteSpace($Arguments)) { $guiArgs += @("-Arguments", $Arguments) }
        Invoke-KitScript -ScriptPath (Resolve-KitPath "ENVIAR_GUI_COMANDO_WINRM.ps1") -ScriptArguments $guiArgs
    }
    "gui-keys" {
        if ([string]::IsNullOrWhiteSpace($WindowTitle) -or [string]::IsNullOrWhiteSpace($Keys)) { throw "gui-keys requiere -WindowTitle y -Keys" }
        Invoke-KitScript -ScriptPath (Resolve-KitPath "ENVIAR_GUI_COMANDO_WINRM.ps1") -ScriptArguments @("-Action", "keys", "-HostsFile", (Resolve-InputPath -InputPath $HostsFile), "-PasswordPlain", $PasswordPlain, "-WindowTitle", $WindowTitle, "-Keys", $Keys)
    }
    "admin-inline" {
        if ([string]::IsNullOrWhiteSpace($Code)) { throw "admin-inline requiere -Code" }
        Invoke-KitScript -ScriptPath (Resolve-KitPath "ENVIAR_ADMIN_COMANDO_WINRM.ps1") -ScriptArguments @("-Action", "powershell_inline", "-HostsFile", (Resolve-InputPath -InputPath $HostsFile), "-PasswordPlain", $PasswordPlain, "-Code", $Code)
    }
    "admin-cmd" {
        if ([string]::IsNullOrWhiteSpace($Command)) { throw "admin-cmd requiere -Command" }
        Invoke-KitScript -ScriptPath (Resolve-KitPath "ENVIAR_ADMIN_COMANDO_WINRM.ps1") -ScriptArguments @("-Action", "cmd", "-HostsFile", (Resolve-InputPath -InputPath $HostsFile), "-PasswordPlain", $PasswordPlain, "-Command", $Command)
    }
    "admin-file" {
        if ([string]::IsNullOrWhiteSpace($Path)) { throw "admin-file requiere -Path" }
        $adminArgs = @("-Action", "powershell_file", "-HostsFile", (Resolve-InputPath -InputPath $HostsFile), "-PasswordPlain", $PasswordPlain, "-Path", $Path)
        if (-not [string]::IsNullOrWhiteSpace($Arguments)) { $adminArgs += @("-Arguments", $Arguments) }
        Invoke-KitScript -ScriptPath (Resolve-KitPath "ENVIAR_ADMIN_COMANDO_WINRM.ps1") -ScriptArguments $adminArgs
    }
}
