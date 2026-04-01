#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================
VEYON MAESTRO - Solo Actualizar
========================================

Script maestro que SOLO actualiza Veyon con WakeMeOnLAN
SIN BORRAR la configuraciÃ³n existente.
"""

import sys
import os
import subprocess
import socket
import tempfile
import csv
from collections import defaultdict
from typing import List, Dict, Tuple

try:
    import msvcrt
except ImportError:
    msvcrt = None

COMPUTER_PREFIX = "CASTEL"
LOCATION_NAME = "SalaComputacion"

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
    "A8-A1-59-9B-B2-D8": 42,
}

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

def get_local_ipv4() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except Exception:
        return ""

def read_console_line_fallback(prompt: str) -> str:
    """Lee desde la consola de Windows cuando stdin no es interactivo."""
    if msvcrt is None:
        return ""

    sys.stdout.write(prompt)
    sys.stdout.flush()

    chars = []
    while True:
        ch = msvcrt.getwch()

        if ch in ("\r", "\n"):
            sys.stdout.write("\n")
            sys.stdout.flush()
            return "".join(chars)

        if ch == "\003":
            raise KeyboardInterrupt

        if ch == "\b":
            if chars:
                chars.pop()
                sys.stdout.write("\b \b")
                sys.stdout.flush()
            continue

        if ch in ("\x00", "\xe0"):
            msvcrt.getwch()
            continue

        chars.append(ch)
        sys.stdout.write(ch)
        sys.stdout.flush()

def prompt_yes_no(prompt: str, default: bool = False) -> bool:
    """Pregunta si/no de forma robusta incluso con stdin roto en consolas elevadas."""
    if os.name == "nt" and msvcrt is not None:
        response = read_console_line_fallback(prompt)
    else:
        try:
            response = input(prompt)
        except EOFError:
            response = read_console_line_fallback(prompt)

    response = (response or "").strip().lower()
    if not response:
        return default
    return response.startswith("s")

def collect_network_conflicts(devices: List[Dict]) -> Tuple[Dict[str, List[Dict]], Dict[str, List[Dict]]]:
    """Agrupa dispositivos por IP y MAC para detectar clones o datos inconsistentes."""
    by_ip: Dict[str, List[Dict]] = defaultdict(list)
    by_mac: Dict[str, List[Dict]] = defaultdict(list)

    for device in devices:
        ip = (device.get("ip") or "").strip()
        mac = (device.get("mac") or "").strip().upper()
        if not ip or not mac:
            continue
        by_ip[ip].append(device)
        by_mac[mac].append(device)

    conflict_ips = {
        ip: entries
        for ip, entries in by_ip.items()
        if len({(entry.get("mac") or "").strip().upper() for entry in entries}) > 1
    }
    conflict_macs = {
        mac: entries
        for mac, entries in by_mac.items()
        if len({(entry.get("ip") or "").strip() for entry in entries}) > 1
    }
    return conflict_ips, conflict_macs

def device_name_score(device: Dict) -> int:
    name = (device.get("original_name") or device.get("name") or "").strip()
    if not name or name.lower() == "unknown":
        return 0
    if name.upper().startswith("DESKTOP-") or name.upper().startswith("CASTEL-"):
        return 1
    return 2

def device_score(device: Dict, tested_ips: Dict[str, bool]) -> Tuple[int, int, str, str]:
    ip = (device.get("ip") or "").strip()
    mac = (device.get("mac") or "").strip().upper()
    return (
        1 if tested_ips.get(ip, False) else 0,
        1 if mac in MAPEO_FISICO_MAC else 0,
        device_name_score(device),
        ip,
    )

def choose_best_device(devices: List[Dict], tested_ips: Dict[str, bool]) -> Dict:
    return max(devices, key=lambda device: device_score(device, tested_ips))

def print_network_conflicts(conflict_ips: Dict[str, List[Dict]], conflict_macs: Dict[str, List[Dict]], tested_ips: Dict[str, bool]):
    """Muestra conflictos de red antes de intentar actualizar Veyon."""
    if not conflict_ips and not conflict_macs:
        return

    print("\n[WARN] Se detectaron conflictos de clonacion o inventario en la red")

    if conflict_ips:
        print("[WARN] IPs con multiples MACs detectadas:")
        for ip in sorted(conflict_ips):
            winner = choose_best_device(conflict_ips[ip], tested_ips)
            seen = []
            for entry in conflict_ips[ip]:
                mac = (entry.get("mac") or "").strip().upper()
                name = (entry.get("original_name") or entry.get("name") or "").strip()
                token = f"{mac} ({name or 'sin nombre'})"
                if entry is winner:
                    token += " [elegido]"
                if token not in seen:
                    seen.append(token)
            print(f"  {ip} -> {', '.join(seen)}")

    if conflict_macs:
        print("[WARN] MACs vistas en multiples IPs:")
        for mac in sorted(conflict_macs):
            winner = choose_best_device(conflict_macs[mac], tested_ips)
            seen = []
            for entry in conflict_macs[mac]:
                ip = (entry.get("ip") or "").strip()
                name = (entry.get("original_name") or entry.get("name") or "").strip()
                token = f"{ip} ({name or 'sin nombre'})"
                if entry is winner:
                    token += " [elegido]"
                if token not in seen:
                    seen.append(token)
            print(f"  {mac} -> {', '.join(seen)}")

    print("[WARN] En cada conflicto se conservara solo la mejor coincidencia")

def resolve_network_conflicts(
    devices: List[Dict], tested_ips: Dict[str, bool]
) -> Tuple[List[Dict], Dict[Tuple[str, str], str]]:
    """Conserva una sola entrada por conflicto de IP o MAC."""
    by_ip: Dict[str, List[Dict]] = defaultdict(list)
    by_mac: Dict[str, List[Dict]] = defaultdict(list)
    for device in devices:
        ip = (device.get("ip") or "").strip()
        mac = (device.get("mac") or "").strip().upper()
        if not ip or not mac:
            continue
        by_ip[ip].append(device)
        by_mac[mac].append(device)

    skip_reasons: Dict[Tuple[str, str], str] = {}

    for ip, entries in by_ip.items():
        if len({(entry.get("mac") or "").strip().upper() for entry in entries}) <= 1:
            continue
        winner = choose_best_device(entries, tested_ips)
        for entry in entries:
            if entry is winner:
                continue
            skip_reasons[((entry.get("ip") or "").strip(), (entry.get("mac") or "").strip().upper())] = "IP duplicada / clon descartado"

    for mac, entries in by_mac.items():
        remaining = [
            entry for entry in entries
            if ((entry.get("ip") or "").strip(), (entry.get("mac") or "").strip().upper()) not in skip_reasons
        ]
        if len({(entry.get("ip") or "").strip() for entry in remaining}) <= 1:
            continue
        winner = choose_best_device(remaining, tested_ips)
        for entry in remaining:
            if entry is winner:
                continue
            skip_reasons[((entry.get("ip") or "").strip(), (entry.get("mac") or "").strip().upper())] = "MAC duplicada / clon descartado"

    filtered = []
    for device in devices:
        key = ((device.get("ip") or "").strip(), (device.get("mac") or "").strip().upper())
        if key not in skip_reasons:
            filtered.append(device)

    return filtered, skip_reasons

def remove_name_conflicts(veyon_clients: List[Dict], tested_ips: Dict[str, bool]) -> Tuple[List[Dict], Dict[Tuple[str, str], str]]:
    """Evita que dos equipos distintos intenten ocupar el mismo nombre CASTEL."""
    by_name: Dict[str, List[Dict]] = defaultdict(list)
    for client in veyon_clients:
        by_name[client["name"]].append(client)

    conflicted_names = {
        name: entries
        for name, entries in by_name.items()
        if len({(entry["ip"], entry["mac"]) for entry in entries}) > 1
    }
    if not conflicted_names:
        return veyon_clients, {}

    print("\n[WARN] Se detectaron nombres CASTEL duplicados:")
    filtered_clients = []
    skipped: Dict[Tuple[str, str], str] = {}
    for name in sorted(conflicted_names):
        winner = choose_best_device(conflicted_names[name], tested_ips)
        details = []
        for entry in conflicted_names[name]:
            token = f"{entry['ip']} / {entry['mac']}"
            if entry is winner:
                token += " [elegido]"
            else:
                skipped[(entry["ip"], entry["mac"])] = "Nombre CASTEL duplicado / clon descartado"
            details.append(token)
        print(f"  {name} -> {', '.join(details)}")

    for client in veyon_clients:
        if (client["ip"], client["mac"]) not in skipped:
            filtered_clients.append(client)
    return filtered_clients, skipped

def filter_veyon_clients(devices: List[Dict]) -> List[Dict]:
    """Filtra solo los dispositivos que tienen Veyon"""
    veyon_clients = []
    next_number = max(MAPEO_FISICO_MAC.values(), default=0) + 1
    local_ip = get_local_ipv4()
    tested_ips: Dict[str, bool] = {}
    unique_ips = sorted({
        (device.get("ip") or "").strip()
        for device in devices
        if (device.get("ip") or "").strip() and (device.get("ip") or "").strip() != local_ip
    })
    for ip in unique_ips:
        tested_ips[ip] = test_veyon_client(ip)

    conflict_ips, conflict_macs = collect_network_conflicts(devices)
    print_network_conflicts(conflict_ips, conflict_macs, tested_ips)
    resolved_devices, skipped_conflicts = resolve_network_conflicts(devices, tested_ips)
    allowed_pairs = {(entry['ip'], entry['mac'].upper()) for entry in resolved_devices}
    seen_pairs = set()

    print("Verificando clientes Veyon...")
    for device in devices:
        ip = device['ip']
        mac = device['mac'].upper()
        key = (ip, mac)

        if ip == local_ip:
            print(f"  {ip} - omitido (equipo administrador actual)")
            continue

        if key in skipped_conflicts:
            print(f"  {ip} - {device['name']} - OMITIDO ({skipped_conflicts[key]})")
            continue

        if key not in allowed_pairs:
            continue

        if key in seen_pairs:
            continue
        seen_pairs.add(key)

        if tested_ips[ip]:
            if mac in MAPEO_FISICO_MAC:
                veyon_name = format_computer_name(MAPEO_FISICO_MAC[mac])
            else:
                veyon_name = format_computer_name(next_number)
                next_number += 1
            
            veyon_clients.append({
                'name': veyon_name,
                'ip': ip,
                'mac': mac,
                'real_name': device['original_name']
            })
            print(f"  {ip} - {veyon_name} (Real: {device['original_name']}) - VEYON")
        else:
            print(f"  {ip} - {device['name']} - NO VEYON")

    filtered_clients, skipped_by_name = remove_name_conflicts(veyon_clients, tested_ips)
    for client in veyon_clients:
        key = (client["ip"], client["mac"])
        if key in skipped_by_name:
            print(f"  {client['ip']} - {client['real_name']} - OMITIDO ({skipped_by_name[key]})")

    return filtered_clients

def update_veyon_safely(veyon_clients: List[Dict]):
    """Actualiza Veyon SIN borrar la configuraciÃ³n existente"""
    veyon_cli = r"C:\Program Files\Veyon\veyon-cli.exe"
    
    if not os.path.exists(veyon_cli):
        print("[ERROR] Veyon no encontrado")
        return False
    
    print(f"Actualizando Veyon con {len(veyon_clients)} clientes...")
    
    try:
        # Primero crear la ubicaciÃ³n si no existe
        print(f"Creando ubicaciÃ³n '{LOCATION_NAME}'...")
        result = subprocess.run([
            veyon_cli, "networkobjects", "add", "location", LOCATION_NAME
        ], capture_output=True, timeout=30)
        
        if result.returncode == 0:
            print("  âœ“ UbicaciÃ³n creada/verificada")
        else:
            print(f"  âš  UbicaciÃ³n ya existe o error: {result.stderr}")
        
        # Ahora agregar computadoras
        added_count = 0
        for client in veyon_clients:
            name = client['name']
            ip = client['ip']
            mac = client['mac']
            
            print(f"Agregando {name} ({ip})...")

            # Reemplazar por nombre para mantener configuraciones existentes.
            subprocess.run([
                veyon_cli, "networkobjects", "remove", "computer", name
            ], capture_output=True, text=True, timeout=30)
            
            # Agregar computadora a la ubicaciÃ³n
            result = subprocess.run([
                veyon_cli, "networkobjects", "add", "computer",
                name, ip, mac, LOCATION_NAME
            ], capture_output=True, timeout=30)
            
            if result.returncode == 0:
                print(f"  âœ“ {name} agregado correctamente")
                added_count += 1
            else:
                print(f"  âœ— Error agregando {name}: {result.stderr}")
        
        print(f"\n[OK] ActualizaciÃ³n completada: {added_count} computadoras agregadas")
        print("Abre Veyon Master para ver los cambios")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error actualizando Veyon: {e}")
        return False

def main():
    """FunciÃ³n principal"""
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
    if not prompt_yes_no("\nActualizar Veyon con estos clientes? (s/N): "):
        print("ActualizaciÃ³n cancelada")
        return
    
    # Actualizar Veyon (SIN borrar configuraciÃ³n)
    update_veyon_safely(veyon_clients)
    
    try:
        input("\nPresiona Enter para continuar...")
    except EOFError:
        # Permite ejecucion remota/no interactiva por WinRM sin marcar error.
        pass

if __name__ == "__main__":
    main()



