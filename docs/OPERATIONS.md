# Operacion diaria

Esta guia resume como usar el repo en terreno sin mezclar datos locales con codigo fuente.

## Requisitos

- Windows con PowerShell.
- Python instalado en el PC administrador.
- Veyon instalado si se usaran comandos `veyon-cli`.
- WakeMeOnLAN disponible en `tools/wakemeonlan/`.
- Credenciales y configuraciones reales guardadas fuera de Git.

## Actualizar Veyon

Desde la raiz del repo:

```powershell
.\VEYON_MAESTRO.bat
```

El flujo esperado:

1. Solicita elevacion si hace falta.
2. Escanea rangos IPv4 con WakeMeOnLAN.
3. Verifica puerto Veyon en clientes detectados.
4. Resuelve conflictos de IP/MAC.
5. Asigna nombres `CASTEL-XX`.
6. Crea ubicaciones necesarias.
7. Reemplaza cada equipo por nombre usando `veyon-cli`.

## Ubicaciones fuera de sala principal

Cuando un PC fisicamente no pertenece a `SalaComputacion`, agrega una regla en `scripts/principales/VEYON_MAESTRO.py`:

```python
LOCATION_OVERRIDES_BY_NAME = {
    "CASTEL-04": "6B",
}
```

Replica la regla por IP y MAC si el equipo puede aparecer con nombres temporales.

## WinRM

Los scripts de `deploy/admin_winrm/` se ejecutan desde el PC administrador. Guardan reportes operativos en `_reports/`, carpeta ignorada por Git.

Uso recomendado:

1. Validar hosts y credenciales localmente.
2. Ejecutar un comando simple sobre pocos equipos.
3. Revisar `_reports/`.
4. Ejecutar el lote completo.

## Kit pendrive

`deploy/kit_pendrive/` contiene scripts pensados para preparar o reparar equipos en terreno. Evita meter exports reales, contrasenas o logs en esa carpeta.

## Limpieza antes de commitear

Antes de publicar cambios:

```powershell
git status --short
git diff --stat
python -m py_compile .\scripts\principales\VEYON_MAESTRO.py
```

Si aparecen archivos bajo `data/`, `config/`, `memory/`, `tasks/`, `backups/`, `void_env/` o `_reports/`, no los agregues al commit.
