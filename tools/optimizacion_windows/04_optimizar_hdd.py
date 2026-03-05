#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimizacion Windows 11 - Optimizar HDD
Script para optimizar el rendimiento del disco duro mecanico
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

def deshabilitar_superfetch():
    """Deshabilita Superfetch/SysMain (consume mucho en HDD)"""
    print("DESHABILITANDO SUPERFETCH/SYSMAIN...")
    print("-" * 70)
    print()
    
    try:
        print("SysMain/Superfetch consume muchos recursos en HDD")
        print("Deshabilitando servicio...")
        
        # Detener servicio
        subprocess.run(["sc", "stop", "SysMain"], capture_output=True, timeout=30)
        
        # Deshabilitar servicio
        result = subprocess.run(
            ["sc", "config", "SysMain", "start=", "disabled"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("  OK SysMain deshabilitado")
        else:
            print(f"  ADVERTENCIA: {result.stderr}")
        print()
        
    except Exception as e:
        print(f"  ERROR: {e}")
        print()

def deshabilitar_indexacion():
    """Deshabilita la indexacion de Windows Search"""
    print("DESHABILITANDO INDEXACION DE WINDOWS SEARCH...")
    print("-" * 70)
    print()
    
    try:
        print("Windows Search indexa archivos constantemente")
        print("Esto consume muchos recursos en HDD lentos")
        print("Deshabilitando servicio...")
        
        # Detener servicio
        subprocess.run(["sc", "stop", "WSearch"], capture_output=True, timeout=30)
        
        # Deshabilitar servicio
        result = subprocess.run(
            ["sc", "config", "WSearch", "start=", "disabled"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("  OK Windows Search deshabilitado")
        else:
            print(f"  ADVERTENCIA: {result.stderr}")
        print()
        
    except Exception as e:
        print(f"  ERROR: {e}")
        print()

def configurar_modo_energia():
    """Configura el modo de energia para mejor rendimiento"""
    print("CONFIGURANDO MODO DE ENERGIA...")
    print("-" * 70)
    print()
    
    try:
        print("Configurando plan de energia de alto rendimiento...")
        
        # Activar plan de alto rendimiento
        result = subprocess.run(
            ["powercfg", "/setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("  OK Plan de alto rendimiento activado")
        else:
            print(f"  ADVERTENCIA: {result.stderr}")
        
        # Deshabilitar suspension del disco
        print("Deshabilitando suspension del disco duro...")
        subprocess.run(
            ["powercfg", "/change", "disk-timeout-ac", "0"],
            capture_output=True,
            timeout=30
        )
        subprocess.run(
            ["powercfg", "/change", "disk-timeout-dc", "0"],
            capture_output=True,
            timeout=30
        )
        print("  OK Suspension del disco deshabilitada")
        print()
        
    except Exception as e:
        print(f"  ERROR: {e}")
        print()

def optimizar_archivo_paginacion():
    """Optimiza la configuracion del archivo de paginacion"""
    print("OPTIMIZANDO ARCHIVO DE PAGINACION...")
    print("-" * 70)
    print()
    
    print("RECOMENDACION para 4GB de RAM:")
    print("  - Tamaño inicial: 6144 MB (1.5x RAM)")
    print("  - Tamaño maximo: 8192 MB (2x RAM)")
    print()
    print("NOTA: El archivo de paginacion se debe configurar manualmente:")
    print("  1. Panel de Control > Sistema > Configuracion avanzada del sistema")
    print("  2. Pestaña 'Opciones avanzadas' > Rendimiento > Configuracion")
    print("  3. Pestaña 'Opciones avanzadas' > Memoria virtual > Cambiar")
    print("  4. Desmarcar 'Administrar automaticamente el tamaño'")
    print("  5. Seleccionar 'Tamaño personalizado'")
    print("  6. Establecer tamaño inicial: 6144 MB")
    print("  7. Establecer tamaño maximo: 8192 MB")
    print("  8. Clic en 'Establecer' y luego 'Aceptar'")
    print("  9. Reiniciar el equipo")
    print()

def deshabilitar_hibernacion():
    """Deshabilita la hibernacion para liberar espacio"""
    print("DESHABILITANDO HIBERNACION...")
    print("-" * 70)
    print()
    
    try:
        print("La hibernacion crea un archivo del tamaño de la RAM")
        print("En equipos con 4GB, esto ocupa 4GB de espacio en disco")
        print()
        
        respuesta = input("Deshabilitar hibernacion? (S/N): ").strip().upper()
        if respuesta != 'S':
            print("Hibernacion mantenida")
            print()
            return
        
        # Deshabilitar hibernacion
        result = subprocess.run(
            ["powercfg", "/hibernate", "off"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("  OK Hibernacion deshabilitada")
            print("  Se liberaron aproximadamente 4GB de espacio")
        else:
            print(f"  ADVERTENCIA: {result.stderr}")
        print()
        
    except Exception as e:
        print(f"  ERROR: {e}")
        print()

def ejecutar_chkdsk():
    """Programa la ejecucion de chkdsk en el siguiente reinicio"""
    print("PROGRAMANDO VERIFICACION DE DISCO...")
    print("-" * 70)
    print()
    
    try:
        print("Se programara una verificacion del disco en el siguiente reinicio")
        print("Esto puede tardar bastante tiempo dependiendo del tamaño del disco")
        print()
        
        respuesta = input("Programar chkdsk para el siguiente reinicio? (S/N): ").strip().upper()
        if respuesta != 'S':
            print("Verificacion de disco no programada")
            print()
            return
        
        # Programar chkdsk
        result = subprocess.run(
            ["chkdsk", "C:", "/F", "/R"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print("  OK Verificacion programada para el siguiente reinicio")
        print("  El equipo se reiniciara y ejecutara chkdsk automaticamente")
        print()
        
    except Exception as e:
        print(f"  ERROR: {e}")
        print()

def desfragmentar_disco():
    """Programa la desfragmentacion del disco"""
    print("DESFRAGMENTACION DE DISCO...")
    print("-" * 70)
    print()
    
    try:
        print("La desfragmentacion mejora el rendimiento del HDD")
        print("NOTA: Esto puede tardar varias horas dependiendo del tamaño")
        print()
        
        respuesta = input("Iniciar desfragmentacion ahora? (S/N): ").strip().upper()
        if respuesta != 'S':
            print("Desfragmentacion no iniciada")
            print()
            return
        
        print("Iniciando desfragmentacion...")
        print("ESTO PUEDE TARDAR VARIAS HORAS")
        print()
        
        # Iniciar desfragmentacion
        subprocess.Popen(
            ["defrag", "C:", "/U", "/V"],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        print("  OK Desfragmentacion iniciada en una nueva ventana")
        print("  Puedes cerrar este script, la desfragmentacion continuara")
        print()
        
    except Exception as e:
        print(f"  ERROR: {e}")
        print()

def main():
    """Funcion principal"""
    print("=" * 70)
    print("OPTIMIZACION WINDOWS 11 - OPTIMIZAR HDD")
    print("=" * 70)
    print()
    print("Este script optimizara el rendimiento del disco duro mecanico")
    print("deshabilitando servicios que causan acceso constante al disco.")
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
    
    respuesta = input("Continuar con la optimizacion de HDD? (S/N): ").strip().upper()
    if respuesta != 'S':
        print("Optimizacion cancelada")
        input("Presiona Enter para salir...")
        sys.exit(0)
    
    print()
    print("=" * 70)
    print("INICIANDO OPTIMIZACION DE HDD...")
    print("=" * 70)
    print()
    
    # Deshabilitar Superfetch
    deshabilitar_superfetch()
    
    # Deshabilitar indexacion
    deshabilitar_indexacion()
    
    # Configurar modo de energia
    configurar_modo_energia()
    
    # Optimizar archivo de paginacion
    optimizar_archivo_paginacion()
    
    # Deshabilitar hibernacion
    deshabilitar_hibernacion()
    
    # Ejecutar chkdsk
    ejecutar_chkdsk()
    
    # Desfragmentar disco
    desfragmentar_disco()
    
    print("=" * 70)
    print("OPTIMIZACION DE HDD COMPLETADA")
    print("=" * 70)
    print()
    print("IMPORTANTE: Se recomienda reiniciar el equipo para aplicar")
    print("todos los cambios.")
    print()
    print("Si programaste chkdsk, el equipo lo ejecutara en el siguiente")
    print("reinicio. Puede tardar varias horas.")
    print()
    
    input("Presiona Enter para salir...")

if __name__ == "__main__":
    main()

