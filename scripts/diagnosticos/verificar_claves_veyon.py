#!/usr/bin/env python3
"""
Verificador de Claves Veyon
Script para verificar la configuración correcta de claves públicas/privadas
"""

import subprocess
import os
import glob

class VeyonKeyChecker:
    def __init__(self):
        self.veyon_cli = r"C:\Program Files\Veyon\veyon-cli.exe"
        
    def check_key_configuration(self):
        """Verifica la configuración de claves de Veyon"""
        print("=" * 60)
        print("VERIFICADOR DE CLAVES VEYON")
        print("=" * 60)
        print()
        
        # 1. Verificar configuración actual
        self.check_current_config()
        
        # 2. Verificar archivos de claves
        self.check_key_files()
        
        # 3. Verificar configuración por dispositivo
        self.check_device_configs()
        
        # 4. Proporcionar recomendaciones
        self.provide_recommendations()
        
        print("\n" + "=" * 60)
        print("VERIFICACIÓN COMPLETADA")
        print("=" * 60)
        
    def check_current_config(self):
        """Verifica la configuración actual de Veyon"""
        print("1. VERIFICANDO CONFIGURACIÓN ACTUAL...")
        print("-" * 40)
        
        if not os.path.exists(self.veyon_cli):
            print("✗ veyon-cli.exe no encontrado")
            return
            
        try:
            # Verificar configuración de autenticación
            result = subprocess.run([
                self.veyon_cli, "config", "list"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✓ Configuración de Veyon accesible")
                
                # Buscar configuración de autenticación
                config_lines = result.stdout.split('\n')
                auth_found = False
                
                for line in config_lines:
                    if 'auth' in line.lower() or 'key' in line.lower():
                        print(f"  - {line.strip()}")
                        auth_found = True
                
                if not auth_found:
                    print("⚠ No se encontró configuración de autenticación")
            else:
                print(f"✗ Error accediendo a configuración: {result.stderr}")
                
        except Exception as e:
            print(f"✗ Error verificando configuración: {e}")
            
    def check_key_files(self):
        """Verifica archivos de claves"""
        print("\n2. VERIFICANDO ARCHIVOS DE CLAVES...")
        print("-" * 40)
        
        # Buscar archivos de claves en ubicaciones comunes
        key_locations = [
            r"C:\Users\%USERNAME%\.config\veyon",
            r"C:\ProgramData\Veyon",
            r"C:\Users\%USERNAME%\AppData\Local\Veyon",
            r"C:\Users\%USERNAME%\AppData\Roaming\Veyon"
        ]
        
        for location in key_locations:
            expanded_location = os.path.expandvars(location)
            if os.path.exists(expanded_location):
                print(f"✓ Ubicación encontrada: {expanded_location}")
                
                # Buscar archivos de claves
                key_files = []
                for pattern in ["*.key", "*.pem", "*.crt", "*.pub", "*.priv"]:
                    key_files.extend(glob.glob(os.path.join(expanded_location, pattern)))
                
                if key_files:
                    print(f"  Archivos de claves encontrados:")
                    for key_file in key_files:
                        file_size = os.path.getsize(key_file)
                        print(f"    - {os.path.basename(key_file)} ({file_size} bytes)")
                else:
                    print("  ⚠ No se encontraron archivos de claves")
            else:
                print(f"✗ Ubicación no encontrada: {expanded_location}")
                
    def check_device_configs(self):
        """Verifica configuración por dispositivo"""
        print("\n3. VERIFICANDO CONFIGURACIÓN POR DISPOSITIVO...")
        print("-" * 40)
        
        print("CONFIGURACIÓN CORRECTA:")
        print("┌─────────────────┬─────────────────┬─────────────────┐")
        print("│ Dispositivo     │ Tipo            │ Clave Requerida │")
        print("├─────────────────┼─────────────────┼─────────────────┤")
        print("│ Laptop          │ MAESTRO         │ CLAVE PRIVADA   │")
        print("│ PC-00           │ MAESTRO BACKUP  │ CLAVE PRIVADA   │")
        print("│ PC-01           │ CLIENTE         │ CLAVE PÚBLICA   │")
        print("│ PC-02 a PC-15   │ CLIENTES        │ CLAVE PÚBLICA   │")
        print("└─────────────────┴─────────────────┴─────────────────┘")
        print()
        
        # Verificar servicios en el sistema actual
        self.check_current_services()
        
    def check_current_services(self):
        """Verifica servicios en el sistema actual"""
        print("SERVICIOS EN ESTE SISTEMA:")
        print("-" * 30)
        
        try:
            services = ["VeyonService", "VeyonMaster", "VeyonWorker"]
            
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
                    
        except Exception as e:
            print(f"✗ Error verificando servicios: {e}")
            
    def provide_recommendations(self):
        """Proporciona recomendaciones de configuración"""
        print("\n4. RECOMENDACIONES DE CONFIGURACIÓN...")
        print("-" * 40)
        
        print("PARA CONFIGURAR CORRECTAMENTE LAS CLAVES:")
        print()
        print("1. EN EL LAPTOP (MAESTRO PRINCIPAL):")
        print("   - Generar par de claves: veyon-cli authkeys generate")
        print("   - Exportar clave pública: veyon-cli authkeys export public")
        print("   - Mantener clave privada en el sistema")
        print("   - Ejecutar Veyon Master con clave privada")
        print()
        print("2. EN EL PC-00 (MAESTRO BACKUP):")
        print("   - Importar la MISMA clave privada del laptop")
        print("   - Ejecutar Veyon Master con clave privada")
        print("   - Usar solo cuando laptop no esté disponible")
        print()
        print("3. EN PC-01 a PC-15 (CLIENTES):")
        print("   - Importar SOLO la clave pública")
        print("   - NO ejecutar Veyon Master")
        print("   - Solo ejecutar VeyonWorker (cliente)")
        print()
        print("4. COMANDOS ÚTILES:")
        print("   - Generar claves: veyon-cli authkeys generate")
        print("   - Exportar pública: veyon-cli authkeys export public")
        print("   - Exportar privada: veyon-cli authkeys export private")
        print("   - Importar clave: veyon-cli authkeys import <archivo>")
        print("   - Listar claves: veyon-cli authkeys list")
        print()
        print("5. VERIFICACIÓN:")
        print("   - Laptop debe poder conectar a todos los clientes")
        print("   - PC-00 debe poder conectar a todos los clientes")
        print("   - PC-01 a PC-15 NO deben poder conectar entre sí")
        print("   - Solo los maestros pueden controlar los clientes")

def main():
    """Función principal"""
    checker = VeyonKeyChecker()
    checker.check_key_configuration()
    
    input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    main()
