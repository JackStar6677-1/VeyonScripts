#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WINRM MAESTRO

Escanea la red con WakeMeOnLAN y verifica disponibilidad de WinRM (TCP 5985).
Genera reporte CSV y TXT en reports/runs/<fecha>.
"""

import csv
import json
import os
import socket
import subprocess
import tempfile
from datetime import datetime
from typing import Dict, List, Tuple

COMPUTER_PREFIX = "CASTEL"
LOCAL_TOPOLOGY_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "config", "veyon_topology.local.json")
)

def load_physical_mac_map() -> Dict[str, int]:
    """Carga el mapeo fisico privado desde config/veyon_topology.local.json."""
    if not os.path.exists(LOCAL_TOPOLOGY_PATH):
        print(f"[WARN] Topologia local no encontrada: {LOCAL_TOPOLOGY_PATH}")
        return {}

    try:
        with open(LOCAL_TOPOLOGY_PATH, "r", encoding="utf-8") as file:
            topology = json.load(file)
    except Exception as exc:
        print(f"[WARN] No se pudo leer la topologia local: {exc}")
        return {}

    return {
        str(mac).strip().upper(): int(number)
        for mac, number in topology.get("physical_mac_map", {}).items()
        if str(mac).strip()
    }

MAPEO_FISICO_MAC = load_physical_mac_map()


def format_computer_name(number: int) -> str:
    return f"{COMPUTER_PREFIX}-{number:02d}"


def get_scan_ranges() -> List[Tuple[str, str]]:
    ranges: List[Tuple[str, str]] = [("192.168.0.1", "192.168.0.254"), ("192.168.100.1", "192.168.100.254")]
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            local_ip = sock.getsockname()[0]
        parts = local_ip.split(".")
        if len(parts) == 4:
            prefix = ".".join(parts[:3])
            local_range = (f"{prefix}.1", f"{prefix}.254")
            if local_range not in ranges:
                ranges.insert(0, local_range)
    except Exception:
        pass
    return ranges


def find_wakemeonlan() -> str:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    possible_paths = [
        os.path.join(repo_root, "tools", "wakemeonlan", "WakeMeOnLAN.exe"),
        os.path.join(repo_root, "WakeMeOnLAN.exe"),
        os.path.join(script_dir, "WakeMeOnLAN.exe"),
        "WakeMeOnLAN.exe",
    ]
    for path in possible_paths:
        if os.path.isfile(path):
            return path
    return ""


def scan_with_wakemeonlan() -> List[Dict]:
    exe = find_wakemeonlan()
    if not exe:
        print("[ERROR] WakeMeOnLAN.exe no encontrado")
        return []

    temp_file = os.path.join(tempfile.gettempdir(), "wake_scan_winrm.csv")
    devices: List[Dict] = []
    seen = set()
    for ip_from, ip_to in get_scan_ranges():
        cmd = [
            exe,
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
        print(f"Escaneando {ip_from} -> {ip_to} ...")
        try:
            subprocess.run(
                cmd,
                capture_output=True,
                timeout=120,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                check=False,
            )
        except Exception:
            continue

        if not os.path.exists(temp_file):
            continue

        with open(temp_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ip = (row.get("IP Address") or "").strip()
                mac = (row.get("MAC Address") or "").strip().upper()
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
                        "name": (row.get("Computer Name") or "").strip(),
                        "status": (row.get("Status") or "").strip(),
                    }
                )

    if os.path.exists(temp_file):
        try:
            os.remove(temp_file)
        except OSError:
            pass

    return devices


def is_port_open(ip: str, port: int, timeout: float = 0.45) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        return s.connect_ex((ip, port)) == 0
    except Exception:
        return False
    finally:
        s.close()


def annotate(devices: List[Dict]) -> List[Dict]:
    rows = []
    for d in devices:
        mac = d["mac"]
        num = MAPEO_FISICO_MAC.get(mac)
        rows.append(
            {
                "castel": format_computer_name(num) if num else "",
                "ip": d["ip"],
                "mac": mac,
                "name": d["name"],
                "wake_status": d["status"],
                "winrm_5985": "OK" if is_port_open(d["ip"], 5985) else "NO",
                "veyon_11100": "OK" if is_port_open(d["ip"], 11100) else "NO",
            }
        )
    rows.sort(key=lambda x: (0 if x["castel"] else 1, x["castel"], x["ip"]))
    return rows


def write_reports(rows: List[Dict]) -> Tuple[str, str]:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    day_dir = os.path.join(repo_root, "reports", "runs", datetime.now().strftime("%Y-%m-%d"))
    os.makedirs(day_dir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(day_dir, f"winrm_scan_{stamp}.csv")
    txt_path = os.path.join(day_dir, f"winrm_scan_{stamp}.txt")

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["CASTEL", "IP", "MAC", "Name", "WakeStatus", "WinRM5985", "Veyon11100"])
        for r in rows:
            w.writerow([r["castel"], r["ip"], r["mac"], r["name"], r["wake_status"], r["winrm_5985"], r["veyon_11100"]])

    total = len(rows)
    castel = [r for r in rows if r["castel"]]
    winrm_ok = [r for r in rows if r["winrm_5985"] == "OK"]
    castel_winrm_no = [r for r in castel if r["winrm_5985"] != "OK"]

    lines = [
        "WINRM MAESTRO - REPORTE",
        f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"Dispositivos detectados (WakeMeOnLAN): {total}",
        f"Equipos CASTEL detectados por MAC: {len(castel)}",
        f"WinRM 5985 abierto (total): {len(winrm_ok)}",
        f"CASTEL con WinRM pendiente: {len(castel_winrm_no)}",
        "",
        "CASTEL con WinRM pendiente:",
    ]
    for r in castel_winrm_no:
        lines.append(f"- {r['castel']} {r['ip']} {r['mac']}")

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return txt_path, csv_path


def main() -> None:
    print("=" * 56)
    print("WINRM MAESTRO - Escaneo y verificacion WinRM")
    print("=" * 56)
    devices = scan_with_wakemeonlan()
    if not devices:
        print("[ERROR] No se detectaron dispositivos")
        return
    rows = annotate(devices)
    txt, csvp = write_reports(rows)
    print(f"[OK] Dispositivos detectados: {len(rows)}")
    print(f"[OK] Reporte TXT: {txt}")
    print(f"[OK] Reporte CSV: {csvp}")


if __name__ == "__main__":
    main()
