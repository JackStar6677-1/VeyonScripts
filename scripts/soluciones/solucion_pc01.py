#!/usr/bin/env python3
"""
Solución para Problema PC-01
Script específico para resolver el problema de visualización del PC-01
"""

import subprocess
import os
import time

class PC01Solver:
    def __init__(self):
        self.veyon_cli = r"C:\Program Files\Veyon\veyon-cli.exe"
        self.pc01_ip = "192.168.50.236"
        self.pc01_mac = "00-D8-61-CB-82-2E"
        
    def solve_pc01_issue(self):
        """Resuelve el problema del PC-01"""
        print("=" * 60)
        print("SOLUCIONADOR DE PROBLEMAS - PC-01")
        print("=" * 60)
        print()
        
        # 1. Verificar estado actual
        self.check_current_status()
        
        # 2. Limpiar configuración problemática
        self.clean_problematic_config()
        
        # 3. Recrear PC-01 con configuración correcta
        self.recreate_pc01()
        
        # 4. Verificar conexión
        self.verify_connection()
        
        # 5. Probar comandos de Veyon
        self.test_veyon_commands()
        
        print("\n" + "=" * 60)
        print("SOLUCIÓN COMPLETADA")
        print("=" * 60)
        
    def check_current_status(self):
        """Verifica el estado actual del PC-01"""
        print("1. VERIFICANDO ESTADO ACTUAL...")
        print("-" * 40)
        
        try:
            # Verificar si PC-01 está en Veyon
            result = subprocess.run([
                self.veyon_cli, "networkobjects", "list", "computer"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                computers = result.stdout.strip().split('\n')
                computers = [comp.strip() for comp in computers if comp.strip()]
                
                pc01_found = False
                for comp in computers:
                    if self.pc01_ip in comp or "PC-01" in comp:
                        print(f"✓ PC-01 encontrado: {comp}")
                        pc01_found = True
                        break
                
                if not pc01_found:
                    print("⚠ PC-01 no encontrado en Veyon")
            else:
                print(f"✗ Error listando computadoras: {result.stderr}")
                
        except Exception as e:
            print(f"✗ Error verificando estado: {e}")
            
    def clean_problematic_config(self):
        """Limpia configuración problemática"""
        print("\n2. LIMPIANDO CONFIGURACIÓN PROBLEMÁTICA...")
        print("-" * 40)
        
        try:
            # Eliminar PC-01 si existe
            result = subprocess.run([
                self.veyon_cli, "networkobjects", "remove", "computer", "PC-01"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✓ PC-01 removido de Veyon")
            else:
                print(f"⚠ Error removiendo PC-01: {result.stderr}")
                
            # Eliminar cualquier computadora con la IP problemática
            result = subprocess.run([
                self.veyon_cli, "networkobjects", "list", "computer"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                computers = result.stdout.strip().split('\n')
                for comp in computers:
                    if comp.strip() and self.pc01_ip in comp:
                        print(f"Removiendo computadora con IP problemática: {comp}")
                        subprocess.run([
                            self.veyon_cli, "networkobjects", "remove", "computer", comp.strip()
                        ], capture_output=True, timeout=30)
                        
        except Exception as e:
            print(f"✗ Error limpiando configuración: {e}")
            
    def recreate_pc01(self):
        """Recrea PC-01 con configuración correcta"""
        print("\n3. RECREANDO PC-01...")
        print("-" * 40)
        
        try:
            # Asegurar que la ubicación existe
            result = subprocess.run([
                self.veyon_cli, "networkobjects", "add", "location", "SalaComputacion"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✓ Ubicación 'SalaComputacion' verificada")
            else:
                print(f"⚠ Error con ubicación: {result.stderr}")
                
            # Crear PC-01 con configuración específica
            result = subprocess.run([
                self.veyon_cli, "networkobjects", "add", "computer",
                "PC-01", self.pc01_ip, self.pc01_mac, "SalaComputacion"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✓ PC-01 creado correctamente")
                print(f"  IP: {self.pc01_ip}")
                print(f"  MAC: {self.pc01_mac}")
                print(f"  Ubicación: SalaComputacion")
            else:
                print(f"✗ Error creando PC-01: {result.stderr}")
                
        except Exception as e:
            print(f"✗ Error recreando PC-01: {e}")
            
    def verify_connection(self):
        """Verifica la conexión al PC-01"""
        print("\n4. VERIFICANDO CONEXIÓN...")
        print("-" * 40)
        
        try:
            # Probar ping
            result = subprocess.run(['ping', '-n', '1', self.pc01_ip], 
                                  capture_output=True, timeout=10)
            if result.returncode == 0:
                print(f"✓ Ping a {self.pc01_ip}: OK")
            else:
                print(f"✗ Ping a {self.pc01_ip}: FALLO")
                return
                
            # Probar puerto Veyon
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((self.pc01_ip, 11100))
            sock.close()
            
            if result == 0:
                print(f"✓ Puerto 11100 en {self.pc01_ip}: ABIERTO")
            else:
                print(f"✗ Puerto 11100 en {self.pc01_ip}: CERRADO")
                print("  El PC-01 necesita tener Veyon Master ejecutándose")
                
        except Exception as e:
            print(f"✗ Error verificando conexión: {e}")
            
    def test_veyon_commands(self):
        """Prueba comandos específicos de Veyon"""
        print("\n5. PROBANDO COMANDOS DE VEYON...")
        print("-" * 40)
        
        try:
            # Probar comando de estado
            result = subprocess.run([
                self.veyon_cli, "status"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✓ Veyon CLI funcionando correctamente")
            else:
                print(f"✗ Error en Veyon CLI: {result.stderr}")
                
            # Listar computadoras para verificar
            result = subprocess.run([
                self.veyon_cli, "networkobjects", "list", "computer"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                computers = result.stdout.strip().split('\n')
                print(f"✓ Computadoras en Veyon: {len(computers)}")
                for comp in computers:
                    if comp.strip():
                        print(f"  - {comp.strip()}")
            else:
                print(f"✗ Error listando computadoras: {result.stderr}")
                
        except Exception as e:
            print(f"✗ Error probando comandos: {e}")
            
    def provide_manual_steps(self):
        """Proporciona pasos manuales para resolver el problema"""
        print("\n6. PASOS MANUALES ADICIONALES...")
        print("-" * 40)
        
        print("Si el problema persiste, sigue estos pasos:")
        print()
        print("EN EL PC-01 (192.168.50.236) - CLIENTE:")
        print("1. NO abrir Veyon Master (es cliente, no maestro)")
        print("2. Verificar que Veyon CLIENTE esté ejecutándose")
        print("3. Verificar configuración de clave pública:")
        print("   - Debe tener la CLAVE PÚBLICA")
        print("   - NO debe tener la clave privada")
        print("4. Verificar configuración de red:")
        print("   - IP: 192.168.50.236")
        print("   - Puerto: 11100")
        print("5. Reiniciar el servicio VeyonWorker")
        print("6. Verificar que no haya firewall bloqueando")
        print()
        print("EN EL LAPTOP (MAESTRO PRINCIPAL):")
        print("1. Abrir Veyon Master")
        print("2. Verificar que tenga la CLAVE PRIVADA")
        print("3. Buscar PC-01 en la lista")
        print("4. Hacer clic derecho en PC-01")
        print("5. Seleccionar 'Conectar' o 'Mostrar pantalla'")
        print("6. Verificar logs de Veyon si hay errores")
        print()
        print("EN EL PC-00 (MAESTRO BACKUP):")
        print("1. Abrir Veyon Master")
        print("2. Verificar que tenga la CLAVE PRIVADA")
        print("3. Probar conexión a PC-01")
        print("4. Usar solo cuando la laptop no esté disponible")
        print()
        print("VERIFICACIONES ADICIONALES:")
        print("- Verificar que todos los PCs estén en la misma red")
        print("- Verificar que no haya conflictos de IP")
        print("- Verificar que el puerto 11100 esté abierto")
        print("- Verificar que las claves públicas/privadas coincidan")
        print("- Reiniciar PC-01 si es necesario")

def main():
    """Función principal"""
    solver = PC01Solver()
    solver.solve_pc01_issue()
    solver.provide_manual_steps()
    
    input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    main()
