COMPONENTES CLIENTE
===================

Esta carpeta contiene payloads y scripts que se copian a los equipos cliente,
normalmente hacia `C:\ProgramData\CastelRemote\`.

Contenido:
- `GUI_AGENTE_INTERACTIVO.ps1`: agente GUI por cola local.
- `ADMIN_ELEVATION_BRIDGE.ps1`: bridge elevado ejecutado como SYSTEM.
- `RESET_CHROME_COMPARTIDO.ps1`: reinicio de perfiles Chrome.
- `PROTEGER_MATERIALES_SALA.ps1`: ACLs para materiales institucionales.
- `CREAR_CARPETA_ENTREGA_SALA.ps1`: carpeta publica controlada.
- `JACKOPTIMIZED.ps1`: payload de optimizacion local.

No ejecutar estos scripts desde aqui por costumbre si la idea es operar la sala.
Para despliegue masivo usa `..\admin_winrm\`.
