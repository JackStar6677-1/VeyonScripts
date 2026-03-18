param(
    [string]$BaseDir = "C:\ProgramData\CastelRemote"
)

$ErrorActionPreference = "Stop"

$queueDir = Join-Path $BaseDir "admin-queue"
$processedDir = Join-Path $BaseDir "admin-processed"
$logDir = Join-Path $BaseDir "logs"
$logFile = Join-Path $logDir "admin_bridge.log"

foreach ($dir in @($BaseDir, $queueDir, $processedDir, $logDir)) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

function Write-Log {
    param([string]$Message)
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message
    Add-Content -Path $logFile -Value $line
}

function Invoke-BridgeCommand {
    param([pscustomobject]$Command)

    switch ($Command.action) {
        "powershell_file" {
            if ([string]::IsNullOrWhiteSpace($Command.path)) {
                throw "powershell_file requiere path"
            }

            $params = @()
            if (-not [string]::IsNullOrWhiteSpace($Command.arguments)) {
                $params += $Command.arguments
            }

            $argLine = "-NoProfile -ExecutionPolicy Bypass -File `"$($Command.path)`""
            if ($params.Count -gt 0) {
                $argLine += " " + ($params -join " ")
            }

            $psi = New-Object System.Diagnostics.ProcessStartInfo
            $psi.FileName = "powershell.exe"
            $psi.Arguments = $argLine
            $psi.UseShellExecute = $false
            $psi.RedirectStandardOutput = $true
            $psi.RedirectStandardError = $true
            $process = [System.Diagnostics.Process]::Start($psi)
            $stdout = $process.StandardOutput.ReadToEnd()
            $stderr = $process.StandardError.ReadToEnd()
            $process.WaitForExit()

            return [pscustomobject]@{
                ExitCode = $process.ExitCode
                StdOut = $stdout
                StdErr = $stderr
            }
        }
        "powershell_inline" {
            if ([string]::IsNullOrWhiteSpace($Command.code)) {
                throw "powershell_inline requiere code"
            }

            $psi = New-Object System.Diagnostics.ProcessStartInfo
            $psi.FileName = "powershell.exe"
            $psi.Arguments = "-NoProfile -ExecutionPolicy Bypass -Command $($Command.code)"
            $psi.UseShellExecute = $false
            $psi.RedirectStandardOutput = $true
            $psi.RedirectStandardError = $true
            $process = [System.Diagnostics.Process]::Start($psi)
            $stdout = $process.StandardOutput.ReadToEnd()
            $stderr = $process.StandardError.ReadToEnd()
            $process.WaitForExit()

            return [pscustomobject]@{
                ExitCode = $process.ExitCode
                StdOut = $stdout
                StdErr = $stderr
            }
        }
        "cmd" {
            if ([string]::IsNullOrWhiteSpace($Command.command)) {
                throw "cmd requiere command"
            }

            $psi = New-Object System.Diagnostics.ProcessStartInfo
            $psi.FileName = "cmd.exe"
            $psi.Arguments = "/c $($Command.command)"
            $psi.UseShellExecute = $false
            $psi.RedirectStandardOutput = $true
            $psi.RedirectStandardError = $true
            $process = [System.Diagnostics.Process]::Start($psi)
            $stdout = $process.StandardOutput.ReadToEnd()
            $stderr = $process.StandardError.ReadToEnd()
            $process.WaitForExit()

            return [pscustomobject]@{
                ExitCode = $process.ExitCode
                StdOut = $stdout
                StdErr = $stderr
            }
        }
        default {
            throw ("accion no soportada: {0}" -f $Command.action)
        }
    }
}

Write-Log "Admin bridge started"

$pending = Get-ChildItem -Path $queueDir -Filter "*.json" -File -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime

foreach ($file in $pending) {
    $json = Get-Content -Path $file.FullName -Raw -Encoding UTF8
    $resultFile = Join-Path $processedDir ($file.BaseName + ".result.json")

    try {
        $command = $json | ConvertFrom-Json
        $result = Invoke-BridgeCommand -Command $command
        $payload = [ordered]@{
            id = $command.id
            host = $env:COMPUTERNAME
            finishedAt = (Get-Date).ToString("s")
            exitCode = $result.ExitCode
            stdout = $result.StdOut
            stderr = $result.StdErr
            action = $command.action
        }
        $payload | ConvertTo-Json -Depth 6 | Set-Content -Path $resultFile -Encoding UTF8
        Remove-Item -Path $file.FullName -Force -ErrorAction SilentlyContinue
        Write-Log ("OK => {0} => exit={1}" -f $file.Name, $result.ExitCode)
    } catch {
        $payload = [ordered]@{
            id = $file.BaseName
            host = $env:COMPUTERNAME
            finishedAt = (Get-Date).ToString("s")
            exitCode = -1
            stdout = ""
            stderr = $_.Exception.Message
            action = "error"
        }
        $payload | ConvertTo-Json -Depth 6 | Set-Content -Path $resultFile -Encoding UTF8
        Remove-Item -Path $file.FullName -Force -ErrorAction SilentlyContinue
        Write-Log ("ERROR => {0} => {1}" -f $file.Name, $_.Exception.Message)
    }
}
