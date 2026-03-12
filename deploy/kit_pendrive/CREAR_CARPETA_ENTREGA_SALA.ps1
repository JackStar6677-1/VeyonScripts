param(
    [string]$FolderPath = "C:\Users\Public\Desktop\Entrega Sala",
    [string]$UsersGroup = "Users"
)

$ErrorActionPreference = "Stop"
$logFile = "C:\Windows\Temp\crear_carpeta_entrega_sala.log"

function Write-Log {
    param([string]$Message)
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message
    Add-Content -Path $logFile -Value $line
}

function Ensure-Folder {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        New-Item -Path $Path -ItemType Directory -Force | Out-Null
        Write-Log ("Carpeta creada: {0}" -f $Path)
    }
}

function Set-EntregaAcl {
    param(
        [string]$Path,
        [string]$GroupName
    )

    $acl = Get-Acl -Path $Path
    $acl.SetAccessRuleProtection($true, $false)
    $acl.Access | ForEach-Object { [void]$acl.RemoveAccessRule($_) }

    $adminsRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
        "Administrators",
        "FullControl",
        "ContainerInherit,ObjectInherit",
        "None",
        "Allow"
    )
    $systemRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
        "SYSTEM",
        "FullControl",
        "ContainerInherit,ObjectInherit",
        "None",
        "Allow"
    )
    $usersAllowRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
        $GroupName,
        "ReadAndExecute, Write, Synchronize",
        "ContainerInherit,ObjectInherit",
        "None",
        "Allow"
    )
    $usersDenyRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
        $GroupName,
        "Delete, DeleteSubdirectoriesAndFiles",
        "ContainerInherit,ObjectInherit",
        "None",
        "Deny"
    )

    $acl.AddAccessRule($adminsRule) | Out-Null
    $acl.AddAccessRule($systemRule) | Out-Null
    $acl.AddAccessRule($usersAllowRule) | Out-Null
    $acl.AddAccessRule($usersDenyRule) | Out-Null

    Set-Acl -Path $Path -AclObject $acl
    Write-Log ("ACL aplicada a: {0}" -f $Path)
}

Write-Log "=== CREAR_CARPETA_ENTREGA_SALA START ==="
Write-Log ("Host={0} FolderPath={1}" -f $env:COMPUTERNAME, $FolderPath)

Ensure-Folder -Path $FolderPath
Set-EntregaAcl -Path $FolderPath -GroupName $UsersGroup

$report = @(
    "CARPETA ENTREGA SALA OK",
    ("Host: {0}" -f $env:COMPUTERNAME),
    ("Date: {0}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss")),
    ("Folder: {0}" -f $FolderPath),
    ("UsersGroup: {0}" -f $UsersGroup),
    "Permisos: lectura + escritura permitidas, eliminacion denegada para usuarios comunes"
)

$report | Set-Content -Path "C:\Windows\Temp\crear_carpeta_entrega_sala_done.txt" -Encoding UTF8
Write-Log "=== CREAR_CARPETA_ENTREGA_SALA END ==="
