# Castel LabOps

Suite operativa para administrar laboratorios Windows del Colegio Castel Gandolfo con Veyon, Wake-on-LAN, WinRM y utilidades de soporte en terreno.

**Autor:** Pablo Elias Avendano Miranda
**Plataforma principal:** Windows / PowerShell
**Enfoque:** automatizacion pragmatica para salas de computacion, PCs de profesor y equipos de curso.

---

## Que resuelve

Este repositorio agrupa scripts y launchers para:

- Actualizar el directorio de Veyon desde escaneos de red.
- Mantener nombres logicos `CASTEL-XX` aunque cambien las IPs.
- Separar equipos fuera de la sala principal en ubicaciones Veyon propias.
- Encender equipos por Wake-on-LAN.
- Ejecutar tareas clave locals por WinRM.
- Preparar PCs con un kit portable.
- Instalar componentes cliente para acciones interactivas o elevadas.
- Documentar procedimientos repetibles sin subir datos reales del colegio.

## Estructura

```text
VeyonScripts/
|-- apps/                    # GUI y herramientas visuales
|-- deploy/                  # Material de despliegue y operacion remota
|   |-- admin_ssh/           # Sincronizacion por SSH para equipos puntuales
|   |-- admin_winrm/         # Orquestacion remota desde el PC administrador
|   |-- componentes_cliente/ # Payloads que se instalan en los clientes
|   `-- kit_pendrive/        # Kit portable/manual para terreno
|-- docs/                    # Arquitectura, seguridad y operacion
|-- examples/                # Datos de ejemplo sanitizados
|-- launchers/               # Launchers reales invocados desde la raiz
|-- reports/                 # Plantillas o reportes publicables
|-- scripts/                 # Scripts principales, diagnosticos y legacy
|-- tools/                   # Herramientas auxiliares
`-- *.bat                    # Wrappers de compatibilidad para escritorio
```

Las carpetas `data/`, `config/`, `memory/`, `tasks/`, `backups/`, `void_env/`, `_reports/` y archivos `.cfg`/logs operativos son locales. No deben versionarse.

## Uso rapido

Ejecutar desde PowerShell o con los `.bat` de la raiz:

```powershell
.\VEYON_MAESTRO.bat
.\MAPEO_FISICO_ADMIN.bat
.\WINRM_MAESTRO.bat
```

Los launchers de la raiz llaman a `launchers/`, y estos ejecutan los scripts reales dentro de `scripts/principales/`.

## Flujo recomendado

1. Preparar cada PC cliente con `deploy/kit_pendrive/`.
2. Validar conectividad y credenciales fuera del repo.
3. Mantener inventarios reales en `data/` local, nunca en Git.
4. Ejecutar el maestro de Veyon desde el PC administrador.
5. Usar `deploy/admin_winrm/` para acciones masivas.
6. Guardar salidas operativas en `_reports/` local.

## Ubicaciones Veyon especiales

`scripts/principales/VEYON_MAESTRO.py` mantiene reglas explicitas para equipos que no pertenecen a `SalaComputacion`:

| Equipo | IP | Ubicacion Veyon |
| --- | --- | --- |
| `CASTEL-04` | `192.168.0.104` | `6B` |
| `CASTEL-40` | `192.168.0.160` | `CuartoMedioB` |

Estas reglas evitan que el maestro vuelva a mezclar PCs de curso dentro de la sala principal.

## Documentacion

- [Arquitectura](docs/ARCHITECTURE.md)
- [Operacion diaria](docs/OPERATIONS.md)
- [Seguridad y datos locales](docs/SECURITY.md)
- [Ejemplo de reservas DHCP sanitizado](examples/reservas_dhcp_castel.example.csv)
- [GUI de mapeo fisico](apps/veyongui/README_GUI.md)

## Politica de datos

Este repo puede ser publico o privado, pero debe tratarse como codigo fuente. No se suben:

- Inventarios reales de IP/MAC.
- Configuraciones de WakeMeOnLAN.
- Logs o reportes con usuarios/equipos reales.
- Respaldos de drivers, exports o binarios generados.
- Entornos virtuales Python.
- Bases SQLite locales.

Usa `examples/` para ejemplos artificiales y `docs/` para explicar formatos.

## Validacion basica

```powershell
python -m py_compile .\scripts\principales\VEYON_MAESTRO.py
git status --short
```

Para pruebas reales de Veyon se requiere Windows con Veyon instalado y permisos de administrador.
