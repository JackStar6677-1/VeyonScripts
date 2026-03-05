#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================
MAPEO FÃSICO DE PCs - Veyon (CON ADMIN)
========================================

Script que mapea las IPs a los nÃºmeros fÃ­sicos reales de los PCs
en la sala de computaciÃ³n para Veyon (con solicitud automÃ¡tica de admin).
"""

import sys
import os
import subprocess
import socket
import tempfile
import csv
from typing import List, Dict, Tuple

COMPUTER_PREFIX = "CASTEL"
LOCATION_NAME = "SalaComputacion"

def format_computer_name(number: int) -> str:
    return f"{COMPUTER_PREFIX}-{number:02d}"

def get_scan_ranges() -> List[Tuple[str, str]]:
    """Detecta rangos IPv4 para escaneo."""
    ranges: List[Tuple[str, str]] = [("192.168.0.1", "192.168.0.254"), ("192.168.100.1", "192.168.100.254")]

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            local_ip = sock.getsockname()[0]
    except Exception:
        return ranges

    parts = local_ip.split(".")
    if len(parts) != 4:
        return ranges

    prefix = ".".join(parts[:3])
    local_range = (f"{prefix}.1", f"{prefix}.254")
    if local_range not in ranges:
        ranges.insert(0, local_range)
    return ranges

# Mapeo de MAC addresses a posiciones fÃ­sicas ordenadas (0-15)
# La MAC address es Ãºnica y no cambia, perfecta para identificar PCs fÃ­sicamente
# Orden fÃ­sico real en la sala de computaciÃ³n (16 PCs: 0-15)
# MAPEO CORREGIDO con las MAC addresses correctas proporcionadas
MAPEO_FISICO_MAC = {
    "08-BF-B8-BE-76-66": 1,
    "08-BF-B8-36-6C-21": 2,
    "08-BF-B8-36-6F-B6": 3,
    "08-BF-B8-36-6E-6E": 4,
    "08-BF-B8-36-6E-D7": 5,
    "08-BF-B8-36-70-4F": 6,
    "08-BF-B8-36-6B-32": 7,
    "08-BF-B8-36-6C-04": 8,
    "08-BF-B8-36-6C-2A": 9,
    "08-BF-B8-36-6B-67": 10,
    "08-BF-B8-36-6B-5A": 11,
    "08-BF-B8-6E-20-29": 12,
    "08-BF-B8-36-6B-4A": 13,
    "30-9C-23-D4-B9-D2": 14,
    "08-BF-B8-A3-8B-87": 15,
    "08-BF-B8-A3-8A-3C": 16,
    "08-BF-B8-A3-8B-7E": 17,
    "08-BF-B8-A3-8B-32": 18,
    "08-BF-B8-A3-89-FB": 19,
    "08-BF-B8-A2-2B-5F": 20,
    "08-BF-B8-A2-2B-19": 21,
    "08-BF-B8-6E-1F-F0": 22,
    "30-9C-23-0C-68-CD": 23,
    "08-BF-B8-6E-20-45": 24,
    "08-BF-B8-6E-20-F3": 25,
    "08-BF-B8-6E-20-4B": 26,
    "08-BF-B8-6E-1F-F5": 27,
    "04-7C-16-BD-C2-C6": 28,
    "04-7C-16-BD-C2-CF": 29,
    "04-7C-16-BD-C3-2F": 30,
    "04-7C-16-BD-C2-9C": 31,
    "04-7C-16-BD-C2-94": 32,
    "04-7C-16-BD-C2-E4": 33,
    "08-BF-B8-A3-8A-CD": 34,
    "08-BF-B8-BE-76-FC": 35,
    "08-BF-B8-BE-77-0D": 36,
    "08-BF-B8-A3-8B-95": 37,
    "04-7C-16-BD-C2-AD": 38,
    "08-BF-B8-BE-76-3A": 39,
    "30-9C-23-09-06-4C": 40,
    "30-9C-23-AA-BF-D8": 41,
}

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
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    possible_paths = [
        os.path.join(repo_root, "tools", "wakemeonlan", "WakeMeOnLAN.exe"),
        os.path.join(repo_root, "WakeMeOnLAN.exe"),
        os.path.join(script_dir, "WakeMeOnLAN.exe"),
        r"C:\Users\pablo\Documentos\WakeMeOnLan\WakeMeOnLAN.exe",
        "WakeMeOnLAN.exe",
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

    temp_file = os.path.join(tempfile.gettempdir(), "wake_me_on_lan_scan.csv")

    try:
        seen = set()
        devices = []

        for ip_from, ip_to in get_scan_ranges():
            cmd = [
                wakemeonlan_path,
                "/scan",
                "/scomma",
                temp_file,
                "/UseIPAddressesRange",
                "1",
                "/IPAddressFrom",
                ip_from,
                "/IPAddressTo",
                ip_to,
            ]

            print(f"Escaneando red con WakeMeOnLAN ({ip_from} -> {ip_to})...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=120,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )

            if result.returncode != 0:
                print(f"[WARN] WakeMeOnLAN falló en rango {ip_from}-{ip_to}")
                continue

            if os.path.exists(temp_file):
                with open(temp_file, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        ip = row.get("IP Address")
                        mac = row.get("MAC Address")
                        if not ip or not mac:
                            continue
                        key = (ip, mac)
                        if key in seen:
                            continue
                        seen.add(key)
                        devices.append(
                            {
                                "ip": ip,
                                "mac": mac,
                                "name": row.get("Computer Name", "Unknown"),
                                "original_name": row.get("Computer Name", "Unknown"),
                            }
                        )

        print(f"WakeMeOnLAN encontró {len(devices)} dispositivos")
        return devices

    except Exception as e:
        print(f"[ERROR] Error escaneando con WakeMeOnLAN: {e}")
        return []
    finally:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
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

def get_physical_name(mac: str, original_name: str) -> str:
    """Obtiene el nombre fÃ­sico correcto basado en la MAC address (ordenado 0-15)"""
    if mac in MAPEO_FISICO_MAC:
        position = MAPEO_FISICO_MAC[mac]
        return format_computer_name(position)
    return original_name if original_name and original_name != 'Unknown' else ""

def filter_veyon_clients_with_physical_mapping(devices: List[Dict]) -> List[Dict]:
    """Filtra dispositivos y aplica mapeo fÃ­sico por MAC (incluye todos los dispositivos)"""
    veyon_clients = []
    next_number = max(MAPEO_FISICO_MAC.values(), default=0) + 1
    
    print("Verificando dispositivos y aplicando mapeo fÃ­sico por MAC...")
    print("=" * 60)
    
    for device in devices:
        ip = device['ip']
        mac = device['mac']
        name = device['name']
        original_name = device['original_name']
        
        # Obtener nombre fÃ­sico correcto basado en MAC
        physical_name = get_physical_name(mac, original_name)
        
        has_veyon = test_veyon_client(ip)

        if not has_veyon:
            print(f"  {ip} ({mac}) -> descartado (sin Veyon)")
            continue

        # Si no estÃ¡ en el mapeo fÃ­sico, asignar nÃºmero secuencial
        if mac not in MAPEO_FISICO_MAC:
            physical_name = format_computer_name(next_number)
            next_number += 1
        
        veyon_clients.append({
            'name': physical_name,
            'ip': ip,
            'mac': mac,
            'real_name': original_name,
            'physical_number': physical_name,
            'has_veyon': has_veyon
        })
        
        veyon_status = "VEYON" if has_veyon else "NO VEYON"
        print(f"  {ip} ({mac}) -> {physical_name} (Real: {original_name}) - {veyon_status}")
    
    return veyon_clients

def upsert_computer(veyon_cli: str, name: str, ip: str, mac: str) -> subprocess.CompletedProcess:
    """Reemplaza por nombre para no borrar toda la configuraciÃ³n existente."""
    subprocess.run(
        [veyon_cli, "networkobjects", "remove", "computer", name],
        capture_output=True,
        text=True,
        timeout=30
    )
    return subprocess.run(
        [veyon_cli, "networkobjects", "add", "computer", name, ip, mac, LOCATION_NAME],
        capture_output=True,
        text=True,
        timeout=30
    )

def update_veyon_with_physical_mapping(veyon_clients: List[Dict]):
    """Actualiza Veyon con nombres fÃ­sicos correctos"""
    veyon_cli = r"C:\Program Files\Veyon\veyon-cli.exe"
    
    if not os.path.exists(veyon_cli):
        print("[ERROR] Veyon no encontrado")
        return False
    
    print(f"\nActualizando Veyon con {len(veyon_clients)} clientes (nombres fÃ­sicos)...")
    print("=" * 60)
    
    try:
        # Verificar que la ubicaciÃ³n existe
        print(f"Verificando ubicaciÃ³n '{LOCATION_NAME}'...")
        result = subprocess.run([
            veyon_cli, "networkobjects", "add", "location", LOCATION_NAME
        ], capture_output=True, timeout=30)
        
        if result.returncode == 0:
            print("  âœ“ UbicaciÃ³n creada/verificada")
        else:
            print(f"  âš  UbicaciÃ³n ya existe o error: {result.stderr}")
        
        # Ahora agregar computadoras con nombres fÃ­sicos
        added_count = 0
        for client in veyon_clients:
            name = client['name']
            ip = client['ip']
            mac = client['mac']
            real_name = client['real_name']
            has_veyon = client.get('has_veyon', False)
            
            veyon_status = "CON VEYON" if has_veyon else "SIN VEYON"
            print(f"Agregando {name} ({ip}) - Real: {real_name} - {veyon_status}")
            
            result = upsert_computer(veyon_cli, name, ip, mac)
            
            if result.returncode == 0:
                print(f"  âœ“ {name} agregado correctamente")
                added_count += 1
            else:
                print(f"  âœ— Error agregando {name}: {result.stderr}")
        
        print(f"\n[OK] ActualizaciÃ³n completada: {added_count} computadoras agregadas")
        print("Los nombres ahora reflejan el orden fÃ­sico real en la sala")
        print("Abre Veyon Master para ver los cambios")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error actualizando Veyon: {e}")
        return False

def show_mapping_table():
    """Muestra la tabla de mapeo fÃ­sico por MAC"""
    print("=" * 70)
    print("TABLA DE MAPEO FÃSICO POR MAC ADDRESS")
    print("=" * 70)
    print("MAC Address           -> PosiciÃ³n -> Nombre en Veyon")
    print("-" * 60)
    
    # Ordenar por posiciÃ³n fÃ­sica
    sorted_mapping = sorted(MAPEO_FISICO_MAC.items(), key=lambda x: x[1])
    
    for mac, position in sorted_mapping:
        veyon_name = format_computer_name(position)
        print(f"{mac:<20} -> {position:2d}       -> {veyon_name}")
    
    print("=" * 70)
    print(f"Los PCs aparecerÃ¡n ordenados como {COMPUTER_PREFIX}-XX en Veyon")
    print("INDEPENDIENTE de la IP (funciona con IPs dinÃ¡micas)")
    print("=" * 70)

def main():
    """FunciÃ³n principal"""
    print("=" * 70)
    print("MAPEO FÃSICO INTELIGENTE - Veyon (POR MAC ADDRESS)")
    print("=" * 70)
    print("Este script mapea las MAC addresses a los nÃºmeros fÃ­sicos reales")
    print("de los PCs en la sala de computaciÃ³n.")
    print("FUNCIONA CON IPs DINÃMICAS - La MAC no cambia nunca!")
    print()
    
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
    
    # Mostrar tabla de mapeo
    show_mapping_table()
    
    # Escanear con WakeMeOnLAN
    devices = scan_with_wakemeonlan()
    if not devices:
        print("[ERROR] No se encontraron dispositivos")
        return
    
    # Filtrar dispositivos y aplicar mapeo fÃ­sico
    veyon_clients = filter_veyon_clients_with_physical_mapping(devices)
    if not veyon_clients:
        print("[ERROR] No se encontraron dispositivos")
        return
    
    print(f"\n[OK] Encontrados {len(veyon_clients)} dispositivos total")
    
    # Contar cuÃ¡ntos tienen Veyon
    veyon_count = sum(1 for client in veyon_clients if client.get('has_veyon', False))
    print(f"  - Con Veyon: {veyon_count}")
    print(f"  - Sin Veyon: {len(veyon_clients) - veyon_count}")
    
    # Preguntar si actualizar
    response = input("\nÂ¿Actualizar Veyon con TODOS los dispositivos? (s/N): ").lower()
    if not response.startswith('s'):
        print("ActualizaciÃ³n cancelada")
        return
    
    # Actualizar Veyon con nombres fÃ­sicos
    update_veyon_with_physical_mapping(veyon_clients)
    
    input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    main()


