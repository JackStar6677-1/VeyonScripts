#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimizacion Windows 11 - Optimizar Rendimiento Visual
Script para deshabilitar efectos visuales y optimizar el rendimiento grafico
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

def configurar_registro(ruta, nombre, valor, tipo=winreg.REG_DWORD):
    """Configura un valor en el registro de Windows"""
    try:
        # Abrir o crear la clave
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, ruta, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, nombre, 0, tipo, valor)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        # Si la clave no existe, crearla
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, ruta)
            winreg.SetValueEx(key, nombre, 0, tipo, valor)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"  ERROR creando clave: {e}")
            return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

def optimizar_efectos_visuales():
    """Optimiza los efectos visuales de Windows"""
    print("OPTIMIZANDO EFECTOS VISUALES...")
    print("-" * 70)
    print()
    
    # Ruta del registro para efectos visuales
    ruta_visual = r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects"
    
    optimizaciones = [
        # Deshabilitar animaciones
        (r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
         "TaskbarAnimations", 0, "Animaciones de barra de tareas"),
        
        # Deshabilitar transparencias
        (r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
         "EnableTransparency", 0, "Transparencia de ventanas"),
        
        # Optimizar para mejor rendimiento
        (r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects",
         "VisualFXSetting", 2, "Ajustar para mejor rendimiento"),
        
        # Deshabilitar sombras
        (r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
         "ListviewShadow", 0, "Sombras de ventanas"),
        
        # Deshabilitar animacion de minimizar/maximizar
        (r"Control Panel\Desktop\WindowMetrics",
         "MinAnimate", 0, "Animacion al minimizar/maximizar"),
        
        # Deshabilitar efectos al hacer clic
        (r"Software\Microsoft\Windows\CurrentVersion\Explorer\AdvancedVisualEffects",
         "AnimateMinMax", 0, "Efectos al hacer clic"),
    ]
    
    aplicadas = 0
    for ruta, nombre, valor, descripcion in optimizaciones:
        print(f"Aplicando: {descripcion}")
        if configurar_registro(ruta, nombre, valor):
            print(f"  OK")
            aplicadas += 1
        print()
    
    return aplicadas

def deshabilitar_widgets():
    """Deshabilita los widgets de Windows 11"""
    print("DESHABILITANDO WIDGETS DE WINDOWS 11...")
    print("-" * 70)
    print()
    
    # Deshabilitar widgets en el registro
    ruta = r"Software\Microsoft\Windows\CurrentVersion\Dsh"
    
    print("Deshabilitando panel de widgets")
    if configurar_registro(ruta, "IsWidgetsPanelEnabled", 0):
        print("  OK Widgets deshabilitados")
    else:
        print("  ADVERTENCIA: No se pudieron deshabilitar widgets")
    print()

def deshabilitar_chat():
    """Deshabilita el chat de Teams en la barra de tareas"""
    print("DESHABILITANDO CHAT DE TEAMS...")
    print("-" * 70)
    print()
    
    ruta = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
    
    print("Deshabilitando chat de Teams en barra de tareas")
    if configurar_registro(ruta, "TaskbarMn", 0):
        print("  OK Chat de Teams deshabilitado")
    else:
        print("  ADVERTENCIA: No se pudo deshabilitar chat")
    print()

def configurar_modo_oscuro():
    """Configura el modo oscuro (consume menos recursos)"""
    print("CONFIGURANDO MODO OSCURO...")
    print("-" * 70)
    print()
    
    ruta = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
    
    print("Activando modo oscuro (consume menos recursos graficos)")
    if configurar_registro(ruta, "AppsUseLightTheme", 0):
        print("  OK Modo oscuro activado para apps")
    
    if configurar_registro(ruta, "SystemUsesLightTheme", 0):
        print("  OK Modo oscuro activado para sistema")
    print()

def deshabilitar_busqueda_web():
    """Deshabilita la busqueda web desde el menu inicio"""
    print("DESHABILITANDO BUSQUEDA WEB EN MENU INICIO...")
    print("-" * 70)
    print()
    
    ruta = r"Software\Policies\Microsoft\Windows\Explorer"
    
    print("Deshabilitando busqueda web en menu inicio")
    if configurar_registro(ruta, "DisableSearchBoxSuggestions", 1):
        print("  OK Busqueda web deshabilitada")
    else:
        print("  ADVERTENCIA: No se pudo deshabilitar busqueda web")
    print()

def main():
    """Funcion principal"""
    print("=" * 70)
    print("OPTIMIZACION WINDOWS 11 - RENDIMIENTO VISUAL")
    print("=" * 70)
    print()
    print("Este script optimizara el rendimiento visual deshabilitando")
    print("efectos graficos innecesarios que consumen recursos.")
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
    
    respuesta = input("Continuar con la optimizacion visual? (S/N): ").strip().upper()
    if respuesta != 'S':
        print("Optimizacion cancelada")
        input("Presiona Enter para salir...")
        sys.exit(0)
    
    print()
    print("=" * 70)
    print("INICIANDO OPTIMIZACION VISUAL...")
    print("=" * 70)
    print()
    
    # Optimizar efectos visuales
    efectos_aplicados = optimizar_efectos_visuales()
    
    # Deshabilitar widgets
    deshabilitar_widgets()
    
    # Deshabilitar chat de Teams
    deshabilitar_chat()
    
    # Configurar modo oscuro
    configurar_modo_oscuro()
    
    # Deshabilitar busqueda web
    deshabilitar_busqueda_web()
    
    print("=" * 70)
    print("OPTIMIZACION VISUAL COMPLETADA")
    print("=" * 70)
    print()
    print(f"Optimizaciones visuales aplicadas: {efectos_aplicados}")
    print()
    print("IMPORTANTE: Reinicia el explorador de Windows o el equipo")
    print("para aplicar todos los cambios visuales.")
    print()
    print("Para reiniciar el explorador:")
    print("  1. Ctrl + Shift + Esc (Administrador de tareas)")
    print("  2. Buscar 'Explorador de Windows'")
    print("  3. Clic derecho > Reiniciar")
    print()
    
    respuesta = input("Reiniciar el explorador de Windows ahora? (S/N): ").strip().upper()
    if respuesta == 'S':
        try:
            subprocess.run(["taskkill", "/F", "/IM", "explorer.exe"], capture_output=True)
            subprocess.Popen("explorer.exe")
            print("Explorador de Windows reiniciado")
        except Exception as e:
            print(f"Error reiniciando explorador: {e}")
    
    input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()

