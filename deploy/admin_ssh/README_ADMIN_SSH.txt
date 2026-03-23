Flujo SSH para el PC maestro 192.168.0.106
===========================================

Archivos principales:

- `SYNC_REPO_TO_106_SSH.ps1`
  Sincroniza por SSH/scp el repo y la configuracion de Veyon hacia el PC `192.168.0.106`.

- `INSTALL_SYNC_TASK_106_SSH.ps1`
  Crea una tarea programada local para ejecutar la sincronizacion cada N minutos.

Uso manual:

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy\admin_ssh\SYNC_REPO_TO_106_SSH.ps1 -SshTarget "Colegio@192.168.0.106"
```

Si usas clave SSH:

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy\admin_ssh\SYNC_REPO_TO_106_SSH.ps1 -SshTarget "Colegio@192.168.0.106" -IdentityFile "C:\Users\Jack\.ssh\id_ed25519"
```

Instalar tarea cada 15 minutos:

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy\admin_ssh\INSTALL_SYNC_TASK_106_SSH.ps1 -IntervalMinutes 15
```

Con clave SSH:

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy\admin_ssh\INSTALL_SYNC_TASK_106_SSH.ps1 -IntervalMinutes 15 -IdentityFile "C:\Users\Jack\.ssh\id_ed25519"
```

Requisitos:

- `ssh.exe` y `scp.exe` disponibles en Windows.
- OpenSSH Server activo en el PC `106`.
- Acceso SSH valido al usuario remoto.
- `veyon-cli.exe` instalado localmente y remoto.
- `VeyonMaster.json` presente en `%APPDATA%\Veyon\Config`.
