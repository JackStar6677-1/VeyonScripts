#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimizacion Windows 11 - Deshabilitar Servicios Innecesarios
Script para deshabilitar servicios que consumen recursos en PCs con 4GB RAM y HDD
"""

import subprocess
import sys
import ctypes

# Servicios innecesarios para PCs con recursos limitados
# IMPORTANTE: Solo deshabilita servicios que NO son criticos para el sistema
SERVICIOS_DESHABILITAR = [
    # Servicios de telemetria y diagnostico
    ("DiagTrack", "Experiencias del usuario conectado y telemetria"),
    ("dmwappushservice", "Servicio de enrutamiento de mensajes de insercion WAP"),
    ("PcaSvc", "Servicio del Asistente para la compatibilidad de programas"),
    
    # Servicios de Xbox (si no usas Xbox)
    ("XblAuthManager", "Administrador de autenticacion de Xbox Live"),
    ("XblGameSave", "Servicio de guardado de juegos de Xbox Live"),
    ("XboxGipSvc", "Servicio de entrada de Xbox Accessory Management"),
    ("XboxNetApiSvc", "Servicio de red de Xbox Live"),
    
    # Servicios de Windows Search (consume mucho en HDD)
    ("WSearch", "Windows Search - Indexacion de archivos (consume mucho en HDD)"),
    
    # Servicios de actualizacion automatica de mapas
    ("MapsBroker", "Administrador de mapas descargados"),
    
    # Servicio de fax
    ("Fax", "Servicio de fax"),
    
    # Servicio de impresora (si no usas impresora)
    # ("Spooler", "Cola de impresion"),  # Comentado por si acaso usas impresora
    
    # Servicios de Bluetooth (si no usas Bluetooth)
    # ("bthserv", "Servicio de compatibilidad con Bluetooth"),  # Comentado por seguridad
    
    # Servicio de biometria (si no usas huella digital)
    ("WbioSrvc", "Servicio biometrico de Windows"),
    
    # Servicio de uso compartido de red domestica
    ("HomeGroupListener", "Escucha de grupo en el hogar"),
    ("HomeGroupProvider", "Proveedor de grupo en el hogar"),
    
    # Servicio de sincronizacion de hora (opcional)
    # ("W32Time", "Hora de Windows"),  # Comentado por si necesitas sincronizacion
]

# Servicios que se pueden cambiar a MANUAL (inicio solo cuando se necesiten)
SERVICIOS_MANUAL = [
    ("SysMain", "Superfetch/SysMain - Consume mucho en HDD"),
    ("wuauserv", "Windows Update - Cambiar a manual para controlar cuando actualizar"),
    ("WinDefend", "Windows Defender - Cambiar a manual (CUIDADO: reduce seguridad)"),
    ("TabletInputService", "Servicio de entrada de tableta y panel de escritura a mano"),
    ("RetailDemo", "Servicio de demostacion comercial"),
    ("RemoteRegistry", "Registro remoto"),
    ("RemoteAccess", "Enrutamiento y acceso remoto"),
]

def es_admin():
    """Verifica si el script se ejecuta con permisos de administrador"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def solicitar_admin():
    """Solicita permisos de administrador"""
    try:
        script_path = sys.executable
        params = ' '.join([f'"{arg}"' for arg in sys.argv])
        
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", script_path, params, None, 1
        )
        return True
    except Exception as e:
        print(f"Error al solicitar permisos de administrador: {e}")
        return False

def deshabilitar_servicio(nombre_servicio, descripcion):
    """Deshabilita un servicio de Windows"""
    try:
        print(f"Deshabilitando: {descripcion}")
        print(f"  Servicio: {nombre_servicio}")
        
        # Detener el servicio
        result = subprocess.run(
            ["sc", "stop", nombre_servicio],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Deshabilitar el servicio
        result = subprocess.run(
            ["sc", "config", nombre_servicio, "start=", "disabled"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"  OK Servicio deshabilitado")
            return True
        else:
            print(f"  ADVERTENCIA: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

def servicio_a_manual(nombre_servicio, descripcion):
    """Cambia un servicio a inicio manual"""
    try:
        print(f"Cambiando a MANUAL: {descripcion}")
        print(f"  Servicio: {nombre_servicio}")
        
        # Cambiar a inicio manual
        result = subprocess.run(
            ["sc", "config", nombre_servicio, "start=", "demand"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"  OK Servicio cambiado a manual")
            return True
        else:
            print(f"  ADVERTENCIA: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

def main():
    """Funcion principal"""
    print("=" * 70)
    print("OPTIMIZACION WINDOWS 11 - DESHABILITAR SERVICIOS")
    print("=" * 70)
    print()
    print("Este script deshabilitara servicios innecesarios para mejorar")
    print("el rendimiento en PCs con 4GB RAM y HDD")
    print()
    print("IMPORTANTE: Algunos servicios pueden ser necesarios para ti.")
    print("Lee la lista antes de continuar.")
    print()
    
    # Verificar permisos de administrador
    if not es_admin():
        print("ERROR: Se requieren permisos de administrador")
        print("Solicitando permisos...")
        if solicitar_admin():
            sys.exit(0)
        else:
            print("No se pudieron obtener permisos de administrador")
            input("Presiona Enter para salir...")
            sys.exit(1)
    
    # Mostrar lista de servicios a deshabilitar
    print("SERVICIOS A DESHABILITAR:")
    print("-" * 70)
    for nombre, desc in SERVICIOS_DESHABILITAR:
        print(f"  - {desc}")
    print()
    
    print("SERVICIOS A CAMBIAR A MANUAL:")
    print("-" * 70)
    for nombre, desc in SERVICIOS_MANUAL:
        print(f"  - {desc}")
    print()
    
    respuesta = input("Continuar con la optimizacion? (S/N): ").strip().upper()
    if respuesta != 'S':
        print("Optimizacion cancelada")
        input("Presiona Enter para salir...")
        sys.exit(0)
    
    print()
    print("=" * 70)
    print("DESHABILITANDO SERVICIOS...")
    print("=" * 70)
    print()
    
    deshabilitados = 0
    for nombre_servicio, descripcion in SERVICIOS_DESHABILITAR:
        if deshabilitar_servicio(nombre_servicio, descripcion):
            deshabilitados += 1
        print()
    
    print("=" * 70)
    print("CAMBIANDO SERVICIOS A MANUAL...")
    print("=" * 70)
    print()
    
    manuales = 0
    for nombre_servicio, descripcion in SERVICIOS_MANUAL:
        if servicio_a_manual(nombre_servicio, descripcion):
            manuales += 1
        print()
    
    print("=" * 70)
    print("OPTIMIZACION COMPLETADA")
    print("=" * 70)
    print()
    print(f"Servicios deshabilitados: {deshabilitados}/{len(SERVICIOS_DESHABILITAR)}")
    print(f"Servicios cambiados a manual: {manuales}/{len(SERVICIOS_MANUAL)}")
    print()
    print("IMPORTANTE: Reinicia el equipo para aplicar todos los cambios")
    print()
    
    input("Presiona Enter para salir...")

if __name__ == "__main__":
    main()

