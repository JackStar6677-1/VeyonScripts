Write-Host "PAYLOAD DE EJEMPLO" -ForegroundColor Cyan
Write-Host "Edita este archivo antes de lanzarlo en toda la sala." -ForegroundColor Yellow
Write-Host ("Equipo: {0}" -f $env:COMPUTERNAME)
Write-Host ("Fecha : {0}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"))

# Ejemplo seguro:
# New-Item -ItemType Directory -Path 'C:\Temp\PruebaSala' -Force | Out-Null
# 'Hola desde WinRM' | Set-Content -Path 'C:\Temp\PruebaSala\ok.txt' -Encoding UTF8
