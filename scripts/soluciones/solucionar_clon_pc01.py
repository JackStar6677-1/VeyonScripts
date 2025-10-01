#!/usr/bin/env python3
"""
Solucionador de Problemas de Clon - PC-01
Script específico para solucionar problemas comunes en clones de Veyon
"""

import subprocess
import os
import time
import shutil
from typing import List

class SolucionadorClonPC01:
    def __init__(self):
        self.veyon_cli = r"C:\Program Files\Veyon\veyon-cli.exe"
        self.pc01_ip = "192.168.50.236"
        self.pc01_mac = "00-D8-61-CB-82-2E"
        
    def run_solucion_completa(self):
        """Ejecuta solución completa para PC-01 clon"""
        print("=" * 70)
        print("SOLUCIONADOR DE PROBLEMAS DE CLON - PC-01")
        print("=" * 70)
        print()
        
        # 1. Verificar estado actual
        self.verificar_estado_actual()
        
        # 2. Limpiar configuración de Veyon
        self.limpiar_configuracion_veyon()
        
        # 3. Reiniciar servicios
        self.reiniciar_servicios()
        
        # 4. Recrear configuración
        self.recrear_configuracion()
        
        # 5. Verificar funcionamiento
        self.verificar_funcionamiento()
        
        # 6. Proporcionar pasos manuales
        self.proporcionar_pasos_manuales()
        
        print("\n" + "=" * 70)
        print("SOLUCIÓN COMPLETADA")
        print("=" * 70)
        
    def verificar_estado_actual(self):
        """Verifica el estado actual del PC-01"""
        print("1. VERIFICANDO ESTADO ACTUAL...")
        print("-" * 50)
        
        try:
            # Verificar conectividad
            result = subprocess.run(['ping', '-n', '1', self.pc01_ip], 
                                  capture_output=True, timeout=10)
            if result.returncode == 0:
                print("✓ PC-01 responde a ping")
            else:
                print("✗ PC-01 NO responde a ping")
                print("  Verificar conectividad de red antes de continuar")
                return False
                
            # Verificar puerto 11100
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((self.pc01_ip, 11100))
            sock.close()
            
            if result == 0:
                print("✓ Puerto 11100 está abierto")
            else:
                print("✗ Puerto 11100 está cerrado")
                print("  VeyonWorker no está ejecutándose")
                
            return True
            
        except Exception as e:
            print(f"✗ Error verificando estado: {e}")
            return False
            
    def limpiar_configuracion_veyon(self):
        """Limpia la configuración de Veyon"""
        print("\n2. LIMPIANDO CONFIGURACIÓN DE VEYON...")
        print("-" * 50)
        
        if not os.path.exists(self.veyon_cli):
            print("✗ veyon-cli.exe no encontrado")
            return
            
        try:
            # Limpiar objetos de red
            print("Limpiando objetos de red...")
            result = subprocess.run([
                self.veyon_cli, "networkobjects", "clear"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✓ Objetos de red limpiados")
            else:
                print(f"⚠ Error limpiando objetos de red: {result.stderr}")
                
            # Limpiar configuración de autenticación
            print("Limpiando configuración de autenticación...")
            result = subprocess.run([
                self.veyon_cli, "config", "clear", "Authentication"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✓ Configuración de autenticación limpiada")
            else:
                print(f"⚠ Error limpiando autenticación: {result.stderr}")
                
            # Limpiar configuración de servicio
            print("Limpiando configuración de servicio...")
            result = subprocess.run([
                self.veyon_cli, "config", "clear", "Service"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✓ Configuración de servicio limpiada")
            else:
                print(f"⚠ Error limpiando servicio: {result.stderr}")
                
        except Exception as e:
            print(f"✗ Error limpiando configuración: {e}")
            
    def reiniciar_servicios(self):
        """Reinicia los servicios de Veyon"""
        print("\n3. REINICIANDO SERVICIOS...")
        print("-" * 50)
        
        services = ["VeyonService", "VeyonWorker"]
        
        for service in services:
            try:
                print(f"Reiniciando {service}...")
                
                # Detener servicio
                result = subprocess.run([
                    "sc", "stop", service
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    print(f"  ✓ {service} detenido")
                else:
                    print(f"  ⚠ Error deteniendo {service}: {result.stderr}")
                
                # Esperar un momento
                time.sleep(2)
                
                # Iniciar servicio
                result = subprocess.run([
                    "sc", "start", service
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    print(f"  ✓ {service} iniciado")
                else:
                    print(f"  ✗ Error iniciando {service}: {result.stderr}")
                    
            except Exception as e:
                print(f"  ✗ Error con {service}: {e}")
                
    def recrear_configuracion(self):
        """Recrea la configuración de Veyon"""
        print("\n4. RECREANDO CONFIGURACIÓN...")
        print("-" * 50)
        
        if not os.path.exists(self.veyon_cli):
            print("✗ veyon-cli.exe no encontrado")
            return
            
        try:
            # Configurar método de autenticación
            print("Configurando método de autenticación...")
            result = subprocess.run([
                self.veyon_cli, "config", "set", "Authentication/Method", "1"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✓ Método de autenticación configurado")
            else:
                print(f"⚠ Error configurando autenticación: {result.stderr}")
                
            # Configurar directorio de claves públicas
            print("Configurando directorio de claves públicas...")
            result = subprocess.run([
                self.veyon_cli, "config", "set", "Authentication/PublicKeyBaseDir", 
                "%GLOBALAPPDATA%\\keys\\public"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✓ Directorio de claves públicas configurado")
            else:
                print(f"⚠ Error configurando directorio público: {result.stderr}")
                
            # Configurar directorio de claves privadas
            print("Configurando directorio de claves privadas...")
            result = subprocess.run([
                self.veyon_cli, "config", "set", "Authentication/PrivateKeyBaseDir", 
                "%GLOBALAPPDATA%\\keys\\private"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✓ Directorio de claves privadas configurado")
            else:
                print(f"⚠ Error configurando directorio privado: {result.stderr}")
                
            # Crear ubicación
            print("Creando ubicación SalaComputacion...")
            result = subprocess.run([
                self.veyon_cli, "networkobjects", "add", "location", "SalaComputacion"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✓ Ubicación creada")
            else:
                print(f"⚠ Error creando ubicación: {result.stderr}")
                
            # Agregar PC-01
            print("Agregando PC-01...")
            result = subprocess.run([
                self.veyon_cli, "networkobjects", "add", "computer", 
                "PC-01", self.pc01_ip, "SalaComputacion"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✓ PC-01 agregado")
            else:
                print(f"⚠ Error agregando PC-01: {result.stderr}")
                
        except Exception as e:
            print(f"✗ Error recreando configuración: {e}")
            
    def verificar_funcionamiento(self):
        """Verifica el funcionamiento después de la solución"""
        print("\n5. VERIFICANDO FUNCIONAMIENTO...")
        print("-" * 50)
        
        try:
            # Verificar conectividad
            result = subprocess.run(['ping', '-n', '1', self.pc01_ip], 
                                  capture_output=True, timeout=10)
            if result.returncode == 0:
                print("✓ PC-01 responde a ping")
            else:
                print("✗ PC-01 NO responde a ping")
                
            # Verificar puerto 11100
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((self.pc01_ip, 11100))
            sock.close()
            
            if result == 0:
                print("✓ Puerto 11100 está abierto")
            else:
                print("✗ Puerto 11100 está cerrado")
                
            # Verificar configuración
            if os.path.exists(self.veyon_cli):
                result = subprocess.run([
                    self.veyon_cli, "networkobjects", "list", "computer"
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    if "PC-01" in result.stdout:
                        print("✓ PC-01 encontrado en Veyon")
                    else:
                        print("✗ PC-01 NO encontrado en Veyon")
                else:
                    print(f"⚠ Error verificando configuración: {result.stderr}")
                    
        except Exception as e:
            print(f"✗ Error verificando funcionamiento: {e}")
            
    def proporcionar_pasos_manuales(self):
        """Proporciona pasos manuales adicionales"""
        print("\n6. PASOS MANUALES ADICIONALES...")
        print("-" * 50)
        
        print("Si el problema persiste, sigue estos pasos:")
        print()
        print("EN EL PC-01 (192.168.50.236):")
        print("1. Abrir Veyon Master")
        print("2. Verificar que esté en modo 'Client'")
        print("3. Verificar configuración de clave pública:")
        print("   - Debe tener la clave pública")
        print("   - NO debe tener la clave privada")
        print("4. Reiniciar el servicio VeyonWorker")
        print("5. Verificar que no haya firewall bloqueando")
        print()
        print("EN EL LAPTOP (MAESTRO PRINCIPAL):")
        print("1. Abrir Veyon Master")
        print("2. Verificar que tenga la clave privada")
        print("3. Buscar PC-01 en la lista")
        print("4. Hacer clic derecho en PC-01")
        print("5. Seleccionar 'Conectar' o 'Mostrar pantalla'")
        print("6. Verificar logs de Veyon si hay errores")
        print()
        print("EN EL PC-00 (MAESTRO BACKUP):")
        print("1. Abrir Veyon Master")
        print("2. Verificar que tenga la clave privada")
        print("3. Probar conexión a PC-01")
        print("4. Usar solo cuando la laptop no esté disponible")
        print()
        print("VERIFICACIONES ADICIONALES:")
        print("- Verificar que todos los PCs estén en la misma red")
        print("- Verificar que no haya conflictos de IP")
        print("- Verificar que el puerto 11100 esté abierto")
        print("- Verificar que las claves públicas/privadas coincidan")
        print("- Reiniciar PC-01 si es necesario")
        print()
        print("PROBLEMAS COMUNES EN CLONES:")
        print("- SID duplicado (usar sysprep)")
        print("- Configuración de red duplicada")
        print("- Servicios con configuración duplicada")
        print("- Archivos de configuración corruptos")
        print()
        print("SOLUCIONES AVANZADAS:")
        print("- Reinstalar Veyon en PC-01")
        print("- Usar sysprep para limpiar el clon")
        print("- Verificar que no haya conflictos de hardware")
        print("- Comparar configuración con PC-02 que funciona")

def main():
    """Función principal"""
    solucionador = SolucionadorClonPC01()
    solucionador.run_solucion_completa()
    
    input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    main()
