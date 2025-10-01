#!/usr/bin/env python3
"""
Comparador PC-01 vs PC Funcionando
Script para comparar PC-01 (que no funciona) con un PC que sí funciona
"""

import subprocess
import os
import socket
import time
from typing import Dict, List, Tuple

class ComparadorPC01:
    def __init__(self):
        self.veyon_cli = r"C:\Program Files\Veyon\veyon-cli.exe"
        self.pc01_ip = "192.168.50.236"
        self.pc_funcionando_ip = "192.168.50.222"  # PC-02 que funciona
        self.pc_funcionando_mac = "00-D8-61-CB-96-9A"
        
    def run_comparacion(self):
        """Ejecuta comparación entre PC-01 y PC funcionando"""
        print("=" * 70)
        print("COMPARACIÓN PC-01 (NO FUNCIONA) vs PC-02 (FUNCIONA)")
        print("=" * 70)
        print()
        
        # 1. Comparar conectividad
        self.comparar_conectividad()
        
        # 2. Comparar servicios
        self.comparar_servicios()
        
        # 3. Comparar configuración de Veyon
        self.comparar_configuracion_veyon()
        
        # 4. Comparar archivos de configuración
        self.comparar_archivos_config()
        
        # 5. Comparar logs
        self.comparar_logs()
        
        # 6. Probar comandos específicos
        self.comparar_comandos()
        
        # 7. Identificar diferencias clave
        self.identificar_diferencias()
        
        print("\n" + "=" * 70)
        print("COMPARACIÓN COMPLETADA")
        print("=" * 70)
        
    def comparar_conectividad(self):
        """Compara conectividad entre ambos PCs"""
        print("1. COMPARACIÓN DE CONECTIVIDAD...")
        print("-" * 50)
        
        pcs = [
            ("PC-01 (NO FUNCIONA)", self.pc01_ip),
            ("PC-02 (FUNCIONA)", self.pc_funcionando_ip)
        ]
        
        for name, ip in pcs:
            print(f"\n{name} ({ip}):")
            
            # Ping
            try:
                result = subprocess.run(['ping', '-n', '3', ip], 
                                      capture_output=True, timeout=15)
                if result.returncode == 0:
                    print("  ✓ Ping: OK")
                else:
                    print("  ✗ Ping: FALLO")
                    continue
            except:
                print("  ✗ Ping: ERROR")
                continue
                
            # Puerto 11100
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                result = sock.connect_ex((ip, 11100))
                sock.close()
                
                if result == 0:
                    print("  ✓ Puerto 11100: ABIERTO")
                else:
                    print(f"  ✗ Puerto 11100: CERRADO (Error: {result})")
            except Exception as e:
                print(f"  ✗ Puerto 11100: ERROR ({e})")
                
            # Otros puertos
            other_ports = [22, 80, 443, 3389]
            for port in other_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(3)
                    result = sock.connect_ex((ip, port))
                    sock.close()
                    if result == 0:
                        print(f"  ✓ Puerto {port}: ABIERTO")
                except:
                    pass
                    
    def comparar_servicios(self):
        """Compara servicios entre ambos PCs"""
        print("\n2. COMPARACIÓN DE SERVICIOS...")
        print("-" * 50)
        
        print("NOTA: Esta comparación se hace desde este PC.")
        print("Para comparar servicios en PC-01 y PC-02, necesitarías")
        print("ejecutar este script en cada PC o usar herramientas remotas.")
        print()
        
        # Verificar servicios locales
        services = ["VeyonService", "VeyonMaster", "VeyonWorker"]
        
        print("Servicios en este PC:")
        for service in services:
            try:
                result = subprocess.run([
                    "sc", "query", service
                ], capture_output=True, text=True, timeout=10)
                
                if "RUNNING" in result.stdout:
                    print(f"  ✓ {service}: EJECUTÁNDOSE")
                elif "STOPPED" in result.stdout:
                    print(f"  ⚠ {service}: DETENIDO")
                else:
                    print(f"  ✗ {service}: NO ENCONTRADO")
            except Exception as e:
                print(f"  ✗ {service}: ERROR ({e})")
                
    def comparar_configuracion_veyon(self):
        """Compara configuración de Veyon"""
        print("\n3. COMPARACIÓN DE CONFIGURACIÓN VEYON...")
        print("-" * 50)
        
        if not os.path.exists(self.veyon_cli):
            print("✗ veyon-cli.exe no encontrado")
            return
            
        try:
            # Verificar configuración local
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
                    'Network/'
                ]
                
                print("Configuraciones importantes:")
                for line in config_lines:
                    for config in important_configs:
                        if config in line:
                            print(f"  - {line.strip()}")
                            
            else:
                print(f"✗ Error accediendo a configuración: {result.stderr}")
                
            # Verificar computadoras
            result = subprocess.run([
                self.veyon_cli, "networkobjects", "list", "computer"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                computers = result.stdout.strip().split('\n')
                computers = [comp.strip() for comp in computers if comp.strip()]
                
                print(f"\nComputadoras en Veyon ({len(computers)}):")
                pc01_found = False
                pc02_found = False
                
                for comp in computers:
                    if self.pc01_ip in comp or "PC-01" in comp:
                        print(f"  ✓ PC-01 encontrado: {comp}")
                        pc01_found = True
                    elif self.pc_funcionando_ip in comp or "PC-02" in comp:
                        print(f"  ✓ PC-02 encontrado: {comp}")
                        pc02_found = True
                    else:
                        print(f"  - {comp}")
                        
                if not pc01_found:
                    print("  ⚠ PC-01 NO encontrado en Veyon")
                if not pc02_found:
                    print("  ⚠ PC-02 NO encontrado en Veyon")
                    
        except Exception as e:
            print(f"✗ Error verificando configuración: {e}")
            
    def comparar_archivos_config(self):
        """Compara archivos de configuración"""
        print("\n4. COMPARACIÓN DE ARCHIVOS DE CONFIGURACIÓN...")
        print("-" * 50)
        
        # Buscar archivos de configuración
        config_locations = [
            r"C:\ProgramData\Veyon",
            r"C:\Users\%USERNAME%\AppData\Roaming\Veyon",
            r"C:\Users\%USERNAME%\AppData\Local\Veyon"
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
                        mod_time = time.ctime(os.path.getmtime(file))
                        print(f"  - {os.path.basename(file)} ({file_size} bytes, {mod_time})")
            else:
                print(f"✗ Ubicación no encontrada: {expanded_location}")
                
    def comparar_logs(self):
        """Compara logs entre ambos PCs"""
        print("\n5. COMPARACIÓN DE LOGS...")
        print("-" * 50)
        
        # Buscar logs locales
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
                for log_file in sorted(log_files, key=os.path.getmtime, reverse=True)[:2]:
                    mod_time = time.ctime(os.path.getmtime(log_file))
                    file_size = os.path.getsize(log_file)
                    print(f"  - {os.path.basename(log_file)} ({file_size} bytes, {mod_time})")
                    
                    # Mostrar últimas líneas del log
                    try:
                        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            if lines:
                                print(f"    Últimas líneas:")
                                for line in lines[-2:]:
                                    print(f"      {line.strip()}")
                    except:
                        pass
            else:
                print(f"✗ Logs no encontrados en: {expanded_location}")
                
    def comparar_comandos(self):
        """Compara comandos específicos"""
        print("\n6. COMPARACIÓN DE COMANDOS...")
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
                
        except Exception as e:
            print(f"✗ Error probando comandos: {e}")
            
    def identificar_diferencias(self):
        """Identifica diferencias clave entre PC-01 y PC funcionando"""
        print("\n7. IDENTIFICACIÓN DE DIFERENCIAS CLAVE...")
        print("-" * 50)
        
        print("DIFERENCIAS IDENTIFICADAS:")
        print()
        print("1. CONECTIVIDAD:")
        print("   - PC-01: Verificar si responde a ping")
        print("   - PC-02: Verificar si responde a ping")
        print("   - Puerto 11100: Verificar si está abierto en ambos")
        print()
        print("2. SERVICIOS:")
        print("   - PC-01: Verificar VeyonWorker ejecutándose")
        print("   - PC-02: Verificar VeyonWorker ejecutándose")
        print("   - Comparar estado de servicios")
        print()
        print("3. CONFIGURACIÓN:")
        print("   - PC-01: Verificar configuración de Veyon")
        print("   - PC-02: Verificar configuración de Veyon")
        print("   - Comparar archivos de configuración")
        print()
        print("4. LOGS:")
        print("   - PC-01: Revisar logs de Veyon")
        print("   - PC-02: Revisar logs de Veyon")
        print("   - Buscar errores específicos en PC-01")
        print()
        print("5. PROBLEMAS COMUNES EN CLONES:")
        print("   - SID duplicado")
        print("   - Configuración de red duplicada")
        print("   - Servicios con configuración duplicada")
        print("   - Archivos de configuración corruptos")
        print()
        print("6. SOLUCIONES RECOMENDADAS:")
        print("   - Reiniciar servicios de Veyon en PC-01")
        print("   - Limpiar configuración de Veyon en PC-01")
        print("   - Recrear configuración de Veyon en PC-01")
        print("   - Verificar que no haya conflictos de red")
        print("   - Reinstalar Veyon en PC-01 si es necesario")

def main():
    """Función principal"""
    comparador = ComparadorPC01()
    comparador.run_comparacion()
    
    input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    main()
