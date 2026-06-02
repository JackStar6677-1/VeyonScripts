$ErrorActionPreference = "Stop"

$sharedHome = Join-Path $env:USERPROFILE "OpenClawShared"
$env:OPENCLAW_HOME = $sharedHome

$gatewayPort = 18789
$logDir = Join-Path $sharedHome "logs"
$stdoutLog = Join-Path $logDir "gateway-windows.out.log"
$stderrLog = Join-Path $logDir "gateway-windows.err.log"

New-Item -ItemType Directory -Force -Path $sharedHome, $logDir | Out-Null

$openClawCommand = Get-Command openclaw -ErrorAction SilentlyContinue
if (-not $openClawCommand) {
  Write-Error "OpenClaw CLI is not on PATH for this Windows session. Install/update with: npm install -g openclaw@latest"
  exit 1
}

$openClawPath = $openClawCommand.Path
if (-not $openClawPath) {
  $openClawPath = $openClawCommand.Source
}

function Invoke-OpenClaw {
  param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $OpenClawArgs
  )

  $previousErrorActionPreference = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  if ($openClawPath -like "*.ps1") {
    try {
      & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $openClawPath @OpenClawArgs
    }
    finally {
      $ErrorActionPreference = $previousErrorActionPreference
    }
  }
  else {
    try {
      & $openClawPath @OpenClawArgs
    }
    finally {
      $ErrorActionPreference = $previousErrorActionPreference
    }
  }
}

function Start-OpenClawGateway {
  Remove-Item -LiteralPath $stdoutLog, $stderrLog -ErrorAction SilentlyContinue

  $args = @("gateway", "run", "--port", "$gatewayPort", "--tailscale", "off")

  if ($openClawPath -like "*.ps1") {
    $gatewayArgs = @(
      "-NoProfile",
      "-ExecutionPolicy",
      "Bypass",
      "-File",
      $openClawPath
    ) + $args
    Start-Process -WindowStyle Hidden -FilePath "powershell.exe" -ArgumentList $gatewayArgs `
      -RedirectStandardOutput $stdoutLog -RedirectStandardError $stderrLog
  }
  else {
    Start-Process -WindowStyle Hidden -FilePath $openClawPath -ArgumentList $args `
      -RedirectStandardOutput $stdoutLog -RedirectStandardError $stderrLog
  }
}

function Wait-OpenClawGateway {
  $deadline = (Get-Date).AddSeconds(90)
  do {
    Start-Sleep -Seconds 2
    $listener = Get-NetTCPConnection -LocalPort $gatewayPort -State Listen -ErrorAction SilentlyContinue
    if ($listener) {
      return $true
    }
  } until ((Get-Date) -gt $deadline)

  return $false
}

$listener = Get-NetTCPConnection -LocalPort $gatewayPort -State Listen -ErrorAction SilentlyContinue
if (-not $listener) {
  Start-OpenClawGateway
}

if (-not (Wait-OpenClawGateway)) {
  Write-Error "OpenClaw gateway did not start on port $gatewayPort. Check logs: $stdoutLog and $stderrLog"
  exit 1
}

$autoApproveScript = Join-Path $PSScriptRoot "OpenClaw-AutoApprove.ps1"
if (Test-Path $autoApproveScript) {
  $autoApproveRunning = Get-CimInstance Win32_Process -Filter "Name = 'powershell.exe' OR Name = 'pwsh.exe'" |
    Where-Object { $_.CommandLine -like "*OpenClaw-AutoApprove.ps1*" }

  if (-not $autoApproveRunning) {
    Start-Process -WindowStyle Hidden -FilePath "powershell.exe" -ArgumentList @(
      "-NoProfile",
      "-ExecutionPolicy",
      "Bypass",
      "-File",
      $autoApproveScript
    )
  }
}

$dashboardUrl = $null
try {
  $dashboardUrl = Invoke-OpenClaw "dashboard" "--no-open" 2>$null |
    Select-String -Pattern "^Dashboard URL:\s+(.*)$" |
    ForEach-Object { $_.Matches[0].Groups[1].Value } |
    Select-Object -First 1
}
catch {
  $dashboardUrl = $null
}

if ($dashboardUrl) {
  Start-Process $dashboardUrl
}
else {
  Start-Process "http://127.0.0.1:$gatewayPort/"
}
