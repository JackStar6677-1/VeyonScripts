param(
  [string]$ReservasCsvPath
)
$ErrorActionPreference = "SilentlyContinue"

function Send-Wol {
  param([string]$Mac,[string]$Broadcast='192.168.0.255',[int]$Port=9)
  $macBytes = ($Mac -replace '[:-]','' -split '(.{2})' | ? { $_ }) | % { [byte]("0x$_") }
  if($macBytes.Count -ne 6){ return $false }
  $packet = [byte[]](,0xFF * 6 + ($macBytes * 16))
  $udp = New-Object System.Net.Sockets.UdpClient
  $udp.Connect($Broadcast,$Port)
  [void]$udp.Send($packet,$packet.Length)
  $udp.Close()
  return $true
}

$rows = Import-Csv $ReservasCsvPath
$ok=0
foreach($r in $rows){
  if(Send-Wol -Mac $r.MAC){ $ok++ }
}
"WOL enviado: $ok equipos - $(Get-Date -Format s)" | Set-Content C:\Windows\Temp\jackoptimized_wol.log -Encoding UTF8
