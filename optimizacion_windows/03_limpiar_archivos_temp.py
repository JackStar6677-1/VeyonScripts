#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimizacion Windows 11 - Limpieza de Archivos Temporales
Script para limpiar archivos temporales y liberar espacio en disco
"""

import subprocess
import sys
import ctypes
import os
import shutil
import glob

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

def obtener_tamano_carpeta(ruta):
    """Obtiene el tamaño total de una carpeta"""
    total = 0
    try:
        for dirpath, dirnames, filenames in os.walk(ruta):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total += os.path.getsize(filepath)
                except:
                    pass
    except:
        pass
    return total

def formatear_bytes(bytes):
    """Formatea bytes a una unidad legible"""
    for unidad in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unidad}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"

def limpiar_carpeta(ruta, descripcion):
    """Limpia una carpeta de archivos temporales"""
    try:
        if not os.path.exists(ruta):
            print(f"  ADVERTENCIA: Carpeta no existe: {ruta}")
            return 0
        
        # Obtener tamaño antes de limpiar
        tamano_antes = obtener_tamano_carpeta(ruta)
        
        print(f"Limpiando: {descripcion}")
        print(f"  Ruta: {ruta}")
        print(f"  Tamaño actual: {formatear_bytes(tamano_antes)}")
        
        archivos_eliminados = 0
        errores = 0
        
        # Limpiar archivos
        for item in os.listdir(ruta):
            item_path = os.path.join(ruta, item)
            try:
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    archivos_eliminados += 1
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    archivos_eliminados += 1
            except Exception as e:
                errores += 1
        
        # Obtener tamaño después de limpiar
        tamano_despues = obtener_tamano_carpeta(ruta)
        liberado = tamano_antes - tamano_despues
        
        print(f"  Archivos eliminados: {archivos_eliminados}")
        print(f"  Errores: {errores}")
        print(f"  Espacio liberado: {formatear_bytes(liberado)}")
        print()
        
        return liberado
        
    except Exception as e:
        print(f"  ERROR: {e}")
        print()
        return 0

def limpiar_cache_navegadores():
    """Limpia el cache de navegadores comunes"""
    print("LIMPIANDO CACHE DE NAVEGADORES...")
    print("-" * 70)
    print()
    
    total_liberado = 0
    usuario = os.environ.get('USERNAME', 'Usuario')
    
    # Cache de Chrome
    chrome_cache = os.path.join("C:\\Users", usuario, "AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cache")
    total_liberado += limpiar_carpeta(chrome_cache, "Cache de Google Chrome")
    
    # Cache de Edge
    edge_cache = os.path.join("C:\\Users", usuario, "AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Cache")
    total_liberado += limpiar_carpeta(edge_cache, "Cache de Microsoft Edge")
    
    # Cache de Firefox
    firefox_cache = os.path.join("C:\\Users", usuario, "AppData\\Local\\Mozilla\\Firefox\\Profiles")
    if os.path.exists(firefox_cache):
        for perfil in os.listdir(firefox_cache):
            cache_path = os.path.join(firefox_cache, perfil, "cache2")
            if os.path.exists(cache_path):
                total_liberado += limpiar_carpeta(cache_path, f"Cache de Firefox - {perfil}")
    
    return total_liberado

def limpiar_archivos_temp():
    """Limpia archivos temporales del sistema"""
    print("LIMPIANDO ARCHIVOS TEMPORALES DEL SISTEMA...")
    print("-" * 70)
    print()
    
    total_liberado = 0
    
    # Temp del usuario
    temp_usuario = os.environ.get('TEMP', '')
    if temp_usuario:
        total_liberado += limpiar_carpeta(temp_usuario, "Archivos temporales del usuario")
    
    # Temp del sistema
    temp_sistema = "C:\\Windows\\Temp"
    total_liberado += limpiar_carpeta(temp_sistema, "Archivos temporales del sistema")
    
    # Archivos temporales de instaladores
    temp_instaladores = "C:\\Windows\\Installer\\$PatchCache$"
    if os.path.exists(temp_instaladores):
        total_liberado += limpiar_carpeta(temp_instaladores, "Cache de instaladores")
    
    return total_liberado

def limpiar_prefetch():
    """Limpia los archivos prefetch"""
    print("LIMPIANDO ARCHIVOS PREFETCH...")
    print("-" * 70)
    print()
    
    prefetch = "C:\\Windows\\Prefetch"
    return limpiar_carpeta(prefetch, "Archivos Prefetch")

def limpiar_papelera():
    """Limpia la papelera de reciclaje"""
    print("LIMPIANDO PAPELERA DE RECICLAJE...")
    print("-" * 70)
    print()
    
    try:
        resultado = subprocess.run(
            ["powershell", "-Command", "Clear-RecycleBin -Force"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if resultado.returncode == 0:
            print("  OK Papelera de reciclaje vaciada")
        else:
            print(f"  ADVERTENCIA: {resultado.stderr}")
        print()
        
    except Exception as e:
        print(f"  ERROR: {e}")
        print()

def ejecutar_disk_cleanup():
    """Ejecuta el liberador de espacio en disco de Windows"""
    print("EJECUTANDO LIBERADOR DE ESPACIO EN DISCO...")
    print("-" * 70)
    print()
    
    try:
        print("Ejecutando cleanmgr con opciones predeterminadas...")
        subprocess.Popen(["cleanmgr", "/sagerun:1"])
        print("  OK Liberador de espacio iniciado")
        print("  NOTA: Se abrira una ventana del liberador de espacio")
        print()
    except Exception as e:
        print(f"  ERROR: {e}")
        print()

def main():
    """Funcion principal"""
    print("=" * 70)
    print("OPTIMIZACION WINDOWS 11 - LIMPIEZA DE ARCHIVOS")
    print("=" * 70)
    print()
    print("Este script eliminara archivos temporales y cache")
    print("para liberar espacio en disco y mejorar el rendimiento.")
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
    
    print("ADVERTENCIA: Esta operacion eliminara archivos temporales.")
    print("Los navegadores pueden tardar un poco mas en abrir la primera vez.")
    print()
    
    respuesta = input("Continuar con la limpieza? (S/N): ").strip().upper()
    if respuesta != 'S':
        print("Limpieza cancelada")
        input("Presiona Enter para salir...")
        sys.exit(0)
    
    print()
    print("=" * 70)
    print("INICIANDO LIMPIEZA DE ARCHIVOS...")
    print("=" * 70)
    print()
    
    total_liberado = 0
    
    # Limpiar archivos temporales
    total_liberado += limpiar_archivos_temp()
    
    # Limpiar cache de navegadores
    total_liberado += limpiar_cache_navegadores()
    
    # Limpiar prefetch
    total_liberado += limpiar_prefetch()
    
    # Limpiar papelera
    limpiar_papelera()
    
    # Ejecutar disk cleanup
    ejecutar_disk_cleanup()
    
    print("=" * 70)
    print("LIMPIEZA COMPLETADA")
    print("=" * 70)
    print()
    print(f"Espacio total liberado: {formatear_bytes(total_liberado)}")
    print()
    print("NOTA: Tambien se ejecuto el liberador de espacio de Windows")
    print("para limpiar archivos adicionales del sistema.")
    print()
    
    input("Presiona Enter para salir...")

if __name__ == "__main__":
    main()

