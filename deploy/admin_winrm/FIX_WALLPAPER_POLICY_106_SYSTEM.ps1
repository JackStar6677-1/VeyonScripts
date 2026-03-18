param(
    [string]$ComputerName = "192.168.0.106",
    [string]$UserName = "Colegio",
    [string]$PasswordPlain = "administrativa"
)

$ErrorActionPreference = "Stop"

$pass = ConvertTo-SecureString $PasswordPlain -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential("$ComputerName\$UserName", $pass)

Invoke-Command -ComputerName $ComputerName -Credential $cred -ScriptBlock {
    $scriptPath = "C:\CastelAdmin\fix_wallpaper_policy_system.ps1"
    $taskName = "CastelFixWallpaperPolicy106"

    $systemScript = @'
$userPol = "C:\Windows\System32\GroupPolicy\User\Registry.pol"
$backupDir = "C:\CastelAdmin\backups\GroupPolicy_User_SYSTEM_20260316_140500"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
if (Test-Path $userPol) {
    Copy-Item $userPol (Join-Path $backupDir "Registry.pol.system.bak") -Force
}
$bytes = [byte[]](0x50,0x52,0x65,0x67,0x01,0x00,0x00,0x00)
[System.IO.File]::WriteAllBytes($userPol, $bytes)
foreach ($key in @(
    "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System",
    "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer",
    "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\ActiveDesktop",
    "HKCU:\SOFTWARE\Policies\Microsoft\Windows\Personalization",
    "HKCU:\SOFTWARE\Policies\Microsoft\Windows\Control Panel\Desktop"
)) {
    if (Test-Path $key) {
        Remove-Item $key -Recurse -Force -ErrorAction SilentlyContinue
    }
}
gpupdate /target:user /force | Out-Null
'@

    Set-Content -Path $scriptPath -Value $systemScript -Encoding ASCII -Force

    schtasks /Delete /TN $taskName /F 1>$null 2>$null
    schtasks /Create /TN $taskName /SC ONCE /ST 23:59 /RU SYSTEM /RL HIGHEST /TR "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`"" /F | Out-Null
    schtasks /Run /TN $taskName | Out-Null
    Start-Sleep -Seconds 5

    [pscustomobject]@{
        ScriptPath = $scriptPath
        RegistryPolLength = (Get-Item "C:\Windows\System32\GroupPolicy\User\Registry.pol").Length
        RegistryPolLastWrite = (Get-Item "C:\Windows\System32\GroupPolicy\User\Registry.pol").LastWriteTime
    }
}
