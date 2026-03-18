ADMIN WINRM - OPERACION CENTRAL DESDE EL PC ADMIN
=================================================

Esta carpeta contiene los scripts que se ejecutan desde el equipo administrador
contra toda la sala por WinRM.

Contenido principal:
- `CASTEL_REMOTO.ps1`: orquestador central.
- `hosts_castel.txt`: lista operativa de la sala.
- `EJECUTAR_MASIVO_WINRM.*`: ejecucion masiva de payloads.
- `EJECUTAR_MASIVO_AUTO_CRED.*`: variante auto-credencial.
- `ENVIAR_WOL_CASTEL.ps1`: Wake-on-LAN masivo.
- `INSTALAR_GUI_AGENTE_WINRM.ps1`: instala agente GUI.
- `INSTALAR_ELEVACION_WINRM.ps1`: instala bridge admin.
- `ENVIAR_GUI_COMANDO_WINRM.ps1`: comandos GUI visibles.
- `ENVIAR_ADMIN_COMANDO_WINRM.ps1`: comandos elevados remotos.
- `PROGRAMAR_ENERGIA_LAB_WINRM.ps1`: programa apagado.
- `REMOVE_APAGADO_AUTOMATICO_WINRM.ps1`: retira tareas de apagado.
- `APLICAR_FONDO_CASTEL_WINRM.ps1`: distribuye wallpaper.
- `INSTALAR_IMPRESORA_BROTHER_WINRM.ps1`: instala impresora de sala.

Notas:
- Esta carpeta NO es el kit pendrive.
- Los componentes que estos scripts copian a los clientes viven en `..\componentes_cliente\`.
- El script `PREPARAR_REMOTO_WIN10.bat` vive en `..\kit_pendrive\`.
