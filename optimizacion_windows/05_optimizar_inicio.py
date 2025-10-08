#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimizacion Windows 11 - Optimizar Inicio
Script para deshabilitar programas de inicio y acelerar el arranque
"""

import subprocess
import sys
import ctypes
import winreg

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

def mostrar_programas_inicio():
    """Muestra los programas que se ejecutan al inicio"""
    print("PROGRAMAS DE INICIO DETECTADOS...")
    print("-" * 70)
    print()
    
    try:
        # Ejecutar comando para listar programas de inicio
        result = subprocess.run(
            ["wmic", "startup", "get", "caption,command", "/format:list"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            lineas = result.stdout.strip().split('\n')
            programas = []
            programa_actual = {}
            
            for linea in lineas:
                linea = linea.strip()
                if not linea:
                    if programa_actual:
                        programas.append(programa_actual)
                        programa_actual = {}
                    continue
                
                if '=' in linea:
                    clave, valor = linea.split('=', 1)
                    programa_actual[clave.strip()] = valor.strip()
            
            if programa_actual:
                programas.append(programa_actual)
            
            if programas:
                print(f"Se encontraron {len(programas)} programas de inicio:")
                print()
                for i, prog in enumerate(programas, 1):
                    caption = prog.get('Caption', 'Sin nombre')
                    command = prog.get('Command', 'Sin comando')
                    print(f"{i}. {caption}")
                    print(f"   Comando: {command[:60]}...")
                    print()
            else:
                print("No se encontraron programas de inicio o estan deshabilitados")
                print()
        else:
            print(f"Error al listar programas: {result.stderr}")
            print()
        
    except Exception as e:
        print(f"ERROR: {e}")
        print()

def deshabilitar_inicio_rapido():
    """Deshabilita el inicio rapido de Windows"""
    print("CONFIGURANDO INICIO RAPIDO...")
    print("-" * 70)
    print()
    
    print("El inicio rapido en PCs con HDD puede causar problemas")
    print("Es mejor deshabilitarlo para evitar problemas de rendimiento")
    print()
    
    respuesta = input("Deshabilitar inicio rapido? (S/N): ").strip().upper()
    if respuesta != 'S':
        print("Inicio rapido mantenido")
        print()
        return
    
    try:
        # Deshabilitar inicio rapido
        result = subprocess.run(
            ["powercfg", "/hibernate", "off"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("  OK Inicio rapido deshabilitado")
        else:
            print(f"  ADVERTENCIA: {result.stderr}")
        print()
        
    except Exception as e:
        print(f"  ERROR: {e}")
        print()

def configurar_tiempo_boot():
    """Configura el tiempo de espera del menu de inicio"""
    print("CONFIGURANDO TIEMPO DE ESPERA DEL MENU DE INICIO...")
    print("-" * 70)
    print()
    
    try:
        print("Reduciendo tiempo de espera del menu de inicio a 3 segundos...")
        
        # Configurar timeout a 3 segundos
        result = subprocess.run(
            ["bcdedit", "/timeout", "3"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("  OK Tiempo de espera configurado a 3 segundos")
        else:
            print(f"  ADVERTENCIA: {result.stderr}")
        print()
        
    except Exception as e:
        print(f"  ERROR: {e}")
        print()

def abrir_administrador_tareas():
    """Abre el administrador de tareas en la pestaña de inicio"""
    print("ABRIENDO ADMINISTRADOR DE TAREAS...")
    print("-" * 70)
    print()
    
    print("Se abrira el Administrador de tareas para que puedas")
    print("deshabilitar manualmente los programas de inicio")
    print()
    print("INSTRUCCIONES:")
    print("  1. Ve a la pestaña 'Inicio'")
    print("  2. Selecciona los programas que NO necesitas al iniciar")
    print("  3. Haz clic derecho > 'Deshabilitar'")
    print()
    print("PROGRAMAS COMUNES A DESHABILITAR:")
    print("  - Microsoft Teams")
    print("  - OneDrive (si no lo usas)")
    print("  - Spotify")
    print("  - Discord")
    print("  - Adobe Creative Cloud")
    print("  - Cualquier programa que no necesites inmediatamente")
    print()
    
    respuesta = input("Abrir Administrador de tareas? (S/N): ").strip().upper()
    if respuesta != 'S':
        print("Administrador de tareas no abierto")
        print()
        return
    
    try:
        subprocess.Popen(["taskmgr", "/startup"])
        print("  OK Administrador de tareas abierto")
        print()
    except Exception as e:
        print(f"  ERROR: {e}")
        print()

def deshabilitar_cortana_inicio():
    """Deshabilita Cortana al inicio"""
    print("DESHABILITANDO CORTANA AL INICIO...")
    print("-" * 70)
    print()
    
    try:
        # Deshabilitar Cortana
        ruta = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
        
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, ruta, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "ShowCortanaButton", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        
        print("  OK Cortana deshabilitada en la barra de tareas")
        print()
        
    except Exception as e:
        print(f"  ERROR: {e}")
        print()

def deshabilitar_onedrive_inicio():
    """Deshabilita OneDrive al inicio"""
    print("DESHABILITANDO ONEDRIVE AL INICIO...")
    print("-" * 70)
    print()
    
    print("NOTA: OneDrive se puede deshabilitar desde el Administrador de tareas")
    print("Este script solo oculta el icono de OneDrive")
    print()
    
    try:
        # Ocultar icono de OneDrive
        ruta = r"Software\Microsoft\OneDrive"
        
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, ruta, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "DisableFileSyncNGSC", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
        
        print("  OK OneDrive configurado para no iniciarse")
        print()
        
    except Exception as e:
        print(f"  ADVERTENCIA: {e}")
        print()

def main():
    """Funcion principal"""
    print("=" * 70)
    print("OPTIMIZACION WINDOWS 11 - OPTIMIZAR INICIO")
    print("=" * 70)
    print()
    print("Este script optimizara el inicio de Windows deshabilitando")
    print("programas innecesarios que se ejecutan al arrancar el sistema.")
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
    
    respuesta = input("Continuar con la optimizacion de inicio? (S/N): ").strip().upper()
    if respuesta != 'S':
        print("Optimizacion cancelada")
        input("Presiona Enter para salir...")
        sys.exit(0)
    
    print()
    print("=" * 70)
    print("INICIANDO OPTIMIZACION DE INICIO...")
    print("=" * 70)
    print()
    
    # Mostrar programas de inicio
    mostrar_programas_inicio()
    
    # Deshabilitar inicio rapido
    deshabilitar_inicio_rapido()
    
    # Configurar tiempo de boot
    configurar_tiempo_boot()
    
    # Deshabilitar Cortana
    deshabilitar_cortana_inicio()
    
    # Deshabilitar OneDrive
    deshabilitar_onedrive_inicio()
    
    # Abrir administrador de tareas
    abrir_administrador_tareas()
    
    print("=" * 70)
    print("OPTIMIZACION DE INICIO COMPLETADA")
    print("=" * 70)
    print()
    print("IMPORTANTE: Revisa el Administrador de tareas y deshabilita")
    print("manualmente los programas que no necesites al inicio.")
    print()
    print("Se recomienda reiniciar el equipo para aplicar los cambios.")
    print()
    
    input("Presiona Enter para salir...")

if __name__ == "__main__":
    main()

