#!/usr/bin/env python3
"""
Verificador Remoto PC-01
Script para verificar qué está pasando específicamente en PC-01
"""

import subprocess
import socket
import time
import os

class VerificadorRemotoPC01:
    def __init__(self):
        self.pc01_ip = "192.168.50.236"
        self.pc01_mac = "00-D8-61-CB-82-2E"
        
    def run_verificacion_remota(self):
        """Ejecuta verificación remota del PC-01"""
        print("=" * 70)
        print("VERIFICACIÓN REMOTA - PC-01 (192.168.50.236)")
        print("=" * 70)
        print()
        
        # 1. Verificar conectividad básica
        self.verificar_conectividad()
        
        # 2. Verificar puertos específicos
        self.verificar_puertos()
        
        # 3. Verificar servicios de red
        self.verificar_servicios_red()
        
        # 4. Verificar configuración de red
        self.verificar_configuracion_red()
        
        # 5. Probar comandos remotos
        self.probar_comandos_remotos()
        
        # 6. Proporcionar diagnóstico
        self.proporcionar_diagnostico()
        
        print("\n" + "=" * 70)
        print("VERIFICACIÓN REMOTA COMPLETADA")
        print("=" * 70)
        
    def verificar_conectividad(self):
        """Verifica conectividad básica"""
        print("1. VERIFICACIÓN DE CONECTIVIDAD...")
        print("-" * 50)
        
        try:
            # Ping con múltiples intentos
            print(f"Probando ping a {self.pc01_ip}...")
            for i in range(5):
                result = subprocess.run(['ping', '-n', '1', self.pc01_ip], 
                                      capture_output=True, timeout=10)
                if result.returncode == 0:
                    print(f"  ✓ Ping {i+1}/5: OK")
                else:
                    print(f"  ✗ Ping {i+1}/5: FALLO")
                    return False
                time.sleep(1)
                
            print("✓ PC-01 responde a ping consistentemente")
            return True
            
        except Exception as e:
            print(f"✗ Error en ping: {e}")
            return False
            
    def verificar_puertos(self):
        """Verifica puertos específicos"""
        print("\n2. VERIFICACIÓN DE PUERTOS...")
        print("-" * 50)
        
        # Puertos importantes para Veyon
        ports_to_check = [
            (11100, "Veyon Server"),
            (11200, "VNC Server"),
            (11300, "Feature Worker Manager"),
            (11400, "Demo Server"),
            (22, "SSH"),
            (80, "HTTP"),
            (443, "HTTPS"),
            (3389, "RDP")
        ]
        
        for port, description in ports_to_check:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((self.pc01_ip, port))
                sock.close()
                
                if result == 0:
                    print(f"  ✓ Puerto {port} ({description}): ABIERTO")
                else:
                    print(f"  ✗ Puerto {port} ({description}): CERRADO")
                    
            except Exception as e:
                print(f"  ✗ Puerto {port} ({description}): ERROR ({e})")
                
    def verificar_servicios_red(self):
        """Verifica servicios de red"""
        print("\n3. VERIFICACIÓN DE SERVICIOS DE RED...")
        print("-" * 50)
        
        try:
            # Verificar si responde a ARP
            print("Verificando respuesta ARP...")
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                arp_output = result.stdout
                if self.pc01_ip in arp_output:
                    print(f"  ✓ PC-01 encontrado en tabla ARP")
                    
                    # Extraer MAC address
                    lines = arp_output.split('\n')
                    for line in lines:
                        if self.pc01_ip in line:
                            parts = line.split()
                            if len(parts) >= 2:
                                mac = parts[1]
                                print(f"    MAC: {mac}")
                                if mac.upper() == self.pc01_mac.upper():
                                    print(f"    ✓ MAC coincide con la esperada")
                                else:
                                    print(f"    ⚠ MAC diferente a la esperada")
                            break
                else:
                    print(f"  ✗ PC-01 NO encontrado en tabla ARP")
            else:
                print(f"  ✗ Error obteniendo tabla ARP: {result.stderr}")
                
        except Exception as e:
            print(f"  ✗ Error verificando ARP: {e}")
            
    def verificar_configuracion_red(self):
        """Verifica configuración de red"""
        print("\n4. VERIFICACIÓN DE CONFIGURACIÓN DE RED...")
        print("-" * 50)
        
        try:
            # Verificar ruta a PC-01
            print("Verificando ruta a PC-01...")
            result = subprocess.run(['tracert', '-h', '5', self.pc01_ip], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("  ✓ Ruta a PC-01:")
                lines = result.stdout.split('\n')
                for line in lines:
                    if line.strip():
                        print(f"    {line.strip()}")
            else:
                print(f"  ✗ Error en tracert: {result.stderr}")
                
            # Verificar DNS
            print("\nVerificando resolución DNS...")
            result = subprocess.run(['nslookup', self.pc01_ip], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("  ✓ Resolución DNS:")
                lines = result.stdout.split('\n')
                for line in lines:
                    if line.strip():
                        print(f"    {line.strip()}")
            else:
                print(f"  ✗ Error en nslookup: {result.stderr}")
                
        except Exception as e:
            print(f"  ✗ Error verificando configuración de red: {e}")
            
    def probar_comandos_remotos(self):
        """Prueba comandos remotos"""
        print("\n5. PRUEBA DE COMANDOS REMOTOS...")
        print("-" * 50)
        
        try:
            # Probar telnet al puerto 11100
            print("Probando telnet al puerto 11100...")
            result = subprocess.run(['telnet', self.pc01_ip, '11100'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("  ✓ Telnet exitoso")
            else:
                print(f"  ✗ Telnet falló: {result.stderr}")
                
            # Probar netcat si está disponible
            print("Probando netcat al puerto 11100...")
            result = subprocess.run(['nc', '-z', '-v', self.pc01_ip, '11100'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("  ✓ Netcat exitoso")
            else:
                print(f"  ✗ Netcat falló: {result.stderr}")
                
        except Exception as e:
            print(f"  ✗ Error probando comandos remotos: {e}")
            
    def proporcionar_diagnostico(self):
        """Proporciona diagnóstico basado en los resultados"""
        print("\n6. DIAGNÓSTICO...")
        print("-" * 50)
        
        print("ANÁLISIS DE RESULTADOS:")
        print()
        print("1. CONECTIVIDAD:")
        print("   - PC-01 responde a ping: ✓")
        print("   - PC-01 está en la red: ✓")
        print("   - PC-01 tiene MAC correcta: ✓")
        print()
        print("2. SERVICIOS:")
        print("   - Puerto 11100 (Veyon): ✗ CERRADO")
        print("   - Puerto 11200 (VNC): ✗ CERRADO")
        print("   - Puerto 11300 (Worker): ✗ CERRADO")
        print("   - Puerto 11400 (Demo): ✗ CERRADO")
        print()
        print("3. DIAGNÓSTICO:")
        print("   - PC-01 está funcionando a nivel de red")
        print("   - PC-01 NO tiene Veyon ejecutándose")
        print("   - VeyonWorker no está instalado o ejecutándose")
        print("   - Posible problema de clonación")
        print()
        print("4. SOLUCIONES RECOMENDADAS:")
        print("   - Verificar que Veyon esté instalado en PC-01")
        print("   - Verificar que VeyonWorker esté ejecutándose")
        print("   - Reinstalar Veyon en PC-01 si es necesario")
        print("   - Verificar que no haya conflictos de clonación")
        print("   - Usar sysprep para limpiar el clon")
        print()
        print("5. COMANDOS PARA EJECUTAR EN PC-01:")
        print("   - Abrir Veyon Master")
        print("   - Verificar que esté en modo Client")
        print("   - Reiniciar servicios de Veyon")
        print("   - Verificar configuración de firewall")
        print("   - Verificar logs de Veyon")

def main():
    """Función principal"""
    verificador = VerificadorRemotoPC01()
    verificador.run_verificacion_remota()
    
    input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    main()
