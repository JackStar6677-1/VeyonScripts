KIT PENDRIVE - GESTION REMOTA MASIVA (WIN10)
============================================

Contenido:
1) PREPARAR_REMOTO_WIN10.bat
   - Ejecutar UNA vez en cada PC (doble clic, aceptar UAC).
   - Habilita WinRM + firewall + ajustes remotos.

2) EJECUTAR_MASIVO_WINRM.bat
   - Ejecutar en el PC administrador.
   - Pide credenciales y corre un payload en todos los hosts.

3) EJECUTAR_MASIVO_WINRM.ps1
   - Motor interno del punto 2.

4) EJECUTAR_MASIVO_AUTO_CRED.bat
   - Variante automatica para entornos donde el usuario local cambia
     (por ejemplo: Admin, Profesor, Usuario) pero la clave es la misma.

5) EJECUTAR_MASIVO_AUTO_CRED.ps1
   - Motor del modo auto-credencial.

6) hosts_castel.txt
   - Lista de equipos destino (IP por linea).
   - Edita aqui para incluir/quitar equipos.

USO RAPIDO
----------
Paso A) Preparar PCs destino:
- En cada PC alumno: ejecutar PREPARAR_REMOTO_WIN10.bat y esperar "LISTO".

Paso B) Definir payload:
- Crea en esta carpeta un archivo llamado:
  - payload.ps1   (recomendado), o
  - payload.bat

Paso C) Ejecutar en masa:
- Desde el PC del encargado:
  - Ejecuta EJECUTAR_MASIVO_WINRM.bat
  - Ingresa credencial admin valida para los PCs.

Modo alternativo (usuario variable, clave comun):
- Ejecuta EJECUTAR_MASIVO_AUTO_CRED.bat
- Ingresa la clave comun (ej: administrativa)
- El script prueba automaticamente: Admin, Profesor, Usuario por host.

Salida:
- Genera reporte CSV: reporte_masivo_YYYYMMDD_HHMMSS.csv

Notas:
- Si sale NO_WINRM en un equipo, faltan pasos del PREPARAR o hay firewall/red.
- Si el usuario local admin no coincide entre PCs, usa una credencial comun.
