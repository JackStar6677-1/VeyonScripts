#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimizacion Windows 11 - Informacion del Sistema
Script para mostrar informacion del sistema y recursos
"""

import subprocess
import sys
import platform
import psutil
import ctypes

def obtener_info_sistema():
    """Obtiene informacion basica del sistema"""
    print("INFORMACION DEL SISTEMA")
    print("=" * 70)
    print()
    
    try:
        # Sistema operativo
        print(f"Sistema Operativo: {platform.system()} {platform.release()}")
        print(f"Version: {platform.version()}")
        print(f"Arquitectura: {platform.machine()}")
        print(f"Procesador: {platform.processor()}")
        print()
        
    except Exception as e:
        print(f"Error obteniendo informacion del sistema: {e}")
        print()

def obtener_info_memoria():
    """Obtiene informacion de la memoria RAM"""
    print("MEMORIA RAM")
    print("=" * 70)
    print()
    
    try:
        memoria = psutil.virtual_memory()
        
        total_gb = memoria.total / (1024 ** 3)
        disponible_gb = memoria.available / (1024 ** 3)
        usado_gb = memoria.used / (1024 ** 3)
        porcentaje = memoria.percent
        
        print(f"Total: {total_gb:.2f} GB")
        print(f"Usado: {usado_gb:.2f} GB ({porcentaje}%)")
        print(f"Disponible: {disponible_gb:.2f} GB")
        print()
        
        if total_gb <= 4.5:
            print("ADVERTENCIA: Tu PC tiene 4GB o menos de RAM")
            print("Se recomienda ejecutar TODAS las optimizaciones")
            print()
        elif total_gb <= 8:
            print("NOTA: Tu PC tiene entre 4-8GB de RAM")
            print("Las optimizaciones mejoraran el rendimiento")
            print()
        else:
            print("NOTA: Tu PC tiene mas de 8GB de RAM")
            print("Algunas optimizaciones pueden no ser necesarias")
            print()
        
    except Exception as e:
        print(f"Error obteniendo informacion de memoria: {e}")
        print()

def obtener_info_disco():
    """Obtiene informacion del disco"""
    print("DISCOS")
    print("=" * 70)
    print()
    
    try:
        particiones = psutil.disk_partitions()
        
        for particion in particiones:
            if 'cdrom' in particion.opts or particion.fstype == '':
                continue
            
            try:
                uso = psutil.disk_usage(particion.mountpoint)
                
                total_gb = uso.total / (1024 ** 3)
                usado_gb = uso.used / (1024 ** 3)
                libre_gb = uso.free / (1024 ** 3)
                porcentaje = uso.percent
                
                print(f"Unidad: {particion.device}")
                print(f"Tipo: {particion.fstype}")
                print(f"Total: {total_gb:.2f} GB")
                print(f"Usado: {usado_gb:.2f} GB ({porcentaje}%)")
                print(f"Libre: {libre_gb:.2f} GB")
                print()
                
                if porcentaje > 90:
                    print("ADVERTENCIA: Disco casi lleno!")
                    print("Se recomienda liberar espacio")
                    print()
                elif porcentaje > 80:
                    print("NOTA: Disco con poco espacio")
                    print("Considera limpiar archivos temporales")
                    print()
                
            except Exception as e:
                print(f"Error leyendo {particion.device}: {e}")
                print()
        
    except Exception as e:
        print(f"Error obteniendo informacion de disco: {e}")
        print()

def obtener_tipo_disco():
    """Determina si el disco es HDD o SSD"""
    print("TIPO DE DISCO")
    print("=" * 70)
    print()
    
    try:
        result = subprocess.run(
            ["powershell", "-Command", 
             "Get-PhysicalDisk | Select-Object FriendlyName, MediaType, Size"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(result.stdout)
            
            if "HDD" in result.stdout or "Unspecified" in result.stdout:
                print("NOTA: Parece que tienes un disco HDD (mecanico)")
                print("Se recomienda ejecutar TODAS las optimizaciones de HDD")
                print()
            elif "SSD" in result.stdout:
                print("NOTA: Parece que tienes un disco SSD")
                print("Algunas optimizaciones de HDD no son necesarias")
                print("(como desfragmentacion)")
                print()
        else:
            print("No se pudo determinar el tipo de disco")
            print()
        
    except Exception as e:
        print(f"Error determinando tipo de disco: {e}")
        print()

def obtener_info_cpu():
    """Obtiene informacion del CPU"""
    print("PROCESADOR (CPU)")
    print("=" * 70)
    print()
    
    try:
        print(f"Nucleos fisicos: {psutil.cpu_count(logical=False)}")
        print(f"Nucleos logicos: {psutil.cpu_count(logical=True)}")
        print(f"Uso actual: {psutil.cpu_percent(interval=1)}%")
        print()
        
    except Exception as e:
        print(f"Error obteniendo informacion del CPU: {e}")
        print()

def obtener_tiempo_encendido():
    """Obtiene el tiempo que lleva encendido el sistema"""
    print("TIEMPO DE ACTIVIDAD")
    print("=" * 70)
    print()
    
    try:
        import datetime
        tiempo = datetime.datetime.fromtimestamp(psutil.boot_time())
        ahora = datetime.datetime.now()
        uptime = ahora - tiempo
        
        dias = uptime.days
        horas = uptime.seconds // 3600
        minutos = (uptime.seconds % 3600) // 60
        
        print(f"Inicio del sistema: {tiempo.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Tiempo encendido: {dias} dias, {horas} horas, {minutos} minutos")
        print()
        
        if dias > 7:
            print("RECOMENDACION: El sistema lleva mucho tiempo encendido")
            print("Se recomienda reiniciar el equipo periodicamente")
            print()
        
    except Exception as e:
        print(f"Error obteniendo tiempo de actividad: {e}")
        print()

def recomendar_optimizaciones():
    """Recomienda optimizaciones basadas en el hardware"""
    print("RECOMENDACIONES")
    print("=" * 70)
    print()
    
    try:
        memoria = psutil.virtual_memory()
        total_ram_gb = memoria.total / (1024 ** 3)
        
        print("Basado en tu hardware, se recomienda:")
        print()
        
        if total_ram_gb <= 4.5:
            print("1. [CRITICO] Deshabilitar servicios innecesarios")
            print("2. [CRITICO] Optimizar rendimiento visual")
            print("3. [IMPORTANTE] Limpiar archivos temporales")
            print("4. [IMPORTANTE] Optimizar HDD")
            print("5. [IMPORTANTE] Optimizar programas de inicio")
        elif total_ram_gb <= 8:
            print("1. [IMPORTANTE] Deshabilitar servicios innecesarios")
            print("2. [IMPORTANTE] Optimizar rendimiento visual")
            print("3. [RECOMENDADO] Limpiar archivos temporales")
            print("4. [RECOMENDADO] Optimizar HDD")
            print("5. [RECOMENDADO] Optimizar programas de inicio")
        else:
            print("1. [OPCIONAL] Deshabilitar servicios innecesarios")
            print("2. [OPCIONAL] Optimizar rendimiento visual")
            print("3. [RECOMENDADO] Limpiar archivos temporales")
            print("4. [OPCIONAL] Optimizar HDD")
            print("5. [OPCIONAL] Optimizar programas de inicio")
        
        print()
        
    except Exception as e:
        print(f"Error generando recomendaciones: {e}")
        print()

def main():
    """Funcion principal"""
    print("=" * 70)
    print("INFORMACION DEL SISTEMA - OPTIMIZACION WINDOWS 11")
    print("=" * 70)
    print()
    
    try:
        # Verificar si psutil esta instalado
        import psutil
    except ImportError:
        print("ERROR: psutil no esta instalado")
        print()
        print("Para instalar psutil:")
        print("  pip install psutil")
        print()
        input("Presiona Enter para salir...")
        sys.exit(1)
    
    # Obtener informacion del sistema
    obtener_info_sistema()
    obtener_info_cpu()
    obtener_info_memoria()
    obtener_info_disco()
    obtener_tipo_disco()
    obtener_tiempo_encendido()
    
    # Recomendaciones
    recomendar_optimizaciones()
    
    print("=" * 70)
    print("INFORMACION RECOPILADA")
    print("=" * 70)
    print()
    print("Usa esta informacion para decidir que optimizaciones ejecutar")
    print()
    
    input("Presiona Enter para salir...")

if __name__ == "__main__":
    main()

