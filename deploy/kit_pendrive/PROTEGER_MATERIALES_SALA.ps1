param(
    [string[]]$TargetPaths = @(
        "C:\MaterialesSala",
        "C:\Users\Public\Desktop\Materiales",
        "C:\Users\Public\Documents\Materiales"
    ),
    [string]$UsersGroup = "Users",
    [switch]$CreateMissingFolders,
    [switch]$ProtectOnlyExisting
)

$ErrorActionPreference = "Continue"
$logFile = "C:\Windows\Temp\proteger_materiales_sala.log"

function Write-Log {
    param([string]$Message)
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message
    Add-Content -Path $logFile -Value $line
}

function Ensure-Folder {
    param([string]$Path)

    if (Test-Path $Path) {
        return $true
    }

    if ($CreateMissingFolders) {
        try {
            New-Item -Path $Path -ItemType Directory -Force | Out-Null
            Write-Log ("Carpeta creada: {0}" -f $Path)
            return $true
        } catch {
            Write-Log ("No se pudo crear carpeta {0}: {1}" -f $Path, $_.Exception.Message)
            return $false
        }
    }

    return $false
}

function Protect-FolderContent {
    param(
        [string]$Path,
        [string]$GroupName
    )

    $resolved = Resolve-Path -Path $Path -ErrorAction Stop
    $folderPath = $resolved.Path

    $acl = Get-Acl -Path $folderPath
    $inheritanceEnabled = $true
    $preserveInheritedRules = $true
    $acl.SetAccessRuleProtection(-not $inheritanceEnabled, $preserveInheritedRules)

    foreach ($rule in @($acl.Access)) {
        if ($rule.IdentityReference -like "*\$GroupName" -or $rule.IdentityReference.Value -eq $GroupName) {
            if ($rule.FileSystemRights.ToString() -match "Modify|FullControl|Delete|Write") {
                $acl.RemoveAccessRule($rule) | Out-Null
            }
        }
    }

    $allowRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
        $GroupName,
        "ReadAndExecute, Synchronize",
        "ContainerInherit,ObjectInherit",
        "None",
        "Allow"
    )
    $denyRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
        $GroupName,
        "Delete, DeleteSubdirectoriesAndFiles",
        "ContainerInherit,ObjectInherit",
        "None",
        "Deny"
    )

    $acl.SetAccessRule($allowRule)
    $acl.AddAccessRule($denyRule) | Out-Null
    Set-Acl -Path $folderPath -AclObject $acl

    attrib +R "$folderPath\*" /S /D | Out-Null

    Write-Log ("Protegido: {0}" -f $folderPath)
}

Write-Log "=== PROTEGER_MATERIALES_SALA START ==="
Write-Log ("Host={0} UsersGroup={1}" -f $env:COMPUTERNAME, $UsersGroup)

$done = New-Object System.Collections.Generic.List[string]
$skipped = New-Object System.Collections.Generic.List[string]
$failed = New-Object System.Collections.Generic.List[string]

foreach ($path in $TargetPaths) {
    try {
        $exists = Ensure-Folder -Path $path
        if (-not $exists) {
            if ($ProtectOnlyExisting) {
                $skipped.Add($path)
                Write-Log ("Saltado: {0}" -f $path)
                continue
            }

            $skipped.Add($path)
            Write-Log ("No existe: {0}" -f $path)
            continue
        }

        Protect-FolderContent -Path $path -GroupName $UsersGroup
        $done.Add($path)
    } catch {
        $failed.Add(($path + " => " + $_.Exception.Message))
        Write-Log ("Error: {0} => {1}" -f $path, $_.Exception.Message)
    }
}

$report = @(
    "PROTEGER MATERIALES SALA OK",
    ("Host: {0}" -f $env:COMPUTERNAME),
    ("Date: {0}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss")),
    "Protegidos:",
    ($done | Sort-Object),
    "",
    "Saltados:",
    ($skipped | Sort-Object),
    "",
    "Errores:",
    ($failed | Sort-Object)
)

$report | Set-Content -Path "C:\Windows\Temp\proteger_materiales_sala_done.txt" -Encoding UTF8
Write-Log "=== PROTEGER_MATERIALES_SALA END ==="
