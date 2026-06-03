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
import json
import ipaddress
from collections import defaultdict
from typing import List, Dict, Tuple

try:
    import msvcrt
except ImportError:
    msvcrt = None

COMPUTER_PREFIX = "CASTEL"
DEFAULT_LOCATION_NAME = "SalaComputacion"
LOCAL_TOPOLOGY_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "config", "veyon_topology.local.json")
)

def normalize_mac_map(raw_map: Dict) -> Dict:
    """Normaliza claves MAC de un diccionario cargado desde configuracion local."""
    return {
        str(mac).strip().upper(): value
        for mac, value in raw_map.items()
        if str(mac).strip()
    }

def load_local_topology() -> Dict:
    """Carga topologia privada ignorada por Git, sin exponer MACs reales en el repo."""
    if not os.path.exists(LOCAL_TOPOLOGY_PATH):
        print(f"[WARN] Topologia local no encontrada: {LOCAL_TOPOLOGY_PATH}")
        print("[WARN] Se usaran nombres automaticos y solo la ubicacion por defecto.")
        return {}

    try:
        with open(LOCAL_TOPOLOGY_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as exc:
        print(f"[WARN] No se pudo leer la topologia local: {exc}")
        return {}

LOCAL_TOPOLOGY = load_local_topology()

# La topologia real vive en config/veyon_topology.local.json, ignorado por Git.
ROOM_PARENT_LOCATIONS = LOCAL_TOPOLOGY.get("room_parent_locations", {})
COMPUTER_NAME_OVERRIDES_BY_MAC = normalize_mac_map(
    LOCAL_TOPOLOGY.get("computer_name_overrides_by_mac", {})
)
LOCATION_OVERRIDES_BY_MAC = normalize_mac_map(
    LOCAL_TOPOLOGY.get("location_overrides_by_mac", {})
)
PROFESOR_MAC = str(LOCAL_TOPOLOGY.get("profesor_mac", "")).strip().upper()
MASTER_MAC = str(LOCAL_TOPOLOGY.get("master_mac", "")).strip().upper()
MASTER_MACS = set(normalize_mac_map({mac: True for mac in LOCAL_TOPOLOGY.get("master_macs", [])}))
MASTER_MACS.update(mac for mac in (MASTER_MAC, PROFESOR_MAC) if mac)
EXCLUDED_MACS = set(normalize_mac_map({mac: True for mac in LOCAL_TOPOLOGY.get("excluded_macs", [])}))
EXCLUDED_MACS.update(MASTER_MACS)
MAPEO_FISICO_MAC = {
    mac: int(number)
    for mac, number in normalize_mac_map(LOCAL_TOPOLOGY.get("physical_mac_map", {})).items()
}
ACTIVE_LAN_ADAPTERS_CACHE = None

def format_computer_name(number: int) -> str:
    return f"{COMPUTER_PREFIX}-{number:02d}"

def get_client_name(mac: str, fallback_number: int) -> str:
    """Devuelve el nombre visible de Veyon para un equipo detectado."""
    normalized_mac = (mac or "").strip().upper()
    return COMPUTER_NAME_OVERRIDES_BY_MAC.get(normalized_mac) or format_computer_name(fallback_number)

def get_client_location(client: Dict) -> str:
    """Devuelve la ubicacion Veyon correcta para un cliente detectado."""
    mac = (client.get("mac") or "").strip().upper()

    return (
        LOCATION_OVERRIDES_BY_MAC.get(mac)
        or DEFAULT_LOCATION_NAME
    )

def get_location_chain(location: str) -> List[str]:
    """Devuelve la cadena de ubicaciones que debe existir antes de agregar un PC."""
    parent = ROOM_PARENT_LOCATIONS.get(location)
    if parent:
        return [parent, location]
    return [location]

def get_location_parent(location: str) -> str:
    """Devuelve la ubicacion padre para crear jerarquia en Veyon."""
    return ROOM_PARENT_LOCATIONS.get(location, "")

def export_current_veyon_computers(veyon_cli: str) -> Dict[str, Dict]:
    """Exporta los equipos actuales de Veyon indexados por MAC y nombre."""
    current_by_mac: Dict[str, Dict] = {}
    current_by_name: Dict[str, Dict] = {}

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
        export_path = temp_file.name

    try:
        result = subprocess.run([
            veyon_cli, "networkobjects", "export", export_path,
            "format", "%type%;%location%;%name%;%host%;%mac%"
        ], capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            print(f"[WARN] No se pudo exportar el estado actual de Veyon: {result.stderr}")
            return {"by_mac": current_by_mac, "by_name": current_by_name}

        with open(export_path, "r", encoding="utf-8-sig", newline="") as file:
            reader = csv.reader(file, delimiter=";")
            for row in reader:
                if len(row) < 5:
                    continue
                object_type, location, name, host, mac = [cell.strip() for cell in row[:5]]
                if object_type.lower() not in {"computer", "equipo"}:
                    continue

                entry = {
                    "location": location,
                    "name": name,
                    "ip": host,
                    "mac": mac.upper(),
                }
                if entry["mac"]:
                    current_by_mac[entry["mac"]] = entry
                if entry["name"]:
                    current_by_name[entry["name"].upper()] = entry
    except Exception as exc:
        print(f"[WARN] Error leyendo estado actual de Veyon: {exc}")
    finally:
        try:
            os.remove(export_path)
        except OSError:
            pass

    return {"by_mac": current_by_mac, "by_name": current_by_name}

def needs_veyon_update(current: Dict, desired: Dict) -> bool:
    """Indica si un equipo debe reescribirse en Veyon."""
    if not current:
        return True

    return (
        (current.get("name") or "").strip().upper() != desired["name"].strip().upper()
        or (current.get("ip") or "").strip() != desired["ip"].strip()
        or (current.get("mac") or "").strip().upper() != desired["mac"].strip().upper()
        or (current.get("location") or "").strip().upper() != desired["location"].strip().upper()
    )

def get_scan_ranges() -> List[Tuple[str, str]]:
    """Detecta rangos IPv4 para escaneo."""
    ranges: List[Tuple[str, str]] = []

    for adapter in get_active_lan_adapters():
        scan_range = build_scan_range(adapter["ip"], adapter["prefix"])
        if scan_range and scan_range not in ranges:
            print(
                f"[INFO] Red detectada: {adapter['alias']} "
                f"{adapter['ip']}/{adapter['prefix']} -> {scan_range[0]}-{scan_range[1]}"
            )
            ranges.append(scan_range)

    if not ranges:
        ranges = [("192.168.0.1", "192.168.0.254"), ("192.168.100.1", "192.168.100.254")]

    return ranges

def get_active_lan_adapters() -> List[Dict[str, str]]:
    """Lee adaptadores IPv4 activos en Windows y prioriza LAN fisica con gateway."""
    global ACTIVE_LAN_ADAPTERS_CACHE
    if ACTIVE_LAN_ADAPTERS_CACHE is not None:
        return ACTIVE_LAN_ADAPTERS_CACHE

    if os.name != "nt":
        ACTIVE_LAN_ADAPTERS_CACHE = get_socket_lan_adapter()
        return ACTIVE_LAN_ADAPTERS_CACHE

    command = [
        "powershell.exe",
        "-NoProfile",
        "-Command",
        (
            "Get-NetIPConfiguration | "
            "Where-Object { $_.IPv4Address -and $_.NetAdapter.Status -eq 'Up' } | "
            "Select-Object InterfaceAlias,InterfaceDescription,"
            "@{Name='IPv4';Expression={$_.IPv4Address.IPAddress}},"
            "@{Name='PrefixLength';Expression={$_.IPv4Address.PrefixLength}},"
            "@{Name='Gateway';Expression={$_.IPv4DefaultGateway.NextHop}} | "
            "ConvertTo-Json -Depth 3"
        ),
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        if result.returncode != 0 or not result.stdout.strip():
            ACTIVE_LAN_ADAPTERS_CACHE = get_socket_lan_adapter()
            return ACTIVE_LAN_ADAPTERS_CACHE
        raw_adapters = json.loads(result.stdout)
        if isinstance(raw_adapters, dict):
            raw_adapters = [raw_adapters]
    except Exception as exc:
        print(f"[WARN] No se pudieron leer adaptadores Windows: {exc}")
        ACTIVE_LAN_ADAPTERS_CACHE = get_socket_lan_adapter()
        return ACTIVE_LAN_ADAPTERS_CACHE

    adapters = []
    for raw in raw_adapters:
        adapter = normalize_adapter(raw)
        if adapter:
            adapters.append(adapter)

    adapters.sort(key=adapter_priority)
    ACTIVE_LAN_ADAPTERS_CACHE = adapters
    return ACTIVE_LAN_ADAPTERS_CACHE

def normalize_adapter(raw: Dict) -> Dict[str, str]:
    """Valida que un adaptador sea una red LAN privada escaneable."""
    ip = str(raw.get("IPv4") or "").strip()
    prefix = raw.get("PrefixLength")
    alias = str(raw.get("InterfaceAlias") or "").strip()
    description = str(raw.get("InterfaceDescription") or "").strip()
    gateway = str(raw.get("Gateway") or "").strip()

    if not ip or prefix is None:
        return {}

    try:
        address = ipaddress.ip_address(ip)
        prefix_int = int(prefix)
    except ValueError:
        return {}

    if (
        address.is_loopback
        or address.is_link_local
        or address.is_multicast
        or not address.is_private
        or prefix_int < 16
        or prefix_int > 30
    ):
        return {}

    label = f"{alias} {description}".lower()
    tunnel_words = ("tailscale", "wireguard", "zerotier", "vpn", "tunnel", "loopback")
    if any(word in label for word in tunnel_words):
        return {}

    return {
        "ip": ip,
        "prefix": str(prefix_int),
        "alias": alias or description or "Adaptador",
        "description": description,
        "gateway": gateway,
    }

def adapter_priority(adapter: Dict[str, str]) -> Tuple[int, int, str]:
    """Ordena primero interfaces con gateway y nombres tipicos de LAN."""
    label = f"{adapter.get('alias', '')} {adapter.get('description', '')}".lower()
    has_gateway = 0 if adapter.get("gateway") else 1
    wired_or_wifi = 0 if any(word in label for word in ("ethernet", "wi-fi", "wifi", "realtek", "intel")) else 1
    return (has_gateway, wired_or_wifi, adapter.get("ip", ""))

def build_scan_range(ip: str, prefix: str) -> Tuple[str, str]:
    """Construye un rango seguro; limita redes grandes al /24 del equipo local."""
    try:
        prefix_int = int(prefix)
        network = ipaddress.ip_network(f"{ip}/{prefix_int}", strict=False)
        if network.num_addresses > 256:
            octets = ip.split(".")
            return (f"{'.'.join(octets[:3])}.1", f"{'.'.join(octets[:3])}.254")

        hosts = list(network.hosts())
        if not hosts:
            return ("", "")
        return (str(hosts[0]), str(hosts[-1]))
    except Exception:
        return ("", "")

def get_socket_lan_adapter() -> List[Dict[str, str]]:
    """Fallback portable cuando no se puede consultar Get-NetIPConfiguration."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            local_ip = sock.getsockname()[0]
        return [{
            "ip": local_ip,
            "prefix": "24",
            "alias": "SocketFallback",
            "description": "",
            "gateway": "",
        }]
    except Exception:
        return []

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
    adapters = get_active_lan_adapters()
    if adapters:
        return adapters[0]["ip"]
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

def prompt_yes_no_windows(prompt: str, default: bool = False) -> bool:
    """Lee una sola tecla S/N directamente desde la consola de Windows."""
    if msvcrt is None:
        return default

    while msvcrt.kbhit():
        msvcrt.getwch()

    suffix = " [S/N, Enter=N]: " if not default else " [S/N, Enter=S]: "
    sys.stdout.write(f"{prompt}{suffix}")
    sys.stdout.flush()

    while True:
        ch = msvcrt.getwch()

        if ch in ("\x00", "\xe0"):
            msvcrt.getwch()
            continue

        if ch == "\003":
            raise KeyboardInterrupt

        if ch in ("\r", "\n"):
            sys.stdout.write("\n")
            sys.stdout.flush()
            return default

        value = ch.strip().lower()
        if value == "s":
            sys.stdout.write("s\n")
            sys.stdout.flush()
            return True
        if value == "n":
            sys.stdout.write("n\n")
            sys.stdout.flush()
            return False

def prompt_yes_no(prompt: str, default: bool = False) -> bool:
    """Pregunta si/no de forma robusta incluso con stdin roto en consolas elevadas."""
    if os.name == "nt" and msvcrt is not None:
        return prompt_yes_no_windows(prompt, default)
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
        raw_name = (device.get('name') or '').strip().upper()
        original_name = (device.get('original_name') or '').strip().upper()
        key = (ip, mac)

        if ip == local_ip:
            print(f"  {ip} - omitido (equipo administrador actual)")
            continue

        if mac in EXCLUDED_MACS:
            print(f"  {ip} - {mac} - OMITIDO (equipo excluido: admin, master o profesor)")
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
                veyon_name = get_client_name(mac, MAPEO_FISICO_MAC[mac])
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
    """Actualiza Veyon SIN borrar la configuración existente"""
    veyon_cli = r"C:\Program Files\Veyon\veyon-cli.exe"
    
    if not os.path.exists(veyon_cli):
        print("[ERROR] Veyon no encontrado")
        return False
    
    print(f"Actualizando Veyon con {len(veyon_clients)} clientes...")
    
    try:
        # Primero crear las ubicaciones necesarias si no existen.
        locations = []
        seen_locations = set()
        for client in veyon_clients:
            for location in get_location_chain(get_client_location(client)):
                if location not in seen_locations:
                    seen_locations.add(location)
                    locations.append(location)

        for location in locations:
            print(f"Creando ubicacion '{location}'...")
            add_location_cmd = [veyon_cli, "networkobjects", "add", "location", location]
            parent = get_location_parent(location)
            if parent:
                add_location_cmd.append(parent)

            result = subprocess.run(add_location_cmd, capture_output=True, timeout=30)

            if result.returncode == 0:
                print("  [OK] Ubicacion creada/verificada")
            else:
                print(f"  [INFO] Ubicacion ya existe o no requiere cambios: {result.stderr}")
        
        current_objects = export_current_veyon_computers(veyon_cli)
        current_by_mac = current_objects["by_mac"]
        current_by_name = current_objects["by_name"]

        # Ahora sincronizar solo computadoras nuevas o modificadas.
        added_count = 0
        skipped_count = 0
        for client in veyon_clients:
            name = client['name']
            ip = client['ip']
            mac = client['mac']
            location = get_client_location(client)
            desired = {
                "name": name,
                "ip": ip,
                "mac": mac,
                "location": location,
            }

            current = current_by_mac.get(mac.upper()) or current_by_name.get(name.upper())
            if not needs_veyon_update(current, desired):
                print(f"Sin cambios {name} ({ip}) en {location}")
                skipped_count += 1
                continue

            if current:
                print(
                    f"Actualizando {name}: "
                    f"{current.get('ip', 'sin-ip')} -> {ip}, "
                    f"{current.get('location', 'sin-ubicacion')} -> {location}"
                )
            else:
                print(f"Agregando {name} ({ip}) en {location}...")

            # Reemplazar por nombre actual y por el nombre CASTEL-XX historico si cambio.
            names_to_remove = {name}
            if current and current.get("name"):
                names_to_remove.add(current["name"])
            if mac in MAPEO_FISICO_MAC:
                names_to_remove.add(format_computer_name(MAPEO_FISICO_MAC[mac]))

            for existing_name in names_to_remove:
                subprocess.run([
                    veyon_cli, "networkobjects", "remove", existing_name
                ], capture_output=True, text=True, timeout=30)
            
            # Agregar computadora a la ubicación
            result = subprocess.run([
                veyon_cli, "networkobjects", "add", "computer",
                name, ip, mac, location
            ], capture_output=True, timeout=30)
            
            if result.returncode == 0:
                print(f"  ✓ {name} sincronizado correctamente")
                added_count += 1
            else:
                print(f"  ✗ Error sincronizando {name}: {result.stderr}")
        
        print(f"\n[OK] Actualización completada: {added_count} cambios aplicados, {skipped_count} sin cambios")
        print("Abre Veyon Master para ver los cambios")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error actualizando Veyon: {e}")
        return False

def sync_profesor_files(prof_ip: str):
    """Sincroniza archivos y configuración con el PC del profesor vía WinRM"""
    print(f"\n[WINRM] Iniciando sincronización con PC Profesor ({prof_ip})...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    sync_script = os.path.join(repo_root, "deploy", "admin_winrm", "SYNC_PROFESOR.ps1")
    
    if not os.path.exists(sync_script):
        print(f"[ERROR] No se encontró el script de sincronización: {sync_script}")
        return False
        
    try:
        cmd = [
            "powershell.exe", "-ExecutionPolicy", "Bypass", "-File", sync_script,
            "-ComputerName", prof_ip,
            "-LocalRepoPath", repo_root,
            "-LocalMasterConfig", os.path.expandvars(r"%APPDATA%\Veyon\Config\VeyonMaster.json")
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] Sincronización con PC Profesor completada.")
            return True
        else:
            print(f"[ERROR] Falló la sincronización (Código {result.returncode})")
            print(f"Detalle: {result.stdout}\n{result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error al ejecutar sincronización WinRM: {e}")
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
    
    # Actualizar Veyon (SIN borrar configuración)
    update_veyon_safely(veyon_clients)
    
    # Sincronización con el PC del profesor si fue detectado
    prof_device = next((d for d in devices if d['mac'].upper() in MASTER_MACS), None)
    if prof_device:
        print(f"\n[INFO] Se ha detectado el PC Master/Profesor en {prof_device['ip']}")
        if prompt_yes_no("¿Deseas sincronizar los archivos y configuración con el PC Master/Profesor? (s/N): "):
            sync_profesor_files(prof_device['ip'])
    else:
        print("\n[INFO] No se detectó el PC Master/Profesor en la red para sincronización.")

    
    try:
        input("\nPresiona Enter para continuar...")
    except EOFError:
        # Permite ejecucion remota/no interactiva por WinRM sin marcar error.
        pass

if __name__ == "__main__":
    main()
