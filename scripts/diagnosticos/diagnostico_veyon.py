#!/usr/bin/env python3
"""
Diagnóstico de Problemas de Veyon
Script para diagnosticar problemas de conexión y visualización
"""

import subprocess
import socket
import os
import time
from typing import Dict, List

class VeyonDiagnostic:
    def __init__(self):
        self.veyon_cli = r"C:\Program Files\Veyon\veyon-cli.exe"
        self.problematic_ip = "192.168.50.236"  # PC-01
        
    def run_full_diagnostic(self):
        """Ejecuta diagnóstico completo"""
        print("=" * 60)
        print("DIAGNÓSTICO DE VEYON - PC-01 (192.168.50.236)")
        print("=" * 60)
        print()
        
        # 1. Verificar conectividad básica
        self.test_basic_connectivity()
        
        # 2. Verificar puerto Veyon
        self.test_veyon_port()
        
        # 3. Verificar configuración de Veyon
        self.check_veyon_config()
        
        # 4. Verificar servicios de Veyon
        self.check_veyon_services()
        
        # 5. Probar comandos específicos
        self.test_veyon_commands()
        
        # 6. Verificar firewall
        self.check_firewall()
        
        print("\n" + "=" * 60)
        print("DIAGNÓSTICO COMPLETADO")
        print("=" * 60)
        
    def test_basic_connectivity(self):
        """Prueba conectividad básica"""
        print("1. PROBANDO CONECTIVIDAD BÁSICA...")
        print("-" * 40)
        
        try:
            # Ping básico
            result = subprocess.run(['ping', '-n', '1', self.problematic_ip], 
                                  capture_output=True, timeout=10)
            if result.returncode == 0:
                print(f"✓ Ping a {self.problematic_ip}: OK")
            else:
                print(f"✗ Ping a {self.problematic_ip}: FALLO")
                return
                
            # Verificar que el host está vivo
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.problematic_ip, 22))  # SSH como prueba
            sock.close()
            
            if result == 0:
                print(f"✓ Host {self.problematic_ip} está vivo")
            else:
                print(f"⚠ Host {self.problematic_ip} no responde en puerto 22 (normal)")
                
        except Exception as e:
            print(f"✗ Error en conectividad básica: {e}")
            
    def test_veyon_port(self):
        """Prueba el puerto específico de Veyon"""
        print("\n2. PROBANDO PUERTO VEYON (11100)...")
        print("-" * 40)
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((self.problematic_ip, 11100))
            sock.close()
            
            if result == 0:
                print(f"✓ Puerto 11100 en {self.problematic_ip}: ABIERTO")
            else:
                print(f"✗ Puerto 11100 en {self.problematic_ip}: CERRADO")
                print("  Posibles causas:")
                print("  - Veyon Master no está ejecutándose")
                print("  - Firewall bloqueando el puerto")
                print("  - Servicio de Veyon deshabilitado")
                
        except Exception as e:
            print(f"✗ Error probando puerto Veyon: {e}")
            
    def check_veyon_config(self):
        """Verifica la configuración de Veyon"""
        print("\n3. VERIFICANDO CONFIGURACIÓN DE VEYON...")
        print("-" * 40)
        
        if not os.path.exists(self.veyon_cli):
            print("✗ veyon-cli.exe no encontrado")
            return
            
        try:
            # Listar computadoras en Veyon
            result = subprocess.run([
                self.veyon_cli, "networkobjects", "list", "computer"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                computers = result.stdout.strip().split('\n')
                computers = [comp.strip() for comp in computers if comp.strip()]
                
                print(f"✓ Computadoras en Veyon: {len(computers)}")
                for comp in computers:
                    if self.problematic_ip in comp:
                        print(f"  ✓ PC-01 encontrado: {comp}")
                    else:
                        print(f"  - {comp}")
            else:
                print(f"✗ Error listando computadoras: {result.stderr}")
                
            # Verificar ubicaciones
            result = subprocess.run([
                self.veyon_cli, "networkobjects", "list", "location"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                locations = result.stdout.strip().split('\n')
                locations = [loc.strip() for loc in locations if loc.strip()]
                print(f"✓ Ubicaciones: {locations}")
            else:
                print(f"✗ Error listando ubicaciones: {result.stderr}")
                
        except Exception as e:
            print(f"✗ Error verificando configuración: {e}")
            
    def check_veyon_services(self):
        """Verifica servicios de Veyon"""
        print("\n4. VERIFICANDO SERVICIOS DE VEYON...")
        print("-" * 40)
        
        try:
            # Verificar servicios de Veyon (PC-01 debe ser CLIENTE)
            services = ["VeyonService", "VeyonWorker"]  # Solo servicios de cliente
            
            print("PC-01 debe tener Veyon CLIENTE (no Master):")
            for service in services:
                result = subprocess.run([
                    "sc", "query", service
                ], capture_output=True, text=True, timeout=10)
                
                if "RUNNING" in result.stdout:
                    print(f"✓ {service}: EJECUTÁNDOSE")
                elif "STOPPED" in result.stdout:
                    print(f"⚠ {service}: DETENIDO")
                else:
                    print(f"✗ {service}: NO ENCONTRADO")
            
            # Verificar que NO tenga VeyonMaster ejecutándose
            result = subprocess.run([
                "sc", "query", "VeyonMaster"
            ], capture_output=True, text=True, timeout=10)
            
            if "RUNNING" in result.stdout:
                print("⚠ VeyonMaster: EJECUTÁNDOSE (NO DEBE ESTAR EN PC-01)")
                print("  PC-01 debe ser solo CLIENTE, no MAESTRO")
            else:
                print("✓ VeyonMaster: NO EJECUTÁNDOSE (correcto para cliente)")
                    
        except Exception as e:
            print(f"✗ Error verificando servicios: {e}")
            
    def test_veyon_commands(self):
        """Prueba comandos específicos de Veyon"""
        print("\n5. PROBANDO COMANDOS DE VEYON...")
        print("-" * 40)
        
        if not os.path.exists(self.veyon_cli):
            print("✗ veyon-cli.exe no encontrado")
            return
            
        try:
            # Probar comando de estado
            result = subprocess.run([
                self.veyon_cli, "status"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✓ Comando 'veyon-cli status': OK")
                print(f"  Salida: {result.stdout.strip()}")
            else:
                print(f"✗ Comando 'veyon-cli status': FALLO")
                print(f"  Error: {result.stderr}")
                
            # Probar comando de configuración
            result = subprocess.run([
                self.veyon_cli, "config", "list"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✓ Comando 'veyon-cli config list': OK")
            else:
                print(f"✗ Comando 'veyon-cli config list': FALLO")
                
        except Exception as e:
            print(f"✗ Error probando comandos: {e}")
            
    def check_firewall(self):
        """Verifica configuración del firewall"""
        print("\n6. VERIFICANDO FIREWALL...")
        print("-" * 40)
        
        try:
            # Verificar reglas de firewall para Veyon
            result = subprocess.run([
                "netsh", "advfirewall", "firewall", "show", "rule", "name=all"
            ], capture_output=True, text=True, timeout=30)
            
            if "Veyon" in result.stdout or "veyon" in result.stdout:
                print("✓ Reglas de firewall para Veyon encontradas")
            else:
                print("⚠ No se encontraron reglas específicas para Veyon")
                
            # Verificar estado del firewall
            result = subprocess.run([
                "netsh", "advfirewall", "show", "allprofiles", "state"
            ], capture_output=True, text=True, timeout=30)
            
            print("Estado del firewall:")
            print(result.stdout)
            
        except Exception as e:
            print(f"✗ Error verificando firewall: {e}")
            
    def suggest_solutions(self):
        """Sugiere soluciones basadas en el diagnóstico"""
        print("\n7. SOLUCIONES SUGERIDAS...")
        print("-" * 40)
        
        print("Para resolver el problema del PC-01 (CLIENTE):")
        print()
        print("1. VERIFICAR EN EL PC-01 (CLIENTE):")
        print("   - NO debe tener Veyon Master ejecutándose")
        print("   - Debe tener Veyon CLIENTE ejecutándose")
        print("   - Verificar que esté en modo 'Client'")
        print("   - Verificar configuración de clave pública")
        print("   - Reiniciar servicio VeyonWorker")
        print()
        print("2. VERIFICAR CONFIGURACIÓN DE CLAVES:")
        print("   - PC-01 debe tener la CLAVE PÚBLICA")
        print("   - Laptop debe tener la CLAVE PRIVADA")
        print("   - PC-00 debe tener la CLAVE PRIVADA (backup)")
        print("   - Verificar que las claves coincidan")
        print()
        print("3. VERIFICAR RED:")
        print("   - Verificar que no haya conflictos de IP")
        print("   - Verificar que el puerto 11100 esté abierto")
        print("   - Verificar configuración de firewall")
        print("   - Verificar que esté en la misma red que el maestro")
        print()
        print("4. COMANDOS DE PRUEBA:")
        print("   - Probar conexión desde Laptop (maestro)")
        print("   - Probar conexión desde PC-00 (backup maestro)")
        print("   - Verificar logs de Veyon en PC-01")
        print("   - Reiniciar PC-01 si es necesario")

def main():
    """Función principal"""
    diagnostic = VeyonDiagnostic()
    diagnostic.run_full_diagnostic()
    diagnostic.suggest_solutions()
    
    input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    main()

