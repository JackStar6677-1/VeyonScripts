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

7) GUI_AGENTE_INTERACTIVO.ps1
   - Agente liviano que corre dentro de la sesion del usuario.
   - Ejecuta GUIs visibles y recibe comandos de teclado por cola local.

8) INSTALAR_GUI_AGENTE_WINRM.ps1
   - Instala el agente interactivo en todos los equipos por WinRM.
   - Lo deja en inicio comun para que cargue en cada login.

9) ENVIAR_GUI_COMANDO_WINRM.ps1
   - Encola acciones remotas para el agente interactivo.
   - Permite:
     - launch : abrir un programa visible
     - keys   : enviar teclas a una ventana por titulo

10) ADMIN_ELEVATION_BRIDGE.ps1
   - Runner elevado que procesa comandos admin desde cola local.
   - Ejecuta con privilegios altos via tarea programada.

11) INSTALAR_ELEVACION_WINRM.ps1
   - Instala el bridge admin en todos los equipos por WinRM.
   - Crea la tarea `Castel-AdminBridge` como `SYSTEM`.

12) ENVIAR_ADMIN_COMANDO_WINRM.ps1
   - Encola un comando admin y dispara la tarea remota.
   - Evita depender del prompt UAC y de escribir la clave.

13) RESET_CHROME_COMPARTIDO.ps1
   - Cierra Chrome y elimina `User Data` de los perfiles locales.
   - Pensado para PCs compartidos por alumnos y docentes.
   - Opcion `-DisableChromeSignin` para bloquear inicio de sesion en Chrome.

14) PROTEGER_MATERIALES_SALA.ps1
   - Protege carpetas de materiales institucionales contra borrado por usuarios.
   - Mantiene lectura/ejecucion para `Users` y niega eliminacion.
   - Pensado para carpetas compartidas del colegio, no para bloquear todo `Documents`.

15) CREAR_CARPETA_ENTREGA_SALA.ps1
   - Crea una carpeta fija en el escritorio publico.
   - Permite a `Users` leer y escribir.
   - Niega eliminacion de archivos, subcarpetas y de la carpeta misma.

16) CASTEL_REMOTO.ps1
   - Orquestador central del kit.
   - Unifica estado, WOL, bridge admin, agente GUI y payloads comunes.
   - Incluye `-WhatIfMode` para revisar comandos sin ejecutarlos.

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
- WinRM NO puede manejar GUI de forma directa en Session 0. Para GUI visible usa el agente interactivo.
- Para acciones con privilegios altos usa el bridge admin, no el cuadro UAC.
- Ejemplos de teclas SendKeys:
  - Enter: `~`
  - Numero 1: `1`
  - Alt+F4: `%{F4}`
  - Tab: `{TAB}`

Ejemplos bridge admin:
- Instalar:
  - `.\INSTALAR_ELEVACION_WINRM.ps1`
- Ejecutar un PS1 elevado ya presente en el cliente:
  - `.\ENVIAR_ADMIN_COMANDO_WINRM.ps1 -Action powershell_file -Path "C:\ProgramData\CastelRemote\mi-script.ps1"`
- Ejecutar un comando inline elevado:
  - `.\ENVIAR_ADMIN_COMANDO_WINRM.ps1 -Action powershell_inline -Code "Set-ExecutionPolicy Bypass -Scope LocalMachine -Force"`
- Ejecutar CMD elevado:
  - `.\ENVIAR_ADMIN_COMANDO_WINRM.ps1 -Action cmd -Command "gpupdate /force"`

Ejemplo reset Chrome:
- Ejecutar reset total de Chrome en clientes:
  - `.\ENVIAR_ADMIN_COMANDO_WINRM.ps1 -Action powershell_file -Path "C:\ProgramData\CastelRemote\RESET_CHROME_COMPARTIDO.ps1"`
- Si primero copias el script al cliente y quieres endurecer modo compartido:
  - `.\ENVIAR_ADMIN_COMANDO_WINRM.ps1 -Action powershell_file -Path "C:\ProgramData\CastelRemote\RESET_CHROME_COMPARTIDO.ps1" -Arguments "-DisableChromeSignin"`

Ejemplo proteccion de materiales:
- Aplicar proteccion a carpetas de materiales:
  - `.\ENVIAR_ADMIN_COMANDO_WINRM.ps1 -Action powershell_file -Path "C:\ProgramData\CastelRemote\PROTEGER_MATERIALES_SALA.ps1"`
- Solo sobre carpetas ya existentes:
  - `.\ENVIAR_ADMIN_COMANDO_WINRM.ps1 -Action powershell_file -Path "C:\ProgramData\CastelRemote\PROTEGER_MATERIALES_SALA.ps1" -Arguments "-ProtectOnlyExisting"`

Ejemplo carpeta de entrega en escritorio:
- Crear carpeta fija `Entrega Sala` en el escritorio publico:
  - `.\ENVIAR_ADMIN_COMANDO_WINRM.ps1 -Action powershell_file -Path "C:\ProgramData\CastelRemote\CREAR_CARPETA_ENTREGA_SALA.ps1"`

Ejemplos orquestador:
- Ver estado general:
  - `.\CASTEL_REMOTO.ps1 -Action status`
- Despertar sala:
  - `.\CASTEL_REMOTO.ps1 -Action wol`
- Instalar bridge admin:
  - `.\CASTEL_REMOTO.ps1 -Action install-admin-bridge`
- Reset Chrome endurecido:
  - `.\CASTEL_REMOTO.ps1 -Action reset-chrome -DisableChromeSignin -IncludeEdge`
- Crear carpeta de entrega:
  - `.\CASTEL_REMOTO.ps1 -Action create-entrega`
- Simular sin ejecutar:
  - `.\CASTEL_REMOTO.ps1 -Action reset-chrome -WhatIfMode`
