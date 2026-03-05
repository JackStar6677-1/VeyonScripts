#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimizacion Windows 11 - Script Maestro
Ejecuta todos los scripts de optimizacion en orden
"""

import subprocess
import sys
import ctypes
import os

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

def ejecutar_script(ruta_script, nombre):
    """Ejecuta un script de optimizacion"""
    print()
    print("=" * 70)
    print(f"EJECUTANDO: {nombre}")
    print("=" * 70)
    print()
    
    try:
        resultado = subprocess.run([sys.executable, ruta_script], timeout=600)
        
        if resultado.returncode == 0:
            print(f"\nOK {nombre} completado exitosamente")
            return True
        else:
            print(f"\nADVERTENCIA: {nombre} finalizo con errores")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"\nADVERTENCIA: {nombre} tardo demasiado tiempo")
        return False
    except Exception as e:
        print(f"\nERROR ejecutando {nombre}: {e}")
        return False

def main():
    """Funcion principal"""
    print("=" * 70)
    print("OPTIMIZACION COMPLETA DE WINDOWS 11")
    print("=" * 70)
    print()
    print("Este script ejecutara TODOS los scripts de optimizacion en orden:")
    print()
    print("1. Deshabilitar servicios innecesarios")
    print("2. Optimizar rendimiento visual")
    print("3. Limpiar archivos temporales")
    print("4. Optimizar disco duro (HDD)")
    print("5. Optimizar programas de inicio")
    print()
    print("ADVERTENCIA: Este proceso puede tardar bastante tiempo")
    print("y requiere reiniciar el equipo al finalizar.")
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
    
    respuesta = input("Continuar con la optimizacion completa? (S/N): ").strip().upper()
    if respuesta != 'S':
        print("Optimizacion cancelada")
        input("Presiona Enter para salir...")
        sys.exit(0)
    
    # Obtener directorio del script
    directorio = os.path.dirname(os.path.abspath(__file__))
    
    # Lista de scripts a ejecutar
    scripts = [
        ("01_deshabilitar_servicios.py", "Deshabilitar Servicios"),
        ("02_optimizar_rendimiento_visual.py", "Optimizar Rendimiento Visual"),
        ("03_limpiar_archivos_temp.py", "Limpiar Archivos Temporales"),
        ("04_optimizar_hdd.py", "Optimizar HDD"),
        ("05_optimizar_inicio.py", "Optimizar Inicio"),
    ]
    
    completados = 0
    
    for script, nombre in scripts:
        ruta_script = os.path.join(directorio, script)
        
        if not os.path.exists(ruta_script):
            print(f"\nADVERTENCIA: No se encontro {script}")
            continue
        
        if ejecutar_script(ruta_script, nombre):
            completados += 1
        
        print()
        input("Presiona Enter para continuar con el siguiente script...")
    
    print()
    print("=" * 70)
    print("OPTIMIZACION COMPLETA FINALIZADA")
    print("=" * 70)
    print()
    print(f"Scripts completados: {completados}/{len(scripts)}")
    print()
    print("IMPORTANTE: Se recomienda REINICIAR EL EQUIPO ahora")
    print("para aplicar todos los cambios.")
    print()
    
    respuesta = input("Reiniciar el equipo ahora? (S/N): ").strip().upper()
    if respuesta == 'S':
        print("Reiniciando equipo en 10 segundos...")
        print("Presiona Ctrl+C para cancelar")
        try:
            subprocess.run(["shutdown", "/r", "/t", "10"], timeout=15)
        except KeyboardInterrupt:
            print("\nReinicio cancelado")
        except Exception as e:
            print(f"Error al reiniciar: {e}")
    
    input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()

