#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================
VEYON MAESTRO - Solo Actualizar
========================================

Script maestro que SOLO actualiza Veyon con WakeMeOnLAN
SIN BORRAR la configuración existente.

Autor: Pablo Elías Avendaño Miranda
Título: Ingeniero en Informática
© 2025 - Todos los derechos reservados
"""

import sys
import os
import subprocess
import socket
import tempfile
import csv
from typing import List, Dict

def is_admin():
    """Verifica si el script se ejecuta con permisos de administrador"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def request_admin():
    """Solicita permisos de administrador"""
    try:
        script_path = os.path.abspath(__file__)
        python_path = sys.executable
        
        subprocess.run([
            "powershell", "-Command",
            f"Start-Process {python_path} -ArgumentList '{script_path}' -Verb RunAs"
        ], check=True)
        return True
    except Exception as e:
        print(f"[ERROR] Error al solicitar permisos de administrador: {e}")
        return False

def find_wakemeonlan():
    """Encuentra WakeMeOnLAN.exe"""
    possible_paths = [
        os.path.join(os.path.dirname(__file__), "WakeMeOnLAN.exe"),
        r"C:\Users\pablo\Documentos\WakeMeOnLan\WakeMeOnLAN.exe",
        "WakeMeOnLAN.exe"
    ]
    
    for path in possible_paths:
        if os.path.isfile(path):
            return path
    return None

def scan_with_wakemeonlan():
    """Escanea la red con WakeMeOnLAN"""
    wakemeonlan_path = find_wakemeonlan()
    if not wakemeonlan_path:
        print("[ERROR] WakeMeOnLAN.exe no encontrado")
        return []
    
    print(f"Usando WakeMeOnLAN: {wakemeonlan_path}")
    
    # Crear archivo temporal para el CSV
    temp_file = os.path.join(tempfile.gettempdir(), "wake_me_on_lan_scan.csv")
    
    try:
        # Ejecutar WakeMeOnLAN
        cmd = [wakemeonlan_path, "/scan", "/scomma", temp_file, 
               "/UseIPAddressesRange", "1", 
               "/IPAddressFrom", "192.168.50.1", 
               "/IPAddressTo", "192.168.50.254"]
        
        print("Escaneando red con WakeMeOnLAN...")
        result = subprocess.run(cmd, capture_output=True, timeout=120,
                              creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        
        if result.returncode != 0:
            print(f"[ERROR] WakeMeOnLAN falló: {result.stderr}")
            return []
        
        # Leer resultados
        devices = []
        if os.path.exists(temp_file):
            with open(temp_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('IP Address') and row.get('MAC Address'):
                        devices.append({
                            'ip': row['IP Address'],
                            'mac': row['MAC Address'],
                            'name': row.get('Computer Name', 'Unknown'),
                            'original_name': row.get('Computer Name', 'Unknown')
                        })
        
        print(f"WakeMeOnLAN encontró {len(devices)} dispositivos")
        return devices
        
    except Exception as e:
        print(f"[ERROR] Error escaneando con WakeMeOnLAN: {e}")
        return []
    finally:
        # Limpiar archivo temporal
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass

def test_veyon_client(ip: str, port: int = 11100, timeout: float = 0.5) -> bool:
    """Verifica si una IP tiene un cliente Veyon activo"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False

def filter_veyon_clients(devices: List[Dict]) -> List[Dict]:
    """Filtra solo los dispositivos que tienen Veyon"""
    veyon_clients = []
    
    print("Verificando clientes Veyon...")
    for device in devices:
        ip = device['ip']
        name = device['name']
        
        if test_veyon_client(ip):
            # Generar nombre para Veyon
            if name and name != 'Unknown':
                veyon_name = name
            else:
                veyon_name = f"PC-{ip.split('.')[-1].zfill(2)}"
            
            veyon_clients.append({
                'name': veyon_name,
                'ip': ip,
                'mac': device['mac'],
                'real_name': device['original_name']
            })
            print(f"  {ip} - {veyon_name} (Real: {device['original_name']}) - VEYON")
        else:
            print(f"  {ip} - {name} - NO VEYON")
    
    return veyon_clients

def update_veyon_safely(veyon_clients: List[Dict]):
    """Actualiza Veyon SIN borrar la configuración existente"""
    veyon_cli = r"C:\Program Files\Veyon\veyon-cli.exe"
    
    if not os.path.exists(veyon_cli):
        print("[ERROR] Veyon no encontrado")
        return False
    
    print(f"Actualizando Veyon con {len(veyon_clients)} clientes...")
    
    try:
        # Primero crear la ubicación si no existe
        print("Creando ubicación 'SalaComputacion'...")
        result = subprocess.run([
            veyon_cli, "networkobjects", "add", "location", "SalaComputacion"
        ], capture_output=True, timeout=30)
        
        if result.returncode == 0:
            print("  ✓ Ubicación creada/verificada")
        else:
            print(f"  ⚠ Ubicación ya existe o error: {result.stderr}")
        
        # Ahora agregar computadoras
        added_count = 0
        for client in veyon_clients:
            name = client['name']
            ip = client['ip']
            mac = client['mac']
            
            print(f"Agregando {name} ({ip})...")
            
            # Agregar computadora a la ubicación
            result = subprocess.run([
                veyon_cli, "networkobjects", "add", "computer",
                name, ip, mac, "SalaComputacion"
            ], capture_output=True, timeout=30)
            
            if result.returncode == 0:
                print(f"  ✓ {name} agregado correctamente")
                added_count += 1
            else:
                print(f"  ✗ Error agregando {name}: {result.stderr}")
        
        print(f"\n[OK] Actualización completada: {added_count} computadoras agregadas")
        print("Abre Veyon Master para ver los cambios")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error actualizando Veyon: {e}")
        return False

def main():
    """Función principal"""
    print("=" * 60)
    print("VEYON MAESTRO - Solo Actualizar (Sin Borrar Config)")
    print("=" * 60)
    
    # Verificar permisos de administrador
    if not is_admin():
        print("[ADMIN] Se requieren permisos de administrador")
        print("[ADMIN] Solicitando permisos...")
        
        if request_admin():
            return
        else:
            print("[ERROR] No se pudieron obtener permisos de administrador")
            print("Ejecuta este script como administrador manualmente")
            return
    
    # Escanear con WakeMeOnLAN
    devices = scan_with_wakemeonlan()
    if not devices:
        print("[ERROR] No se encontraron dispositivos")
        return
    
    # Filtrar solo los que tienen Veyon
    veyon_clients = filter_veyon_clients(devices)
    if not veyon_clients:
        print("[ERROR] No se encontraron clientes Veyon")
        return
    
    print(f"\n[OK] Encontrados {len(veyon_clients)} clientes Veyon")
    
    # Preguntar si actualizar
    response = input("\n¿Actualizar Veyon con estos clientes? (s/N): ").lower()
    if not response.startswith('s'):
        print("Actualización cancelada")
        return
    
    # Actualizar Veyon (SIN borrar configuración)
    update_veyon_safely(veyon_clients)
    
    input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    main()
