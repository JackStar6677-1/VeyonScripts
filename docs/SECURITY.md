# Seguridad y datos locales

Este repositorio debe contener codigo, documentacion y ejemplos sanitizados. La informacion operativa real del colegio se mantiene local.

## No versionar

- Inventarios reales de IP/MAC.
- Archivos `.cfg` de herramientas.
- Logs de ejecucion.
- Reportes `_reports/`.
- Bases SQLite locales.
- Backups de drivers o exports.
- Entornos virtuales Python.
- Credenciales, tokens o claves.
- Configuraciones con nombres de usuario reales.

## Donde dejar ejemplos

Usa `examples/` para mostrar formatos sin exponer datos reales. Los ejemplos deben usar rangos reservados para documentacion (`192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`) y MACs ficticias.

## Revision antes de push

Comandos utiles:

```powershell
git status --short
git ls-files *.csv *.cfg *.log *.sqlite
git diff --cached --stat
```

Si un archivo operativo ya estaba trackeado por error, se debe quitar del indice sin borrarlo localmente:

```powershell
git rm --cached -r data backups void_env
```

## Respaldos

Los respaldos automaticos locales van fuera del repo:

```text
C:\Users\Jack\Documents\CodexOrganizado\Backups Codex Automatico
```

No deben moverse a `backups/` dentro de este proyecto.
