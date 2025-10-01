# Veyon GUI - Mapeo Físico Visual

## 🎯 **Descripción**

Interfaz gráfica intuitiva para el mapeo físico de PCs en laboratorios de computación. Permite escanear la red automáticamente y luego organizar visualmente el orden físico de los equipos mediante drag & drop.

## 🚀 **Características Principales**

### ✅ **Escaneo Automático**
- Escanea la red usando WakeMeOnLAN
- Detecta automáticamente IPs, MACs y nombres de PC
- Identifica qué equipos tienen Veyon instalado
- Muestra estado de conexión en tiempo real

### ✅ **Organización Visual**
- **Drag & Drop**: Arrastra dispositivos desde la lista de escaneados al orden físico
- **Interfaz Intuitiva**: Dos paneles claramente separados
- **Orden Personalizable**: Organiza los PCs según el orden físico real de la sala
- **Numeración Automática**: Asigna PC-00, PC-01, PC-02, etc. automáticamente

### ✅ **Gestión de Mapeos**
- **Guardar Mapeos**: Exporta configuraciones a archivos JSON
- **Cargar Mapeos**: Importa configuraciones guardadas
- **Reutilización**: Aplica el mismo mapeo en diferentes sesiones

### ✅ **Integración con Veyon**
- **Actualización Automática**: Actualiza Veyon con el orden físico configurado
- **Limpieza Inteligente**: Elimina computadoras existentes antes de actualizar
- **Verificación**: Confirma que la actualización fue exitosa

## 🖥️ **Interfaz de Usuario**

### **Panel Izquierdo - Dispositivos Detectados**
```
┌─────────────────────────────────────────┐
│ Dispositivos Detectados                 │
├─────────────────────────────────────────┤
│ 192.168.50.122 | 00-D8-61-CB-82-61 |   │
│ SCA-PC01       | ✓ VEYON             │   │
├─────────────────────────────────────────┤
│ 192.168.50.222 | 00-D8-61-CB-94-32 |   │
│ SCA-PC02       | ✓ VEYON             │   │
└─────────────────────────────────────────┘
```

### **Panel Derecho - Orden Físico**
```
┌─────────────────────────────────────────┐
│ Orden Físico (Arrastra para organizar)  │
├─────────────────────────────────────────┤
│ ┌─────────────────────────────────────┐ │
│ │ PC-00: 192.168.50.122              │ │
│ └─────────────────────────────────────┘ │
│ ┌─────────────────────────────────────┐ │
│ │ PC-01: 192.168.50.222              │ │
│ └─────────────────────────────────────┘ │
│ ┌─────────────────────────────────────┐ │
│ │ PC-02: 192.168.50.34               │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## 🎮 **Cómo Usar**

### **Paso 1: Escanear Red**
1. Haz clic en **"🔍 Escanear Red"**
2. El programa escaneará automáticamente la red
3. Los dispositivos aparecerán en el panel izquierdo

### **Paso 2: Organizar Orden Físico**
1. **Arrastra** cada dispositivo desde el panel izquierdo al panel derecho
2. Organiza los dispositivos en el orden físico real de la sala
3. El programa asignará automáticamente PC-00, PC-01, PC-02, etc.

### **Paso 3: Actualizar Veyon**
1. Haz clic en **"💾 Actualizar Veyon"**
2. El programa actualizará la configuración de Veyon
3. Los PCs aparecerán en Veyon Master con el orden físico correcto

### **Paso 4: Guardar Mapeo (Opcional)**
1. Haz clic en **"💾 Guardar Mapeo"** para exportar la configuración
2. Usa **"📁 Cargar Mapeo"** para importar configuraciones guardadas

## 🔧 **Requisitos del Sistema**

### **Software Requerido**
- **Python 3.7+** con tkinter
- **Veyon 4.x+** instalado
- **WakeMeOnLAN** (incluido en el proyecto)

### **Permisos**
- **Administrador**: Requerido para actualizar Veyon
- **Red**: Acceso a la red local para escaneo

## 📁 **Estructura de Archivos**

```
VeyonGUI/
├── physical_mapping_gui.py    # Aplicación principal
├── launch_gui.bat            # Launcher con verificaciones
├── README_GUI.md             # Este archivo
└── WakeMeOnLAN.exe           # Herramienta de escaneo (opcional)
```

## 🚀 **Instalación y Uso**

### **Instalación Rápida**
1. Copia la carpeta `VeyonGUI` a tu sistema
2. Ejecuta `launch_gui.bat`
3. ¡Listo para usar!

### **Uso Avanzado**
```bash
# Ejecutar directamente con Python
python physical_mapping_gui.py
```

## 🎯 **Casos de Uso**

### **Laboratorios Educativos**
- **Configuración Inicial**: Mapea todos los PCs de la sala
- **Reorganización**: Cambia el orden cuando se mueven equipos
- **Mantenimiento**: Actualiza después de cambios de red

### **Centros de Capacitación**
- **Múltiples Salas**: Diferentes mapeos para diferentes salas
- **Plantillas**: Guarda configuraciones para reutilizar
- **Flexibilidad**: Adapta el mapeo según necesidades

### **Empresas**
- **Auditoría**: Identifica todos los dispositivos de red
- **Gestión**: Mantiene inventario actualizado de equipos
- **Control**: Monitorea estado de equipos Veyon

## 🔍 **Funcionalidades Técnicas**

### **Escaneo de Red**
- Usa WakeMeOnLAN para detección profesional
- Identifica IPs, MACs y nombres de PC
- Detecta puerto 11100 para verificar Veyon
- Maneja timeouts y errores de red

### **Drag & Drop**
- Implementación nativa con tkinter
- Feedback visual durante el arrastre
- Validación de posiciones de caída
- Actualización automática del canvas

### **Integración Veyon**
- Usa `veyon-cli` para todas las operaciones
- Comandos seguros que no afectan autenticación
- Verificación de eliminación de computadoras
- Manejo de errores robusto

## 🛠️ **Personalización**

### **Configuración de Red**
```python
# Modificar rangos de escaneo en el código
ip_ranges = ["192.168.50.1-254", "192.168.56.1-254"]
```

### **Estilos Visuales**
```python
# Colores personalizables
colors = {
    'primary': '#3498db',
    'success': '#27ae60',
    'warning': '#f39c12',
    'danger': '#e74c3c'
}
```

## 🐛 **Solución de Problemas**

### **Error: "WakeMeOnLAN no encontrado"**
- Verifica que `WakeMeOnLAN.exe` esté en la carpeta
- O instala WakeMeOnLAN en el sistema

### **Error: "Veyon no encontrado"**
- Verifica que Veyon esté instalado en `C:\Program Files\Veyon\`
- O modifica la ruta en el código

### **Error: "No se pueden actualizar computadoras"**
- Ejecuta como administrador
- Verifica que Veyon esté funcionando
- Revisa los permisos de red

## 📈 **Próximas Mejoras**

- [ ] **Múltiples Ubicaciones**: Soporte para varias salas
- [ ] **Plantillas**: Sistema de plantillas predefinidas
- [ ] **Validación**: Verificación de mapeos duplicados
- [ ] **Estadísticas**: Reportes de uso y estado
- [ ] **Temas**: Múltiples temas visuales

## 🤝 **Contribuciones**

Este proyecto está abierto a contribuciones. Las áreas de mejora incluyen:

- Mejoras en la interfaz de usuario
- Nuevas funcionalidades de escaneo
- Integración con más herramientas de red
- Optimizaciones de rendimiento

## 📄 **Licencia**

Este proyecto está bajo la licencia MIT. Ver `LICENSE` para más detalles.

---

**¡Disfruta organizando tus laboratorios de computación de manera visual e intuitiva!** 🎉

