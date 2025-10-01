#!/usr/bin/env python3
"""
Diagnóstico Profundo PC-01
Script específico para diagnosticar por qué PC-01 no funciona siendo un clon
"""

import subprocess
import socket
import os
import time
import json
from typing import Dict, List

class DiagnosticoProfundoPC01:
    def __init__(self):
        self.veyon_cli = r"C:\Program Files\Veyon\veyon-cli.exe"
        self.pc01_ip = "192.168.50.236"
        self.pc01_mac = "00-D8-61-CB-82-2E"
        
    def run_diagnostico_profundo(self):
        """Ejecuta diagnóstico profundo del PC-01"""
        print("=" * 70)
        print("DIAGNÓSTICO PROFUNDO - PC-01 (CLON QUE NO FUNCIONA)")
        print("=" * 70)
        print()
        
        # 1. Verificar conectividad específica
        self.test_connectivity_detailed()
        
        # 2. Verificar configuración de Veyon específica
        self.check_veyon_config_detailed()
        
        # 3. Verificar servicios específicos
        self.check_services_detailed()
        
        # 4. Verificar archivos de configuración
        self.check_config_files()
        
        # 5. Verificar logs de Veyon
        self.check_veyon_logs()
        
        # 6. Comparar con PCs que funcionan
        self.compare_with_working_pcs()
        
        # 7. Probar comandos específicos
        self.test_specific_commands()
        
        print("\n" + "=" * 70)
        print("DIAGNÓSTICO PROFUNDO COMPLETADO")
        print("=" * 70)
        
    def test_connectivity_detailed(self):
        """Prueba conectividad detallada al PC-01"""
        print("1. PRUEBA DE CONECTIVIDAD DETALLADA...")
        print("-" * 50)
        
        try:
            # Ping con múltiples intentos
            print(f"Probando ping a {self.pc01_ip}...")
            for i in range(3):
                result = subprocess.run(['ping', '-n', '1', self.pc01_ip], 
                                      capture_output=True, timeout=10)
                if result.returncode == 0:
                    print(f"  ✓ Ping {i+1}/3: OK")
                else:
                    print(f"  ✗ Ping {i+1}/3: FALLO")
                    return
                    
            # Prueba de puerto específico con timeout extendido
            print(f"Probando puerto 11100 en {self.pc01_ip}...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(15)  # Timeout extendido
            result = sock.connect_ex((self.pc01_ip, 11100))
            sock.close()
            
            if result == 0:
                print(f"  ✓ Puerto 11100: ABIERTO")
            else:
                print(f"  ✗ Puerto 11100: CERRADO (Error: {result})")
                print("    Posibles causas:")
                print("    - VeyonWorker no está ejecutándose")
                print("    - Firewall bloqueando el puerto")
                print("    - Servicio de Veyon detenido")
                
            # Prueba de otros puertos comunes
            common_ports = [22, 80, 443, 3389]
            for port in common_ports:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((self.pc01_ip, port))
                sock.close()
                if result == 0:
                    print(f"  ✓ Puerto {port}: ABIERTO")
                else:
                    print(f"  - Puerto {port}: CERRADO")
                    
        except Exception as e:
            print(f"✗ Error en prueba de conectividad: {e}")
            
    def check_veyon_config_detailed(self):
        """Verifica configuración detallada de Veyon"""
        print("\n2. CONFIGURACIÓN DETALLADA DE VEYON...")
        print("-" * 50)
        
        if not os.path.exists(self.veyon_cli):
            print("✗ veyon-cli.exe no encontrado")
            return
            
        try:
            # Verificar configuración completa
            result = subprocess.run([
                self.veyon_cli, "config", "list"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✓ Configuración de Veyon accesible")
                
                # Buscar configuraciones específicas
                config_lines = result.stdout.split('\n')
                important_configs = [
                    'Authentication/Method',
                    'Authentication/PrivateKeyBaseDir',
                    'Authentication/PublicKeyBaseDir',
                    'Service/',
                    'Network/',
                    'AccessControl/'
                ]
                
                print("Configuraciones importantes:")
                for line in config_lines:
                    for config in important_configs:
                        if config in line:
                            print(f"  - {line.strip()}")
                            
            else:
                print(f"✗ Error accediendo a configuración: {result.stderr}")
                
            # Verificar computadoras específicamente
            result = subprocess.run([
                self.veyon_cli, "networkobjects", "list", "computer"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                computers = result.stdout.strip().split('\n')
                computers = [comp.strip() for comp in computers if comp.strip()]
                
                print(f"\nComputadoras en Veyon ({len(computers)}):")
                pc01_found = False
                for comp in computers:
                    if self.pc01_ip in comp or "PC-01" in comp:
                        print(f"  ✓ PC-01 encontrado: {comp}")
                        pc01_found = True
                    else:
                        print(f"  - {comp}")
                        
                if not pc01_found:
                    print("  ⚠ PC-01 NO encontrado en Veyon")
                    
        except Exception as e:
            print(f"✗ Error verificando configuración: {e}")
            
    def check_services_detailed(self):
        """Verifica servicios detalladamente"""
        print("\n3. VERIFICACIÓN DETALLADA DE SERVICIOS...")
        print("-" * 50)
        
        try:
            # Verificar servicios de Veyon
            services = ["VeyonService", "VeyonMaster", "VeyonWorker"]
            
            for service in services:
                result = subprocess.run([
                    "sc", "query", service
                ], capture_output=True, text=True, timeout=10)
                
                if "RUNNING" in result.stdout:
                    print(f"✓ {service}: EJECUTÁNDOSE")
                    
                    # Obtener información detallada del servicio
                    result_detail = subprocess.run([
                        "sc", "qc", service
                    ], capture_output=True, text=True, timeout=10)
                    
                    if result_detail.returncode == 0:
                        lines = result_detail.stdout.split('\n')
                        for line in lines:
                            if 'BINARY_PATH_NAME' in line:
                                print(f"    Ruta: {line.split(':', 1)[1].strip()}")
                            elif 'START_TYPE' in line:
                                print(f"    Inicio: {line.split(':', 1)[1].strip()}")
                                
                elif "STOPPED" in result.stdout:
                    print(f"⚠ {service}: DETENIDO")
                else:
                    print(f"✗ {service}: NO ENCONTRADO")
                    
        except Exception as e:
            print(f"✗ Error verificando servicios: {e}")
            
    def check_config_files(self):
        """Verifica archivos de configuración"""
        print("\n4. VERIFICACIÓN DE ARCHIVOS DE CONFIGURACIÓN...")
        print("-" * 50)
        
        # Buscar archivos de configuración de Veyon
        config_locations = [
            r"C:\ProgramData\Veyon",
            r"C:\Users\%USERNAME%\AppData\Roaming\Veyon",
            r"C:\Users\%USERNAME%\AppData\Local\Veyon",
            r"C:\Users\%USERNAME%\.config\veyon"
        ]
        
        for location in config_locations:
            expanded_location = os.path.expandvars(location)
            if os.path.exists(expanded_location):
                print(f"✓ Ubicación encontrada: {expanded_location}")
                
                # Listar archivos importantes
                important_files = ["config.ini", "*.key", "*.pem", "*.crt"]
                for pattern in important_files:
                    import glob
                    files = glob.glob(os.path.join(expanded_location, pattern))
                    for file in files:
                        file_size = os.path.getsize(file)
                        print(f"  - {os.path.basename(file)} ({file_size} bytes)")
            else:
                print(f"✗ Ubicación no encontrada: {expanded_location}")
                
    def check_veyon_logs(self):
        """Verifica logs de Veyon"""
        print("\n5. VERIFICACIÓN DE LOGS DE VEYON...")
        print("-" * 50)
        
        # Buscar logs de Veyon
        log_locations = [
            r"C:\ProgramData\Veyon\logs",
            r"C:\Users\%USERNAME%\AppData\Local\Veyon\logs",
            r"C:\Users\%USERNAME%\AppData\Roaming\Veyon\logs"
        ]
        
        for location in log_locations:
            expanded_location = os.path.expandvars(location)
            if os.path.exists(expanded_location):
                print(f"✓ Logs encontrados en: {expanded_location}")
                
                # Listar archivos de log recientes
                import glob
                log_files = glob.glob(os.path.join(expanded_location, "*.log"))
                for log_file in sorted(log_files, key=os.path.getmtime, reverse=True)[:3]:
                    mod_time = time.ctime(os.path.getmtime(log_file))
                    file_size = os.path.getsize(log_file)
                    print(f"  - {os.path.basename(log_file)} ({file_size} bytes, {mod_time})")
                    
                    # Mostrar últimas líneas del log
                    try:
                        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            if lines:
                                print(f"    Últimas líneas:")
                                for line in lines[-3:]:
                                    print(f"      {line.strip()}")
                    except:
                        pass
            else:
                print(f"✗ Logs no encontrados en: {expanded_location}")
                
    def compare_with_working_pcs(self):
        """Compara con PCs que funcionan"""
        print("\n6. COMPARACIÓN CON PCs QUE FUNCIONAN...")
        print("-" * 50)
        
        print("PCs que deberían funcionar (para comparar):")
        working_pcs = [
            ("PC-00", "192.168.50.122"),
            ("PC-02", "192.168.50.222"),
            ("PC-03", "192.168.50.34"),
            # Agregar más según sea necesario
        ]
        
        for name, ip in working_pcs:
            try:
                # Probar conectividad
                result = subprocess.run(['ping', '-n', '1', ip], 
                                      capture_output=True, timeout=5)
                if result.returncode == 0:
                    print(f"✓ {name} ({ip}): Conectividad OK")
                    
                    # Probar puerto Veyon
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    result = sock.connect_ex((ip, 11100))
                    sock.close()
                    
                    if result == 0:
                        print(f"  ✓ Puerto 11100: ABIERTO")
                    else:
                        print(f"  ✗ Puerto 11100: CERRADO")
                else:
                    print(f"✗ {name} ({ip}): Sin conectividad")
                    
            except Exception as e:
                print(f"✗ Error probando {name}: {e}")
                
    def test_specific_commands(self):
        """Prueba comandos específicos"""
        print("\n7. PRUEBA DE COMANDOS ESPECÍFICOS...")
        print("-" * 50)
        
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
                
            # Probar comando de claves
            result = subprocess.run([
                self.veyon_cli, "authkeys", "list"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✓ Comando 'veyon-cli authkeys list': OK")
                print(f"  Claves: {result.stdout.strip()}")
            else:
                print(f"✗ Comando 'veyon-cli authkeys list': FALLO")
                print(f"  Error: {result.stderr}")
                
            # Probar comando de red
            result = subprocess.run([
                self.veyon_cli, "networkobjects", "list", "computer"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✓ Comando 'veyon-cli networkobjects list computer': OK")
            else:
                print(f"✗ Comando 'veyon-cli networkobjects list computer': FALLO")
                
        except Exception as e:
            print(f"✗ Error probando comandos: {e}")
            
    def provide_specific_solutions(self):
        """Proporciona soluciones específicas para PC-01"""
        print("\n8. SOLUCIONES ESPECÍFICAS PARA PC-01...")
        print("-" * 50)
        
        print("Dado que PC-01 es un clon y tiene la clave pública correcta:")
        print()
        print("1. VERIFICAR DIFERENCIAS CON PCs QUE FUNCIONAN:")
        print("   - Comparar servicios ejecutándose")
        print("   - Comparar archivos de configuración")
        print("   - Comparar logs de Veyon")
        print("   - Verificar diferencias en el registro de Windows")
        print()
        print("2. PROBLEMAS COMUNES EN CLONES:")
        print("   - SID duplicado (usar sysprep)")
        print("   - Configuración de red duplicada")
        print("   - Servicios con configuración duplicada")
        print("   - Archivos de configuración corruptos")
        print()
        print("3. SOLUCIONES ESPECÍFICAS:")
        print("   - Reiniciar servicios de Veyon")
        print("   - Limpiar configuración y recrear")
        print("   - Verificar que no haya conflictos de red")
        print("   - Reinstalar Veyon si es necesario")
        print()
        print("4. COMANDOS DE PRUEBA:")
        print("   - Probar conexión manual desde Veyon Master")
        print("   - Verificar logs específicos de PC-01")
        print("   - Comparar configuración con PC-02 (que funciona)")

def main():
    """Función principal"""
    diagnostic = DiagnosticoProfundoPC01()
    diagnostic.run_diagnostico_profundo()
    diagnostic.provide_specific_solutions()
    
    input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    main()
