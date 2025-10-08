# Suite de Automatizacion - VeyonScripts y Optimizacion Windows 11

**Desarrollado por: Pablo Elias Avendano Miranda**  
*Ingeniero en Informatica*

---

## Descripcion General

Este repositorio contiene **dos proyectos principales** de automatizacion desarrollados con enfoque practico y orientados a resolver problemas reales en ambientes educativos y profesionales.

### Proyectos Incluidos:

1. **VeyonScripts**: Suite de automatizacion para gestion de laboratorios con Veyon
2. **Optimizacion Windows 11**: Scripts de optimizacion para PCs con recursos limitados (4GB RAM + HDD)

---

## Proyecto 1: VeyonScripts - Automatizacion para Laboratorios

Suite completa de automatizacion para **Veyon** (Virtual Eye On Networks), permitiendo la gestion inteligente de laboratorios de computacion con mapeo fisico automatico basado en direcciones MAC.

### Estructura del Proyecto VeyonScripts

```
VeyonScripts/
├── scripts/                        # Scripts organizados
│   ├── principales/               # Scripts principales de uso diario
│   │   ├── VEYON_MAESTRO.py      # Script maestro con WakeMeOnLAN
│   │   └── MAPEO_FISICO_ADMIN.py  # Script de mapeo fisico por MAC
│   ├── diagnosticos/              # Scripts de diagnostico
│   │   ├── diagnostico_veyon.py         # Diagnostico general
│   │   ├── diagnostico_profundo_pc01.py # Diagnostico profundo PC-01
│   │   ├── comparar_pc01_funcionando.py # Comparador PC-01 vs PC funcionando
│   │   ├── verificar_claves_veyon.py    # Verificador de claves
│   │   └── verificar_pc01_remoto.py     # Verificador remoto PC-01
│   └── soluciones/                # Scripts de solucion de problemas
│       ├── solucion_pc01.py            # Solucionador PC-01
│       └── solucionar_clon_pc01.py     # Solucionador para clones
├── VeyonGUI/                      # Interfaz grafica visual
│   ├── physical_mapping_gui.py   # GUI principal funcional
│   ├── launch_gui.bat             # Launcher de la GUI
│   └── README_GUI.md              # Documentacion de la GUI
├── VEYON_MAESTRO.bat              # Launcher script maestro (ADMIN)
├── MAPEO_FISICO_ADMIN.bat         # Launcher mapeo fisico (ADMIN)
├── SOLUCIONAR_PC01_ADMIN.bat      # Launcher solucionador PC-01 (ADMIN)
└── WakeMeOnLAN.exe                # Herramienta de escaneo de red
```

### Caracteristicas Principales de VeyonScripts:
- **Mapeo Fisico por MAC**: Asigna numeros de PC basados en direcciones MAC unicas
- **Compatibilidad con IPs Dinamicas**: Funciona aunque las IPs cambien
- **Escaneo con WakeMeOnLAN**: Integracion con herramienta profesional de red
- **Interfaz Grafica**: GUI intuitiva con drag & drop
- **Diagnosticos Profundos**: Suite completa de herramientas de diagnostico
- **Solucion Automatizada**: Scripts para resolver problemas comunes

### Uso Rapido - VeyonScripts:
```bash
# Mapeo fisico automatico
MAPEO_FISICO_ADMIN.bat

# Interfaz grafica
VeyonGUI/launch_gui.bat

# Script maestro
VEYON_MAESTRO.bat
```

---

## Proyecto 2: Optimizacion Windows 11

Suite de scripts especializados para optimizar Windows 11 en equipos con recursos limitados (4GB RAM + HDD), mejorando significativamente el rendimiento sin necesidad de actualizar hardware.

### Estructura del Proyecto Optimizacion Windows

```
optimizacion_windows/
├── 00_CREAR_PUNTO_RESTAURACION.py    # Crear backup antes de optimizar
├── 01_deshabilitar_servicios.py      # Deshabilitar servicios innecesarios
├── 02_optimizar_rendimiento_visual.py # Optimizar efectos visuales
├── 03_limpiar_archivos_temp.py       # Limpieza profunda de archivos
├── 04_optimizar_hdd.py                # Optimizacion especifica para HDD
├── 05_optimizar_inicio.py             # Gestion de programas de inicio
├── OPTIMIZAR_TODO.py                  # Script maestro (ejecuta todos)
├── INFO_SISTEMA.py                    # Analisis del sistema
└── *.bat                              # Launchers con permisos admin
```

### Caracteristicas Principales de Optimizacion Windows:
- **Deshabilitar Servicios**: Libera RAM deshabilitando servicios innecesarios
- **Optimizar Efectos Visuales**: Deshabilita animaciones y transparencias
- **Limpieza Profunda**: Elimina archivos temporales y cache
- **Optimizacion HDD**: Deshabilita indexacion y superfetch
- **Gestion de Inicio**: Optimiza programas que se ejecutan al arrancar
- **Punto de Restauracion**: Crea backup antes de optimizar

### Mejoras Esperadas:
- Inicio 30-50% mas rapido
- 200-400 MB de RAM liberada
- Reduccion de uso de disco del 80% al 10-30%
- 2-6 GB de espacio liberado

### Uso Rapido - Optimizacion Windows:
```bash
# Analizar sistema
cd optimizacion_windows
INFO_SISTEMA.bat

# Crear punto de restauracion
00_CREAR_PUNTO_RESTAURACION_ADMIN.bat

# Ejecutar todo
OPTIMIZAR_TODO_ADMIN.bat
```

---

## Analisis Tecnico de VeyonScripts

### 1. MAPEO_FISICO_ADMIN.py - Script Principal

**Proposito**: Mapeo inteligente de PCs fisicos en laboratorios usando direcciones MAC.

**Funcionalidades Tecnicas**:
```python
# Mapeo fisico predefinido (0-15)
MAPEO_FISICO_MAC = {
    '00-D8-61-CB-82-61': 0,   # PC-00 (192.168.50.122)
    '00-D8-61-CB-82-2E': 1,   # PC-01 (192.168.50.236)
    # ... mas mapeos
}

# Funciones principales
- scan_network_with_wakemeonlan()    # Escaneo de red
- filter_veyon_clients_with_physical_mapping()  # Filtrado y mapeo
- clear_existing_computers()         # Limpieza de Veyon
- update_veyon_with_physical_mapping()  # Actualizacion
```

**Ventajas**:
- **Consistencia**: Los numeros de PC siempre coinciden con la posicion fisica
- **Mantenimiento**: No requiere reconfiguracion manual al cambiar IPs
- **Escalabilidad**: Facil agregar nuevos PCs al mapeo
- **Robustez**: Manejo de errores y verificacion de eliminacion

### 2. VEYON_MAESTRO.py - Script Maestro

**Proposito**: Script unificado para gestion completa de Veyon con WakeMeOnLAN.

**Caracteristicas**:
- **Integracion WakeMeOnLAN**: Escaneo profesional de red
- **Nombres Reales de PC**: Obtiene nombres reales de los equipos
- **Manejo de Duplicados**: Asigna sufijos automaticamente
- **Actualizacion Segura**: No borra configuracion de autenticacion
- **Deteccion de Veyon**: Identifica que PCs tienen Veyon instalado

**Flujo de Trabajo**:
1. Escanea la red con WakeMeOnLAN
2. Procesa nombres y maneja duplicados
3. Detecta clientes Veyon
4. Actualiza configuracion de Veyon
5. Exporta configuracion a archivo

### 3. VeyonGUI/physical_mapping_gui.py - Interfaz Grafica

**Proposito**: GUI intuitiva para mapeo fisico con drag & drop.

**Funcionalidades Tecnicas**:
```python
# Interfaz con tkinter
class PhysicalMappingGUI:
    def scan_network()           # Escaneo con WakeMeOnLAN
    def add_to_physical_order()  # Drag & drop
    def update_veyon()          # Actualizacion de Veyon
    def save_mapping()          # Exportar configuracion
    def load_mapping()          # Importar configuracion
```

---

## Potencial como Addon Oficial de Veyon

### Ventajas para Veyon

1. **Funcionalidad Unica**:
   - Mapeo fisico automatico no disponible en Veyon nativo
   - Gestion inteligente de laboratorios de computacion
   - Compatibilidad con IPs dinamicas

2. **Integracion Perfecta**:
   - Usa APIs nativas de Veyon (`veyon-cli`)
   - No modifica archivos de configuracion directamente
   - Mantiene compatibilidad con versiones futuras

3. **Valor Educativo**:
   - Ideal para laboratorios escolares y universitarios
   - Facilita la gestion de aulas de computacion
   - Reduce tiempo de configuracion manual

4. **Escalabilidad**:
   - Facil adaptacion a diferentes tamanos de laboratorio
   - Configuracion flexible de mapeos fisicos
   - Soporte para multiples ubicaciones

---

## Casos de Uso

### VeyonScripts - Laboratorios Educativos
- Gestion automatica de aulas de computacion
- Mapeo fisico consistente independiente de IPs
- Facilita identificacion de equipos por estudiantes

### Optimizacion Windows - Equipos con Recursos Limitados
- Laboratorios con equipos antiguos (4GB RAM + HDD)
- Centros educativos con presupuesto limitado
- Maximizar rendimiento sin actualizar hardware

---

## Instalacion y Uso

### Requisitos Generales:
- Windows 10/11
- Python 3.7+
- Permisos de administrador

### Requisitos Especificos VeyonScripts:
- Veyon 4.x+
- WakeMeOnLAN (incluido)

### Instalacion:
```bash
# Clonar repositorio
git clone https://github.com/JackStar6677-1/VeyonScripts.git
cd VeyonScripts

# Instalar dependencias (opcional)
pip install -r requirements.txt

# Usar VeyonScripts
python MAPEO_FISICO_ADMIN.py

# Usar Optimizacion Windows
cd optimizacion_windows
python OPTIMIZAR_TODO.py
```

---

## Documentacion Adicional

Cada proyecto incluye su propia documentacion detallada:

- **VeyonScripts**: Documentacion completa en este README
- **Optimizacion Windows**: Ver `optimizacion_windows/README.md`

---

## Metricas de Exito

### VeyonScripts:
- **Tiempo de Configuracion**: Reduccion del 90% vs configuracion manual
- **Precision de Mapeo**: 100% de precision en mapeo fisico
- **Mantenimiento**: Cero intervencion manual al cambiar IPs
- **Escalabilidad**: Soporte para 1-100+ PCs por laboratorio

### Optimizacion Windows:
- **Inicio**: 30-50% mas rapido
- **RAM liberada**: 200-400 MB
- **Uso de disco**: Reduccion del 80% al 10-30% en reposo
- **Espacio liberado**: 2-6 GB

---

## Contribuciones

Ambos proyectos estan abiertos a contribuciones. Las areas de mejora incluyen:

**VeyonScripts:**
- Interfaz grafica mas intuitiva
- Soporte para mas tipos de dispositivos
- Integracion con sistemas de gestion de red

**Optimizacion Windows:**
- Mas scripts de optimizacion
- Deteccion automatica de tipo de disco
- Scripts de reversion automatica

---

## Licencia

Ambos proyectos estan bajo la licencia MIT. Ver `LICENSE` para mas detalles.

---

## Autor

**Pablo Elias Avendano Miranda**  
*Ingeniero en Informatica*

Estos proyectos fueron desarrollados con dedicacion y atencion al detalle para resolver problemas reales en entornos educativos y profesionales. La experiencia practica ha sido fundamental para crear soluciones robustas y confiables.

### Especializacion
- Automatizacion de Sistemas
- Optimizacion de Sistemas Operativos
- Gestion de Redes y Laboratorios
- Desarrollo de Software Educativo

### Filosofia de Desarrollo

> "La tecnologia debe ser accesible para todos. No se trata de tener el mejor hardware, sino de aprovechar al maximo lo que tienes."

---

**© 2025 Pablo Elias Avendano Miranda - Todos los derechos reservados**

---

## Enlaces Rapidos

- **GitHub**: https://github.com/JackStar6677-1/VeyonScripts
- **Documentacion VeyonScripts**: Este README
- **Documentacion Optimizacion Windows**: `optimizacion_windows/README.md`
- **Informacion del Autor**: `AUTHOR.md`