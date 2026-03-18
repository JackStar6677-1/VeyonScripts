param(
    [string]$BaseDir = "C:\ProgramData\CastelRemote",
    [int]$PollSeconds = 2
)

$ErrorActionPreference = "Continue"

$queueDir = Join-Path $BaseDir "queue"
$processingDir = Join-Path $BaseDir "processing"
$processedDir = Join-Path $BaseDir "processed"
$logDir = Join-Path $BaseDir "logs"
$logFile = Join-Path $logDir "gui_agent.log"
$mutexName = "Global\CastelGuiAgent"

foreach ($dir in @($BaseDir, $queueDir, $processingDir, $processedDir, $logDir)) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

function Write-Log {
    param([string]$Message)
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message
    Add-Content -Path $logFile -Value $line
}

function Wait-Window {
    param(
        [Parameter(Mandatory = $true)][string]$WindowTitle,
        [int]$TimeoutSec = 15
    )

    $shell = New-Object -ComObject WScript.Shell
    $deadline = (Get-Date).AddSeconds($TimeoutSec)

    while ((Get-Date) -lt $deadline) {
        if ($shell.AppActivate($WindowTitle)) {
            Start-Sleep -Milliseconds 300
            return $shell
        }
        Start-Sleep -Milliseconds 400
    }

    return $null
}

function Invoke-LaunchCommand {
    param([pscustomobject]$Command)

    if ([string]::IsNullOrWhiteSpace($Command.path)) {
        throw "launch requiere 'path'"
    }

    $startInfo = @{
        FilePath = $Command.path
        WindowStyle = "Normal"
    }

    if (-not [string]::IsNullOrWhiteSpace($Command.arguments)) {
        $startInfo.ArgumentList = $Command.arguments
    }
    if (-not [string]::IsNullOrWhiteSpace($Command.workingDirectory)) {
        $startInfo.WorkingDirectory = $Command.workingDirectory
    }

    Start-Process @startInfo | Out-Null
    Write-Log ("launch => {0} {1}" -f $Command.path, $Command.arguments)
}

function Invoke-KeysCommand {
    param([pscustomobject]$Command)

    if ([string]::IsNullOrWhiteSpace($Command.windowTitle)) {
        throw "keys requiere 'windowTitle'"
    }
    if ([string]::IsNullOrWhiteSpace($Command.keys)) {
        throw "keys requiere 'keys'"
    }

    $timeoutSec = 15
    if ($Command.timeoutSec) {
        $timeoutSec = [int]$Command.timeoutSec
    }

    $shell = Wait-Window -WindowTitle $Command.windowTitle -TimeoutSec $timeoutSec
    if ($null -eq $shell) {
        throw ("No se encontro ventana: {0}" -f $Command.windowTitle)
    }

    Start-Sleep -Milliseconds 300
    $shell.SendKeys($Command.keys)
    Write-Log ("keys => title={0} keys={1}" -f $Command.windowTitle, $Command.keys)
}

function Invoke-CommandFile {
    param([string]$FilePath)

    $json = Get-Content -Path $FilePath -Raw -Encoding UTF8
    $command = $json | ConvertFrom-Json

    if ($command.delayMs) {
        Start-Sleep -Milliseconds ([int]$command.delayMs)
    }

    switch ($command.action) {
        "launch" { Invoke-LaunchCommand -Command $command }
        "keys" { Invoke-KeysCommand -Command $command }
        default { throw ("accion no soportada: {0}" -f $command.action) }
    }
}

function Claim-CommandFile {
    param([System.IO.FileInfo]$File)

    $claimedPath = Join-Path $processingDir $File.Name
    Move-Item -Path $File.FullName -Destination $claimedPath -Force -ErrorAction Stop
    return $claimedPath
}

$createdNew = $false
$mutex = New-Object System.Threading.Mutex($true, $mutexName, [ref]$createdNew)
if (-not $createdNew) {
    Write-Log "Agente ya esta ejecutandose. Saliendo."
    exit 0
}

Write-Log "GUI agent iniciado"

try {
    while ($true) {
        $files = Get-ChildItem -Path $queueDir -Filter "*.json" -File -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime

        foreach ($file in $files) {
            $claimedPath = $null
            try {
                $claimedPath = Claim-CommandFile -File $file
                $destination = Join-Path $processedDir $file.Name
                Invoke-CommandFile -FilePath $claimedPath
                Move-Item -Path $claimedPath -Destination $destination -Force
                Write-Log ("OK => {0}" -f $file.Name)
            } catch {
                $errorName = [IO.Path]::GetFileNameWithoutExtension($file.Name) + ".error.json"
                $errorPath = Join-Path $processedDir $errorName
                if ($claimedPath -and (Test-Path $claimedPath)) {
                    Move-Item -Path $claimedPath -Destination $errorPath -Force
                } elseif (Test-Path $file.FullName) {
                    Move-Item -Path $file.FullName -Destination $errorPath -Force
                }
                Write-Log ("ERROR => {0} => {1}" -f $file.Name, $_.Exception.Message)
            }
        }

        Start-Sleep -Seconds $PollSeconds
    }
} finally {
    $mutex.ReleaseMutex() | Out-Null
    $mutex.Dispose()
}
