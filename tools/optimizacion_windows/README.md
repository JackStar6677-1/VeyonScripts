# Optimizacion Windows 11 - PCs Lentos (4GB RAM + HDD)

## Descripcion del Proyecto

Suite completa de scripts de optimizacion para Windows 11 en equipos con recursos limitados (4GB de RAM y disco duro mecanico HDD). Los scripts estan diseñados para mejorar significativamente el rendimiento deshabilitando servicios innecesarios, optimizando efectos visuales y liberando recursos del sistema.

## Estructura del Proyecto

```
optimizacion_windows/
├── 01_deshabilitar_servicios.py      - Deshabilita servicios innecesarios
├── 02_optimizar_rendimiento_visual.py - Optimiza efectos visuales
├── 03_limpiar_archivos_temp.py       - Limpia archivos temporales
├── 04_optimizar_hdd.py                - Optimiza disco duro mecanico
├── 05_optimizar_inicio.py             - Optimiza programas de inicio
├── OPTIMIZAR_TODO.py                  - Script maestro (ejecuta todos)
├── OPTIMIZAR_TODO_ADMIN.bat           - Launcher con permisos admin
└── README.md                          - Este archivo
```

## Requisitos

- Windows 11
- Python 3.7 o superior
- Permisos de administrador
- 4GB de RAM (minimo)
- Disco duro mecanico (HDD)

## Scripts Disponibles

### 1. Deshabilitar Servicios (01_deshabilitar_servicios.py)

Deshabilita servicios de Windows que consumen recursos innecesariamente en equipos con recursos limitados.

**Servicios que deshabilita:**
- DiagTrack (Telemetria)
- dmwappushservice (Mensajes WAP)
- Servicios de Xbox (si no usas Xbox)
- Windows Search (indexacion, consume mucho en HDD)
- MapsBroker (Mapas)
- Servicios de biometria
- HomeGroup (compartir en red domestica)

**Servicios que cambia a MANUAL:**
- SysMain/Superfetch (consume mucho en HDD)
- Windows Update (para controlar cuando actualizar)
- Windows Defender (CUIDADO: reduce seguridad)
- Servicios de tablet y escritura a mano

**Uso:**
```bash
python 01_deshabilitar_servicios.py
```

### 2. Optimizar Rendimiento Visual (02_optimizar_rendimiento_visual.py)

Deshabilita efectos visuales y animaciones que consumen recursos graficos.

**Optimizaciones:**
- Deshabilita animaciones de barra de tareas
- Deshabilita transparencia de ventanas
- Ajusta para mejor rendimiento
- Deshabilita sombras de ventanas
- Deshabilita animaciones al minimizar/maximizar
- Deshabilita widgets de Windows 11
- Deshabilita chat de Teams
- Activa modo oscuro (consume menos recursos)
- Deshabilita busqueda web en menu inicio

**Uso:**
```bash
python 02_optimizar_rendimiento_visual.py
```

### 3. Limpiar Archivos Temporales (03_limpiar_archivos_temp.py)

Elimina archivos temporales y cache para liberar espacio en disco.

**Limpia:**
- Archivos temporales del usuario (TEMP)
- Archivos temporales del sistema (Windows\Temp)
- Cache de navegadores (Chrome, Edge, Firefox)
- Archivos prefetch
- Cache de instaladores
- Papelera de reciclaje
- Ejecuta el liberador de espacio de Windows

**Uso:**
```bash
python 03_limpiar_archivos_temp.py
```

### 4. Optimizar HDD (04_optimizar_hdd.py)

Optimiza el rendimiento del disco duro mecanico deshabilitando servicios que causan acceso constante.

**Optimizaciones:**
- Deshabilita Superfetch/SysMain (consume mucho en HDD)
- Deshabilita indexacion de Windows Search
- Configura plan de energia de alto rendimiento
- Deshabilita suspension del disco
- Proporciona instrucciones para optimizar archivo de paginacion
- Opcion para deshabilitar hibernacion (libera 4GB)
- Opcion para programar chkdsk
- Opcion para desfragmentar disco

**Recomendaciones para archivo de paginacion (4GB RAM):**
- Tamaño inicial: 6144 MB (1.5x RAM)
- Tamaño maximo: 8192 MB (2x RAM)

**Uso:**
```bash
python 04_optimizar_hdd.py
```

### 5. Optimizar Inicio (05_optimizar_inicio.py)

Optimiza el inicio de Windows deshabilitando programas innecesarios que se ejecutan al arrancar.

**Optimizaciones:**
- Muestra programas de inicio detectados
- Deshabilita inicio rapido (problemático en HDD)
- Reduce tiempo de espera del menu de inicio a 3 segundos
- Deshabilita Cortana en barra de tareas
- Deshabilita OneDrive al inicio
- Abre Administrador de tareas para deshabilitar programas manualmente

**Programas comunes a deshabilitar:**
- Microsoft Teams
- OneDrive (si no lo usas)
- Spotify
- Discord
- Adobe Creative Cloud

**Uso:**
```bash
python 05_optimizar_inicio.py
```

### 6. Script Maestro (OPTIMIZAR_TODO.py)

Ejecuta todos los scripts de optimizacion en orden secuencial.

**Proceso:**
1. Deshabilita servicios innecesarios
2. Optimiza rendimiento visual
3. Limpia archivos temporales
4. Optimiza disco duro (HDD)
5. Optimiza programas de inicio
6. Ofrece reiniciar el equipo

**Uso:**
```bash
python OPTIMIZAR_TODO.py
```

O usando el archivo BAT:
```bash
OPTIMIZAR_TODO_ADMIN.bat
```

## Instalacion

1. Clona o descarga el repositorio
2. Asegurate de tener Python 3.7+ instalado
3. Ejecuta los scripts con permisos de administrador

```bash
# Clonar repositorio
git clone https://github.com/usuario/optimizacion-windows.git
cd optimizacion-windows

# Ejecutar script maestro
python OPTIMIZAR_TODO.py
```

## Uso Rapido

### Opcion 1: Ejecutar todo de una vez

1. Ejecuta `OPTIMIZAR_TODO_ADMIN.bat` (como administrador)
2. Sigue las instrucciones en pantalla
3. Reinicia el equipo cuando termine

### Opcion 2: Ejecutar scripts individuales

1. Ejecuta cada script por separado segun tus necesidades:
   ```bash
   python 01_deshabilitar_servicios.py
   python 02_optimizar_rendimiento_visual.py
   python 03_limpiar_archivos_temp.py
   python 04_optimizar_hdd.py
   python 05_optimizar_inicio.py
   ```
2. Reinicia el equipo despues de ejecutar todos

## Mejoras Esperadas

Despues de ejecutar todos los scripts, deberias notar:

- **Inicio mas rapido**: 30-50% mas rapido
- **Menor uso de RAM**: 200-400MB liberados
- **Menos acceso al disco**: Reduccion significativa de lectura/escritura
- **Interfaz mas fluida**: Menos lag en animaciones
- **Mas espacio en disco**: 2-6GB liberados (dependiendo del uso)
- **Mejor respuesta general**: Aplicaciones se abren mas rapido

## Advertencias Importantes

1. **Backup**: Se recomienda crear un punto de restauracion antes de ejecutar los scripts
2. **Seguridad**: Algunos scripts deshabilitan Windows Defender temporalmente
3. **Funcionalidades**: Algunos servicios deshabilitados pueden afectar funcionalidades especificas
4. **Reinicio necesario**: Es NECESARIO reiniciar el equipo para aplicar todos los cambios
5. **Reversibilidad**: Los cambios se pueden revertir manualmente desde Servicios de Windows

## Como Revertir Cambios

Si algun cambio causa problemas:

1. **Servicios**:
   - Abrir `services.msc`
   - Buscar el servicio
   - Clic derecho > Propiedades
   - Cambiar "Tipo de inicio" a "Automatico"
   - Clic en "Iniciar"

2. **Efectos visuales**:
   - Panel de Control > Sistema > Configuracion avanzada
   - Pestaña "Opciones avanzadas" > Rendimiento > Configuracion
   - Seleccionar "Ajustar para obtener la mejor apariencia"

3. **Punto de restauracion**:
   - Buscar "Crear punto de restauracion"
   - Clic en "Restaurar sistema"
   - Seleccionar punto anterior a la optimizacion

## Configuracion Manual Adicional

### Archivo de Paginacion (Importante para 4GB RAM)

1. Panel de Control > Sistema > Configuracion avanzada del sistema
2. Pestaña "Opciones avanzadas" > Rendimiento > Configuracion
3. Pestaña "Opciones avanzadas" > Memoria virtual > Cambiar
4. Desmarcar "Administrar automaticamente el tamaño"
5. Seleccionar "Tamaño personalizado"
6. Establecer:
   - Tamaño inicial: 6144 MB
   - Tamaño maximo: 8192 MB
7. Clic en "Establecer" y luego "Aceptar"
8. Reiniciar el equipo

### Deshabilitar Programas de Inicio

1. Ctrl + Shift + Esc (Administrador de tareas)
2. Pestaña "Inicio"
3. Seleccionar programas innecesarios
4. Clic derecho > "Deshabilitar"

### Limpieza de Disco Adicional

1. Buscar "Liberador de espacio en disco"
2. Seleccionar unidad C:
3. Clic en "Limpiar archivos de sistema"
4. Marcar todas las opciones
5. Clic en "Aceptar"

## Metricas de Rendimiento

### Antes de la Optimizacion (Tipico)
- Tiempo de inicio: 2-3 minutos
- Uso de RAM en reposo: 2.8-3.2 GB
- Uso de disco en reposo: 80-100%
- Tiempo de apertura de aplicaciones: 5-10 segundos

### Despues de la Optimizacion (Esperado)
- Tiempo de inicio: 1-1.5 minutos
- Uso de RAM en reposo: 2.2-2.6 GB
- Uso de disco en reposo: 10-30%
- Tiempo de apertura de aplicaciones: 2-5 segundos

## Mantenimiento Recomendado

Para mantener el rendimiento optimo:

1. **Semanal**:
   - Ejecutar limpieza de archivos temporales
   - Cerrar programas no utilizados

2. **Mensual**:
   - Ejecutar desfragmentacion (solo HDD, NO SSD)
   - Revisar programas de inicio
   - Desinstalar programas no utilizados

3. **Cada 3 meses**:
   - Ejecutar scripts de optimizacion completos
   - Actualizar Windows (en horario no critico)

## Troubleshooting

### "No se pueden obtener permisos de administrador"
- Ejecuta el script como administrador manualmente
- Clic derecho en el archivo > "Ejecutar como administrador"

### "Error al deshabilitar servicio"
- El servicio puede estar en uso
- Reinicia el equipo y vuelve a intentar

### "El equipo esta mas lento despues de la optimizacion"
- Reinicia el equipo
- Algunos cambios requieren un reinicio completo
- Si persiste, revierte los cambios desde servicios

### "Algunas funcionalidades no funcionan"
- Revisa que servicios fueron deshabilitados
- Reactiva el servicio especifico desde `services.msc`

## Preguntas Frecuentes

**P: Es seguro ejecutar estos scripts?**  
R: Si, pero se recomienda crear un punto de restauracion antes.

**P: Cuanto tiempo tarda la optimizacion completa?**  
R: Entre 30-60 minutos, dependiendo del estado del equipo.

**P: Funcionan estos scripts en Windows 10?**  
R: La mayoria si, pero algunos ajustes son especificos de Windows 11.

**P: Puedo ejecutar solo algunos scripts?**  
R: Si, puedes ejecutar solo los que necesites.

**P: Los cambios son permanentes?**  
R: Si, pero se pueden revertir manualmente.

**P: Afecta estos scripts a la seguridad?**  
R: Algunos scripts deshabilitan Windows Defender temporalmente. Asegurate de tener otro antivirus.

## Contribuciones

Este proyecto esta abierto a contribuciones. Las areas de mejora incluyen:

- Mas optimizaciones especificas
- Scripts de reversion automatica
- Interfaz grafica
- Deteccion automatica de hardware

## Licencia

Este proyecto esta bajo la licencia MIT. Ver `LICENSE` para mas detalles.

## Contacto y Soporte

Para reportar problemas o sugerir mejoras, abre un issue en el repositorio.

## Disclaimer

Estos scripts modifican configuraciones del sistema. El autor no se hace responsable por cualquier daño o perdida de datos. Usa bajo tu propio riesgo y asegurate de tener backups.

## Recursos Adicionales

- [Documentacion oficial de Windows](https://docs.microsoft.com/windows)
- [Foros de Microsoft Community](https://answers.microsoft.com)
- [Subreddit de Windows11](https://reddit.com/r/Windows11)

---

**Hecho con atencion al detalle para mejorar PCs con recursos limitados**

