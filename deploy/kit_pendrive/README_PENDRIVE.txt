KIT PENDRIVE - PREPARACION LOCAL POR EQUIPO
===========================================

Contenido:
1) PREPARAR_REMOTO_WIN10.bat
   - Ejecutar UNA vez en cada PC (doble clic, aceptar UAC).
   - Habilita WinRM + firewall + ajustes remotos.
2) RESTAURAR_VEYON_SALA.bat
   - Ejecutar en el PC maestro como administrador.
   - Importa las claves publica/privada de la sala y restaura `VeyonMaster.json` desde los respaldos por defecto.

Operacion centralizada:
- Los scripts que se ejecutan desde el PC administrador ahora viven en:
  - `deploy/admin_winrm/`
- Los componentes que se copian a los clientes viven en:
  - `deploy/componentes_cliente/`

USO RAPIDO
----------
Paso A) Preparar PCs destino:
- En cada PC alumno: ejecutar PREPARAR_REMOTO_WIN10.bat y esperar "LISTO".

Paso B) Operar desde el PC administrador:
- Si cambiaste de equipo maestro o restauraste Windows: ejecutar RESTAURAR_VEYON_SALA.bat.
- Usa la carpeta `deploy/admin_winrm/` para acciones masivas por WinRM.
- Usa la carpeta `deploy/componentes_cliente/` para los payloads/componentes que se copian a los clientes.
