PENDRIVE OPERATIVO CASTEL
=========================

Estructura recomendada:

01-PREPARAR-EQUIPO
- PREPARAR_REMOTO_WIN10.bat
  Ejecutar UNA vez en cada PC destino como administrador.
  Habilita WinRM, firewall y deja el equipo listo para gestion remota.

02-EJECUCION-MASIVA
- EJECUTAR_MASIVO_WINRM.bat / .ps1
  Para lanzar un payload con una credencial admin comun.
- EJECUTAR_MASIVO_AUTO_CRED.bat / .ps1
  Para probar usuarios tipicos si cambia el nombre de la cuenta local.
- hosts_castel.txt
  Lista de IPs/equipos destino.
- payload.ps1
  Payload de ejemplo. Editalo antes de usarlo.

03-UTILIDADES-PORTABLES
- RESET_CHROME_TOTAL_PORTABLE.bat / .ps1
  Limpia Chrome completamente del equipo local.

04-VEYON-MAESTRO
- RESTAURAR_VEYON_SALA.bat / .ps1
  Restaura claves/config del maestro de Veyon desde los respaldos.

Notas:
- Los scripts de esta carpeta fueron revisados y actualizados desde el repo local.
- Si modificas algo importante, conviene volver a refrescar esta carpeta desde el repo.
- Evita guardar reportes CSV y pruebas sueltas aqui; mejor dejarlos en el PC local.
