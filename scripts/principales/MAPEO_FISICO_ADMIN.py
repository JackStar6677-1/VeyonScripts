#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================
MAPEO FÍSICO DE PCs - Veyon (CON ADMIN)
========================================

Script que mapea las IPs a los números físicos reales de los PCs
en la sala de computación para Veyon (con solicitud automática de admin).
"""

import sys
import os
import subprocess
import socket
import tempfile
import csv
from typing import List, Dict

# Mapeo de MAC addresses a posiciones físicas ordenadas (0-15)
# La MAC address es única y no cambia, perfecta para identificar PCs físicamente
# Orden físico real en la sala de computación (16 PCs: 0-15)
# MAPEO CORREGIDO con las MAC addresses correctas proporcionadas
MAPEO_FISICO_MAC = {
    '00-D8-61-CB-82-61': 0,   # PC-00 (192.168.50.122) - FÍSICAMENTE PC-00 ✓
    '00-D8-61-CB-82-2E': 1,   # PC-01 (192.168.50.236) - FÍSICAMENTE PC-01
    '00-D8-61-CB-94-32': 2,   # PC-02 (192.168.50.222) - FÍSICAMENTE PC-02
    '00-D8-61-CB-80-52': 3,   # PC-03 (192.168.50.34)  - FÍSICAMENTE PC-03
    '00-D8-61-CB-82-A0': 4,   # PC-04 (192.168.50.224) - FÍSICAMENTE PC-04
    '00-D8-61-CB-96-37': 5,   # PC-05 (192.168.50.71)  - FÍSICAMENTE PC-05
    '00-D8-61-CB-82-3B': 6,   # PC-06 (192.168.50.144) - FÍSICAMENTE PC-06
    '00-D8-61-CB-96-9A': 7,   # PC-07 (192.168.50.92)  - FÍSICAMENTE PC-07
    '00-D8-61-5C-FD-6A': 8,   # PC-08 (192.168.50.51)  - FÍSICAMENTE PC-08
    '00-D8-61-CB-85-AF': 9,   # PC-09 (192.168.50.30)  - FÍSICAMENTE PC-09
    '00-D8-61-CB-80-4D': 10,  # PC-10 (192.168.50.18)  - FÍSICAMENTE PC-10
    '00-D8-61-CB-A4-36': 11,  # PC-11 (192.168.50.201) - FÍSICAMENTE PC-11
    '00-D8-61-CB-84-73': 12,  # PC-12 (192.168.50.185) - FÍSICAMENTE PC-12
    '00-D8-61-CB-80-F4': 13,  # PC-13 (192.168.50.178) - FÍSICAMENTE PC-13
    '00-D8-61-CB-94-59': 14,  # PC-14 (192.168.50.84)  - FÍSICAMENTE PC-14
    '00-D8-61-CB-95-50': 15,  # PC-15 (192.168.50.36)  - FÍSICAMENTE PC-15
    # La laptop (PE-LAPTOP) se asignará automáticamente como PC-16 o superior
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

def get_physical_name(mac: str, original_name: str) -> str:
    """Obtiene el nombre físico correcto basado en la MAC address (ordenado 0-15)"""
    if mac in MAPEO_FISICO_MAC:
        position = MAPEO_FISICO_MAC[mac]
        return f"PC-{position:02d}"  # PC-00, PC-01, PC-02, etc.
    else:
        # Si no está en el mapeo, usar el nombre original o generar uno
        if original_name and original_name != 'Unknown':
            return original_name
        else:
            return f"PC-{mac[-2:].upper()}"  # Usar últimos 2 dígitos de MAC

def filter_veyon_clients_with_physical_mapping(devices: List[Dict]) -> List[Dict]:
    """Filtra dispositivos y aplica mapeo físico por MAC (incluye todos los dispositivos)"""
    veyon_clients = []
    next_number = 16  # Empezar desde 16 para dispositivos no mapeados (laptop, router, etc.)
    
    print("Verificando dispositivos y aplicando mapeo físico por MAC...")
    print("=" * 60)
    
    for device in devices:
        ip = device['ip']
        mac = device['mac']
        name = device['name']
        original_name = device['original_name']
        
        # Obtener nombre físico correcto basado en MAC
        physical_name = get_physical_name(mac, original_name)
        
        # Si no está en el mapeo físico (0-15), asignar número secuencial
        if mac not in MAPEO_FISICO_MAC:
            # Asignar nombres especiales para dispositivos conocidos
            if 'PE-LAPTOP' in original_name or 'LAPTOP' in original_name.upper():
                physical_name = f"LAPTOP-{next_number-15:02d}"  # LAPTOP-01, LAPTOP-02, etc.
            elif ip == '192.168.50.1':  # Router/Gateway
                physical_name = f"ROUTER-{next_number-15:02d}"  # ROUTER-01, ROUTER-02, etc.
            else:
                physical_name = f"PC-{next_number:02d}"  # PC-16, PC-17, etc.
            next_number += 1
        
        veyon_clients.append({
            'name': physical_name,
            'ip': ip,
            'mac': mac,
            'real_name': original_name,
            'physical_number': physical_name,
            'has_veyon': test_veyon_client(ip)
        })
        
        veyon_status = "VEYON" if test_veyon_client(ip) else "NO VEYON"
        print(f"  {ip} ({mac}) -> {physical_name} (Real: {original_name}) - {veyon_status}")
    
    return veyon_clients

def clear_existing_computers():
    """Elimina solo las computadoras existentes, mantiene la ubicación"""
    veyon_cli = r"C:\Program Files\Veyon\veyon-cli.exe"
    
    try:
        print("Eliminando computadoras existentes...")
        
        # Obtener lista de computadoras existentes
        result = subprocess.run([
            veyon_cli, "networkobjects", "list", "computer"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            computers = result.stdout.strip().split('\n')
            # Filtrar líneas vacías y espacios
            computers = [comp.strip() for comp in computers if comp.strip()]
            
            if computers:  # Si hay computadoras
                print(f"  Encontradas {len(computers)} computadoras existentes")
                
                # Eliminar cada computadora
                for computer in computers:
                    print(f"  Eliminando: {computer}")
                    remove_result = subprocess.run([
                        veyon_cli, "networkobjects", "remove", "computer", computer
                    ], capture_output=True, text=True, timeout=30)
                    
                    if remove_result.returncode == 0:
                        print(f"    ✓ {computer} eliminado")
                    else:
                        print(f"    ⚠ Error eliminando {computer}: {remove_result.stderr}")
                
                # Verificar que se eliminaron todas
                print("  Verificando eliminación...")
                verify_result = subprocess.run([
                    veyon_cli, "networkobjects", "list", "computer"
                ], capture_output=True, text=True, timeout=30)
                
                if verify_result.returncode == 0:
                    remaining = verify_result.stdout.strip().split('\n')
                    remaining = [comp.strip() for comp in remaining if comp.strip()]
                    if remaining:
                        print(f"  ⚠ Quedan {len(remaining)} computadoras: {remaining}")
                    else:
                        print("  ✓ Todas las computadoras eliminadas correctamente")
                else:
                    print("  ⚠ No se pudo verificar la eliminación")
                
            else:
                print("  ✓ No hay computadoras existentes")
        else:
            print(f"  ⚠ Error listando computadoras: {result.stderr}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error eliminando computadoras: {e}")
        return False

def update_veyon_with_physical_mapping(veyon_clients: List[Dict]):
    """Actualiza Veyon con nombres físicos correctos"""
    veyon_cli = r"C:\Program Files\Veyon\veyon-cli.exe"
    
    if not os.path.exists(veyon_cli):
        print("[ERROR] Veyon no encontrado")
        return False
    
    print(f"\nActualizando Veyon con {len(veyon_clients)} clientes (nombres físicos)...")
    print("=" * 60)
    
    try:
        # Primero eliminar computadoras existentes (mantener ubicación)
        if not clear_existing_computers():
            print("  ⚠ Continuando con la actualización...")
        
        # Verificar que la ubicación existe
        print("Verificando ubicación 'SalaComputacion'...")
        result = subprocess.run([
            veyon_cli, "networkobjects", "add", "location", "SalaComputacion"
        ], capture_output=True, timeout=30)
        
        if result.returncode == 0:
            print("  ✓ Ubicación creada/verificada")
        else:
            print(f"  ⚠ Ubicación ya existe o error: {result.stderr}")
        
        # Ahora agregar computadoras con nombres físicos
        added_count = 0
        for client in veyon_clients:
            name = client['name']  # Nombre físico (PC-00, PC-01, PC-02, etc.)
            ip = client['ip']
            mac = client['mac']
            real_name = client['real_name']
            has_veyon = client.get('has_veyon', False)
            
            veyon_status = "CON VEYON" if has_veyon else "SIN VEYON"
            print(f"Agregando {name} ({ip}) - Real: {real_name} - {veyon_status}")
            
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
        print("Los nombres ahora reflejan el orden físico real en la sala")
        print("Abre Veyon Master para ver los cambios")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error actualizando Veyon: {e}")
        return False

def show_mapping_table():
    """Muestra la tabla de mapeo físico por MAC"""
    print("=" * 70)
    print("TABLA DE MAPEO FÍSICO POR MAC ADDRESS (0-15)")
    print("=" * 70)
    print("MAC Address           -> Posición -> Nombre en Veyon")
    print("-" * 60)
    
    # Ordenar por posición física
    sorted_mapping = sorted(MAPEO_FISICO_MAC.items(), key=lambda x: x[1])
    
    for mac, position in sorted_mapping:
        veyon_name = f"PC-{position:02d}"
        print(f"{mac:<20} -> {position:2d}       -> {veyon_name}")
    
    print("=" * 70)
    print("Los PCs aparecerán ordenados de PC-00 a PC-15 en Veyon")
    print("INDEPENDIENTE de la IP (funciona con IPs dinámicas)")
    print("=" * 70)

def main():
    """Función principal"""
    print("=" * 70)
    print("MAPEO FÍSICO INTELIGENTE - Veyon (POR MAC ADDRESS)")
    print("=" * 70)
    print("Este script mapea las MAC addresses a los números físicos reales")
    print("de los PCs en la sala de computación.")
    print("FUNCIONA CON IPs DINÁMICAS - La MAC no cambia nunca!")
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
    
    # Filtrar dispositivos y aplicar mapeo físico
    veyon_clients = filter_veyon_clients_with_physical_mapping(devices)
    if not veyon_clients:
        print("[ERROR] No se encontraron dispositivos")
        return
    
    print(f"\n[OK] Encontrados {len(veyon_clients)} dispositivos total")
    
    # Contar cuántos tienen Veyon
    veyon_count = sum(1 for client in veyon_clients if client.get('has_veyon', False))
    print(f"  - Con Veyon: {veyon_count}")
    print(f"  - Sin Veyon: {len(veyon_clients) - veyon_count}")
    
    # Preguntar si actualizar
    response = input("\n¿Actualizar Veyon con TODOS los dispositivos? (s/N): ").lower()
    if not response.startswith('s'):
        print("Actualización cancelada")
        return
    
    # Actualizar Veyon con nombres físicos
    update_veyon_with_physical_mapping(veyon_clients)
    
    input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    main()
