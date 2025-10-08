#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimizacion Windows 11 - Crear Punto de Restauracion
Script para crear un punto de restauracion antes de las optimizaciones
"""

import subprocess
import sys
import ctypes
from datetime import datetime

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

def verificar_restauracion_habilitada():
    """Verifica si la restauracion del sistema esta habilitada"""
    print("Verificando si la restauracion del sistema esta habilitada...")
    print()
    
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-ComputerRestorePoint | Select-Object -Last 1"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if "Error" in result.stderr or result.returncode != 0:
            print("ADVERTENCIA: La restauracion del sistema puede no estar habilitada")
            print()
            print("Para habilitar la restauracion del sistema:")
            print("  1. Buscar 'Crear punto de restauracion'")
            print("  2. Seleccionar unidad C: y clic en 'Configurar'")
            print("  3. Seleccionar 'Activar proteccion del sistema'")
            print("  4. Asignar espacio de disco (minimo 2%)")
            print("  5. Clic en 'Aceptar'")
            print()
            return False
        else:
            print("OK La restauracion del sistema esta habilitada")
            print()
            return True
            
    except Exception as e:
        print(f"Error verificando restauracion: {e}")
        print()
        return False

def crear_punto_restauracion():
    """Crea un punto de restauracion del sistema"""
    print("CREANDO PUNTO DE RESTAURACION...")
    print("-" * 70)
    print()
    
    try:
        # Obtener fecha y hora actual
        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M")
        descripcion = f"Optimizacion Windows 11 - {fecha_hora}"
        
        print(f"Descripcion: {descripcion}")
        print("Esto puede tardar varios minutos...")
        print()
        
        # Crear punto de restauracion usando PowerShell
        comando = f'Checkpoint-Computer -Description "{descripcion}" -RestorePointType "MODIFY_SETTINGS"'
        
        result = subprocess.run(
            ["powershell", "-Command", comando],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos
        )
        
        if result.returncode == 0:
            print("OK Punto de restauracion creado exitosamente")
            print()
            return True
        else:
            print(f"ERROR: {result.stderr}")
            print()
            return False
            
    except subprocess.TimeoutExpired:
        print("ERROR: El proceso tardo demasiado tiempo")
        print()
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        print()
        return False

def listar_puntos_restauracion():
    """Lista los puntos de restauracion existentes"""
    print("PUNTOS DE RESTAURACION EXISTENTES:")
    print("-" * 70)
    print()
    
    try:
        result = subprocess.run(
            ["powershell", "-Command", 
             "Get-ComputerRestorePoint | Format-Table SequenceNumber, CreationTime, Description -AutoSize"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout.strip():
            print(result.stdout)
        else:
            print("No se encontraron puntos de restauracion")
            print()
            
    except Exception as e:
        print(f"Error listando puntos: {e}")
        print()

def main():
    """Funcion principal"""
    print("=" * 70)
    print("CREAR PUNTO DE RESTAURACION")
    print("=" * 70)
    print()
    print("Este script creara un punto de restauracion del sistema")
    print("antes de ejecutar las optimizaciones.")
    print()
    print("IMPORTANTE: Esto permite revertir los cambios si algo sale mal.")
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
    
    # Listar puntos existentes
    listar_puntos_restauracion()
    
    # Verificar si la restauracion esta habilitada
    if not verificar_restauracion_habilitada():
        respuesta = input("Continuar de todos modos? (S/N): ").strip().upper()
        if respuesta != 'S':
            print("Operacion cancelada")
            input("Presiona Enter para salir...")
            sys.exit(0)
    
    print()
    respuesta = input("Crear punto de restauracion ahora? (S/N): ").strip().upper()
    if respuesta != 'S':
        print("Operacion cancelada")
        input("Presiona Enter para salir...")
        sys.exit(0)
    
    print()
    print("=" * 70)
    print("CREANDO PUNTO DE RESTAURACION...")
    print("=" * 70)
    print()
    
    if crear_punto_restauracion():
        print("=" * 70)
        print("PUNTO DE RESTAURACION CREADO")
        print("=" * 70)
        print()
        print("Ahora puedes ejecutar los scripts de optimizacion con seguridad.")
        print()
        print("Para restaurar el sistema si algo sale mal:")
        print("  1. Buscar 'Crear punto de restauracion'")
        print("  2. Clic en 'Restaurar sistema'")
        print("  3. Seleccionar el punto creado")
        print("  4. Seguir el asistente")
        print()
    else:
        print("=" * 70)
        print("ERROR AL CREAR PUNTO DE RESTAURACION")
        print("=" * 70)
        print()
        print("No se pudo crear el punto de restauracion.")
        print("Puedes continuar con las optimizaciones bajo tu propio riesgo")
        print("o crear el punto de restauracion manualmente.")
        print()
    
    input("Presiona Enter para salir...")

if __name__ == "__main__":
    main()

