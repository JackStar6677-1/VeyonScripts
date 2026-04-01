param(
    [string]$RootPath = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RootPath)) {
    $scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
    $RootPath = $scriptRoot
}

$RootPath = (Resolve-Path $RootPath).Path
$DriveRoot = [System.IO.Path]::GetPathRoot($RootPath)

$Paths = [ordered]@{
    OperativoRoot = $RootPath
    Preparar      = Join-Path $RootPath "PREPARAR"
    Masivo        = Join-Path $RootPath "MASIVO"
    Utilidades    = Join-Path $RootPath "UTILIDADES"
    Veyon         = Join-Path $RootPath "VEYON"
    Herramientas  = Join-Path $DriveRoot "HERRAMIENTAS"
    Drivers       = Join-Path $DriveRoot "DRIVERS"
    Isos          = Join-Path $DriveRoot "ISOS"
    Scripts       = Join-Path $DriveRoot "SCRIPTS"
    Optimizador2  = Join-Path (Join-Path $DriveRoot "HERRAMIENTAS\UTILIDADES") "Optimizador2.txt"
    RepoReports   = "C:\Users\Jack\Documents\GitHub\VeyonScripts\reports"
}

function Test-IsAdmin {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Pause-Continue {
    Write-Host ""
    Read-Host "Presiona Enter para continuar"
}

function Confirm-Action {
    param(
        [string]$Title,
        [string]$Description = ""
    )

    Write-Host ""
    Write-Host ("Accion: {0}" -f $Title) -ForegroundColor Yellow
    if ($Description) {
        Write-Host $Description -ForegroundColor DarkYellow
    }
    $answer = Read-Host "Confirmar? (S/N)"
    return $answer -match '^[SsYy]'
}

function Show-Header {
    Clear-Host
    Write-Host "############################################################" -ForegroundColor DarkMagenta
    Write-Host "#                                                          #" -ForegroundColor DarkMagenta
    Write-Host "#  CASTEL PENDRIVE MENU                                    #" -ForegroundColor Yellow
    Write-Host "#  Centro rapido de soporte, scripts y utilidades          #" -ForegroundColor Magenta
    Write-Host "#                                                          #" -ForegroundColor DarkMagenta
    Write-Host "############################################################" -ForegroundColor DarkMagenta
    Write-Host ""
    Write-Host ("Pendrive : {0}" -f $DriveRoot) -ForegroundColor Yellow
    Write-Host ("Operativo: {0}" -f $RootPath) -ForegroundColor Gray
    Write-Host ("Admin    : {0}" -f (if (Test-IsAdmin) { "SI" } else { "NO" })) -ForegroundColor (if (Test-IsAdmin) { "Green" } else { "DarkYellow" })
    Write-Host ""
}

function Open-In-Explorer {
    param([string]$Path)
    if (Test-Path $Path) {
        Start-Process explorer.exe $Path | Out-Null
    } else {
        Write-Host ("No existe: {0}" -f $Path) -ForegroundColor Yellow
    }
}

function Open-TerminalHere {
    param([string]$Path)
    if (Test-Path $Path) {
        Start-Process powershell.exe -ArgumentList @("-NoExit", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ("Set-Location -LiteralPath '{0}'" -f $Path.Replace("'","''"))) | Out-Null
    } else {
        Write-Host ("No existe: {0}" -f $Path) -ForegroundColor Yellow
    }
}

function Open-In-Notepad {
    param([string]$Path)
    if (Test-Path $Path) {
        Start-Process notepad.exe $Path | Out-Null
    } else {
        Write-Host ("No existe: {0}" -f $Path) -ForegroundColor Yellow
    }
}

function Invoke-CommandLineExternal {
    param(
        [string]$CommandLine,
        [switch]$RequireAdmin
    )

    if ([string]::IsNullOrWhiteSpace($CommandLine)) {
        Write-Host "Linea vacia." -ForegroundColor Yellow
        return
    }

    $args = @(
        "-NoExit",
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-Command", $CommandLine
    )

    if ($RequireAdmin -and -not (Test-IsAdmin)) {
        Start-Process powershell.exe -Verb RunAs -ArgumentList $args | Out-Null
    } else {
        Start-Process powershell.exe -ArgumentList $args | Out-Null
    }
}

function Invoke-ScriptFile {
    param(
        [string]$Path,
        [switch]$RequireAdmin
    )

    if (-not (Test-Path $Path)) {
        Write-Host ("No existe: {0}" -f $Path) -ForegroundColor Yellow
        return
    }

    $ext = [IO.Path]::GetExtension($Path).ToLowerInvariant()

    if ($RequireAdmin -and -not (Test-IsAdmin)) {
        switch ($ext) {
            ".ps1" {
                Start-Process powershell.exe -Verb RunAs -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $Path) | Out-Null
            }
            ".bat" { Start-Process $Path -Verb RunAs | Out-Null }
            ".cmd" { Start-Process $Path -Verb RunAs | Out-Null }
            ".exe" { Start-Process $Path -Verb RunAs | Out-Null }
            default {
                Write-Host "No se pudo elevar automaticamente este tipo de archivo." -ForegroundColor Yellow
            }
        }
        return
    }

    switch ($ext) {
        ".ps1" {
            & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Path
        }
        ".bat" {
            & cmd.exe /c $Path
        }
        ".cmd" {
            & cmd.exe /c $Path
        }
        ".exe" {
            Start-Process $Path | Out-Null
        }
        default {
            Invoke-Item $Path
        }
    }
}

function Get-ManagedItems {
    $items = New-Object System.Collections.Generic.List[object]

    Get-ChildItem -Path $DriveRoot -Recurse -Force -ErrorAction SilentlyContinue |
        Where-Object {
            $_.PSIsContainer -or
            $_.Extension -in @(".ps1", ".bat", ".cmd", ".exe", ".txt", ".md", ".lnk", ".url", ".csv", ".html")
        } |
        Where-Object { $_.FullName -notlike "*System Volume Information*" -and $_.FullName -notlike "*`$RECYCLE.BIN*" } |
        Sort-Object FullName |
        ForEach-Object {
            $type = if ($_.PSIsContainer) { "Folder" } else { $_.Extension.TrimStart(".").ToUpperInvariant() }
            $items.Add([pscustomobject]@{
                FullName = $_.FullName
                Name     = $_.Name
                Type     = $type
            })
        }

    return $items
}

function Browse-Pendrive {
    while ($true) {
        Show-Header
        Write-Host "Explorador del pendrive" -ForegroundColor Green
        Write-Host ""

        $items = Get-ManagedItems
        if ($items.Count -eq 0) {
            Write-Host "No se encontraron elementos manejables." -ForegroundColor Yellow
            Pause-Continue
            return
        }

        $limit = [Math]::Min(40, $items.Count)
        for ($i = 0; $i -lt $limit; $i++) {
            $item = $items[$i]
            $relative = $item.FullName.Replace($DriveRoot, "").TrimStart("\")
            Write-Host ("{0}. [{1}] {2}" -f ($i + 1), $item.Type, $relative)
        }

        if ($items.Count -gt $limit) {
            Write-Host ("... mostrando los primeros {0} de {1}" -f $limit, $items.Count) -ForegroundColor DarkGray
        }

        Write-Host ""
        Write-Host "B. Volver"
        $choice = Read-Host "Elige un numero para abrir/ejecutar"
        if ($choice -match "^[Bb]$") { return }
        if ($choice -notmatch "^\d+$") { continue }

        $index = [int]$choice - 1
        if ($index -lt 0 -or $index -ge $limit) { continue }

        $selected = $items[$index]
        if (Test-Path $selected.FullName -PathType Container) {
            Open-In-Explorer -Path $selected.FullName
            continue
        }

        $ext = [IO.Path]::GetExtension($selected.FullName).ToLowerInvariant()
        if ($ext -in @(".txt", ".md", ".csv", ".html")) {
            Open-In-Notepad -Path $selected.FullName
            continue
        }

        $answer = Read-Host "Ejecutar como administrador? (S/N)"
        $requireAdmin = $answer -match "^[SsYy]"
        Invoke-ScriptFile -Path $selected.FullName -RequireAdmin:$requireAdmin
        Pause-Continue
    }
}

function Show-PendriveInfo {
    Show-Header
    $vol = Get-Volume -DriveLetter $DriveRoot.Substring(0,1)
    Write-Host "Info del pendrive" -ForegroundColor Green
    Write-Host ""
    Write-Host ("Etiqueta    : {0}" -f $vol.FileSystemLabel)
    Write-Host ("Sistema     : {0}" -f $vol.FileSystem)
    Write-Host ("Libre       : {0:N2} GB" -f ($vol.SizeRemaining / 1GB))
    Write-Host ("Usado       : {0:N2} GB" -f (($vol.Size - $vol.SizeRemaining) / 1GB))
    Write-Host ("Tamano total: {0:N2} GB" -f ($vol.Size / 1GB))
    Write-Host ""
    Pause-Continue
}

function Show-Option {
    param(
        [string]$Number,
        [string]$Title,
        [string]$Description,
        [ConsoleColor]$Color = [ConsoleColor]::White
    )

    Write-Host ("[{0}] {1}" -f $Number, $Title) -ForegroundColor $Color
    Write-Host ("      {0}" -f $Description) -ForegroundColor Gray
}

function Show-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host ("==== {0} ====" -f $Title.ToUpperInvariant()) -ForegroundColor DarkMagenta
}

function Show-HostsInfo {
    $file = Join-Path $Paths.Masivo "hosts_castel.txt"
    Show-Header
    Write-Host "Hosts de la sala" -ForegroundColor Green
    Write-Host ""
    if (-not (Test-Path $file)) {
        Write-Host ("No existe: {0}" -f $file) -ForegroundColor Yellow
        Pause-Continue
        return
    }

    $hosts = Get-Content $file | ForEach-Object { $_.Trim() } | Where-Object { $_ -and -not $_.StartsWith("#") }
    Write-Host ("Total de hosts: {0}" -f $hosts.Count)
    Write-Host ""
    $hosts | Select-Object -First 20 | ForEach-Object { Write-Host $_ }
    if ($hosts.Count -gt 20) {
        Write-Host ("... y {0} mas" -f ($hosts.Count - 20)) -ForegroundColor DarkGray
    }
    Pause-Continue
}

function Show-RecentReports {
    Show-Header
    Write-Host "Logs y reportes" -ForegroundColor Green
    Write-Host ""
    if (-not (Test-Path $Paths.RepoReports)) {
        Write-Host ("No existe carpeta de reportes: {0}" -f $Paths.RepoReports) -ForegroundColor Yellow
        Pause-Continue
        return
    }

    $files = Get-ChildItem -Path $Paths.RepoReports -Recurse -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 20

    if (-not $files) {
        Write-Host "No se encontraron reportes." -ForegroundColor Yellow
        Pause-Continue
        return
    }

    for ($i = 0; $i -lt $files.Count; $i++) {
        $f = $files[$i]
        $relative = $f.FullName.Replace($Paths.RepoReports, "").TrimStart("\")
        Write-Host ("{0}. {1} [{2}]" -f ($i + 1), $relative, $f.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss"))
    }

    Write-Host ""
    Write-Host "A. Abrir carpeta reportes"
    Write-Host "B. Volver"
    $choice = Read-Host "Elige un numero para abrir"

    if ($choice -match '^[Aa]$') {
        Open-In-Explorer -Path $Paths.RepoReports
        return
    }
    if ($choice -match '^[Bb]$') {
        return
    }
    if ($choice -notmatch '^\d+$') {
        return
    }

    $index = [int]$choice - 1
    if ($index -ge 0 -and $index -lt $files.Count) {
        Open-In-Notepad -Path $files[$index].FullName
    }
}

function Validate-PendriveScripts {
    Show-Header
    Write-Host "Validacion de scripts" -ForegroundColor Green
    Write-Host ""

    $files = Get-ChildItem -Path $DriveRoot -Recurse -File -Force -ErrorAction SilentlyContinue |
        Where-Object {
            $_.Extension -in @(".ps1", ".bat", ".cmd") -and
            $_.FullName -notlike "*System Volume Information*" -and
            $_.FullName -notlike "*`$RECYCLE.BIN*"
        } |
        Sort-Object FullName

    if (-not $files) {
        Write-Host "No se encontraron scripts." -ForegroundColor Yellow
        Pause-Continue
        return
    }

    foreach ($file in $files) {
        $relative = $file.FullName.Replace($DriveRoot, "").TrimStart("\")
        if ($file.Extension -eq ".ps1") {
            $tokens = $null
            $errors = $null
            [void][System.Management.Automation.Language.Parser]::ParseFile($file.FullName, [ref]$tokens, [ref]$errors)
            if ($errors) {
                Write-Host ("FAIL  {0}" -f $relative) -ForegroundColor Red
            } else {
                Write-Host ("OK    {0}" -f $relative) -ForegroundColor Green
            }
        } else {
            Write-Host ("CHECK {0}" -f $relative) -ForegroundColor Cyan
        }
    }

    Pause-Continue
}

function Show-PayloadManager {
    while ($true) {
        $payload = Join-Path $Paths.Masivo "payload.ps1"
        Show-Header
        Write-Host "Payload manager" -ForegroundColor Green
        Write-Host ("Payload: {0}" -f $payload)
        Write-Host ""
        Write-Host "1. Abrir payload.ps1"
        Write-Host "2. Validar payload.ps1"
        Write-Host "3. Abrir carpeta MASIVO"
        Write-Host "4. Ver hosts de la sala"
        Write-Host "B. Volver"

        $choice = Read-Host "Selecciona una opcion"
        switch ($choice) {
            "1" { Open-In-Notepad -Path $payload }
            "2" {
                if (-not (Test-Path $payload)) {
                    Write-Host "No existe payload.ps1" -ForegroundColor Yellow
                } else {
                    $tokens = $null
                    $errors = $null
                    [void][System.Management.Automation.Language.Parser]::ParseFile($payload, [ref]$tokens, [ref]$errors)
                    if ($errors) {
                        Write-Host "Payload con errores de parse." -ForegroundColor Red
                        $errors | ForEach-Object { Write-Host $_.Message -ForegroundColor Red }
                    } else {
                        Write-Host "Payload parsea correctamente." -ForegroundColor Green
                    }
                }
                Pause-Continue
            }
            "3" { Open-In-Explorer -Path $Paths.Masivo }
            "4" { Show-HostsInfo }
            { $_ -match '^[Bb]$' } { return }
            default { }
        }
    }
}

function Run-Optimizador2Menu {
    $file = $Paths.Optimizador2
    if (-not (Test-Path $file)) {
        Write-Host ("No existe: {0}" -f $file) -ForegroundColor Yellow
        Pause-Continue
        return
    }

    while ($true) {
        Show-Header
        Write-Host "Optimizador2" -ForegroundColor Green
        Write-Host ("Archivo: {0}" -f $file)
        Write-Host ""

        $lines = Get-Content -Path $file | ForEach-Object { $_.Trim() } | Where-Object {
            $_ -and $_ -notmatch '^(---+|Specify|LimitBreaker|MarketPlaceBedrock|windowsbreaker|reporte de bater)'
        }

        if ($lines.Count -eq 0) {
            Write-Host "No hay lineas ejecutables detectadas." -ForegroundColor Yellow
            Pause-Continue
            return
        }

        for ($i = 0; $i -lt $lines.Count; $i++) {
            Write-Host ("{0}. {1}" -f ($i + 1), $lines[$i])
        }

        Write-Host ""
        Write-Host "A. Abrir txt en Notepad"
        Write-Host "B. Volver"
        $choice = Read-Host "Elige una linea para ejecutar en otra terminal"

        if ($choice -match '^[Aa]$') {
            Open-In-Notepad -Path $file
            continue
        }

        if ($choice -match '^[Bb]$') {
            return
        }

        if ($choice -notmatch '^\d+$') {
            continue
        }

        $index = [int]$choice - 1
        if ($index -lt 0 -or $index -ge $lines.Count) {
            continue
        }

        $command = $lines[$index]
        Write-Host ""
        Write-Host ("Comando: {0}" -f $command) -ForegroundColor Cyan
        $adminAnswer = Read-Host "Abrir en terminal admin? (S/N)"
        $asAdmin = $adminAnswer -match '^[SsYy]'
        Invoke-CommandLineExternal -CommandLine $command -RequireAdmin:$asAdmin
        Pause-Continue
    }
}

while ($true) {
    Show-Header
    Show-Section -Title "Navegacion"
    Show-Option -Number "1" -Title "Abrir carpeta HERRAMIENTAS" -Description "Abre la carpeta principal de herramientas tecnicas del pendrive." -Color Yellow
    Show-Option -Number "2" -Title "Abrir carpeta SCRIPTS" -Description "Abre la carpeta de scripts para revisar o lanzar cosas manualmente." -Color Yellow
    Show-Option -Number "16" -Title "Abrir terminal en el pendrive" -Description "Abre otra PowerShell ya posicionada en el pendrive." -Color Yellow

    Show-Section -Title "Acciones Admin"
    Show-Option -Number "3" -Title "Preparar PC para gestion remota (admin)" -Description "Habilita WinRM, firewall y ajustes base para poder administrar ese PC remotamente." -Color Magenta
    Show-Option -Number "4" -Title "Ejecutar masivo WinRM (admin)" -Description "Lanza un payload en varios PCs usando una credencial admin comun." -Color Magenta
    Show-Option -Number "5" -Title "Ejecutar masivo auto-cred (admin)" -Description "Prueba varios nombres de usuario locales con una misma clave para ejecutar en masa." -Color Magenta
    Show-Option -Number "6" -Title "Reset total de Chrome local (admin)" -Description "Cierra Chrome y borra perfiles, cache y datos locales para dejarlo limpio." -Color Magenta
    Show-Option -Number "7" -Title "Reset GPO local (admin)" -Description "Restablece o limpia politicas locales de Windows para corregir bloqueos o herencias." -Color Magenta
    Show-Option -Number "8" -Title "Restablecer politicas Office/organizacion (admin)" -Description "Limpia restricciones de Office y politicas de organizacion que puedan molestar." -Color Magenta
    Show-Option -Number "9" -Title "Restaurar Veyon sala (admin)" -Description "Restaura claves y configuracion base del maestro Veyon de la sala." -Color Magenta

    Show-Section -Title "Edicion Y Apoyo"
    Show-Option -Number "10" -Title "Menu de comandos Optimizador2" -Description "Muestra lineas utiles guardadas en Optimizador2.txt y las ejecuta en otra terminal." -Color Yellow
    Show-Option -Number "11" -Title "Editar Optimizador2.txt" -Description "Abre el txt donde guardas comandos utiles de PowerShell o CMD." -Color Yellow
    Show-Option -Number "12" -Title "Payload manager" -Description "Abrir, validar y revisar payload.ps1 y hosts_castel.txt." -Color Yellow
    Show-Option -Number "13" -Title "Editar hosts_castel.txt" -Description "Abre la lista de IPs o equipos destino para los scripts masivos." -Color Yellow

    Show-Section -Title "Diagnostico"
    Show-Option -Number "14" -Title "Explorar y abrir/ejecutar archivos del pendrive" -Description "Recorre archivos del USB y permite abrirlos o ejecutarlos desde el menu." -Color Cyan
    Show-Option -Number "15" -Title "Ver informacion del pendrive" -Description "Muestra datos basicos del USB como etiqueta, sistema de archivos y espacio." -Color Cyan
    Show-Option -Number "17" -Title "Ver logs y reportes" -Description "Abre o muestra los reportes recientes del repo local." -Color Cyan
    Show-Option -Number "18" -Title "Validar scripts del pendrive" -Description "Revisa el parse de los .ps1 y enumera scripts del kit." -Color Cyan

    Show-Section -Title "Salir"
    Show-Option -Number "0" -Title "Salir" -Description "Cierra el menu." -Color DarkGray
    Write-Host ""

    $option = Read-Host "Selecciona una opcion"

    switch ($option) {
        "1"  { Open-In-Explorer -Path $Paths.Herramientas }
        "2"  { Open-In-Explorer -Path $Paths.Scripts }
        "3"  { if (Confirm-Action -Title "Preparar PC remoto" -Description "Va a tocar WinRM, firewall y configuracion local.") { Invoke-ScriptFile -Path (Join-Path $Paths.Preparar "PREPARAR_REMOTO_WIN10.bat") -RequireAdmin }; Pause-Continue }
        "4"  { if (Confirm-Action -Title "Ejecutar masivo WinRM" -Description "Va a correr el payload actual sobre los hosts configurados.") { Invoke-ScriptFile -Path (Join-Path $Paths.Masivo "EJECUTAR_MASIVO_WINRM.bat") -RequireAdmin }; Pause-Continue }
        "5"  { if (Confirm-Action -Title "Ejecutar masivo auto-cred" -Description "Va a probar varios usuarios locales sobre los hosts configurados.") { Invoke-ScriptFile -Path (Join-Path $Paths.Masivo "EJECUTAR_MASIVO_AUTO_CRED.bat") -RequireAdmin }; Pause-Continue }
        "6"  { if (Confirm-Action -Title "Reset total de Chrome" -Description "Borra perfiles, cache y datos locales de Chrome.") { Invoke-ScriptFile -Path (Join-Path $Paths.Utilidades "RESET_CHROME_TOTAL_PORTABLE.bat") -RequireAdmin }; Pause-Continue }
        "7"  { if (Confirm-Action -Title "Reset GPO local" -Description "Puede revertir politicas locales del equipo actual.") { Invoke-ScriptFile -Path (Join-Path $Paths.Utilidades "reset-gpo.ps1") -RequireAdmin }; Pause-Continue }
        "8"  { if (Confirm-Action -Title "Restablecer politicas Office/organizacion" -Description "Puede quitar restricciones de Office y organizacion.") { Invoke-ScriptFile -Path (Join-Path $Paths.Utilidades "Restablecer_politicas_Office_y_organizacion.bat") -RequireAdmin }; Pause-Continue }
        "9"  { if (Confirm-Action -Title "Restaurar Veyon sala" -Description "Va a restaurar claves y configuracion del maestro Veyon.") { Invoke-ScriptFile -Path (Join-Path $Paths.Veyon "RESTAURAR_VEYON_SALA.bat") -RequireAdmin }; Pause-Continue }
        "10" { Run-Optimizador2Menu }
        "11" { Open-In-Notepad -Path $Paths.Optimizador2 }
        "12" { Show-PayloadManager }
        "13" { Open-In-Notepad -Path (Join-Path $Paths.Masivo "hosts_castel.txt") }
        "14" { Browse-Pendrive }
        "15" { Show-PendriveInfo }
        "16" { Open-TerminalHere -Path $DriveRoot }
        "17" { Show-RecentReports }
        "18" { Validate-PendriveScripts }
        "0"  { break }
        default { }
    }
}
