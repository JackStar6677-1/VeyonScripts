#!/usr/bin/env python3
"""
GUI Simplificada para Mapeo Físico de Veyon
Versión simplificada con drag & drop funcional
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
import tempfile
import csv
from typing import List, Dict
import json

class PhysicalMappingGUISimple:
    def __init__(self, root):
        self.root = root
        self.root.title("Veyon - Mapeo Físico de PCs")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.scanned_devices = []
        self.physical_order = []
        self.veyon_cli = r"C:\Program Files\Veyon\veyon-cli.exe"
        
        # Crear interfaz
        self.create_widgets()
        
    def create_widgets(self):
        """Crea todos los widgets de la interfaz"""
        
        # Título principal
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill='x', padx=10, pady=5)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="Veyon - Mapeo Físico de PCs", 
                              font=('Arial', 16, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(expand=True)
        
        # Frame principal con dos paneles
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Panel izquierdo - Dispositivos escaneados
        left_frame = tk.LabelFrame(main_frame, text="Dispositivos Detectados", 
                                  font=('Arial', 12, 'bold'), bg='#f0f0f0')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Lista de dispositivos escaneados con scroll
        list_frame = tk.Frame(left_frame, bg='#f0f0f0')
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.scanned_listbox = tk.Listbox(list_frame, font=('Consolas', 10), 
                                         selectmode=tk.SINGLE, height=15)
        self.scanned_listbox.pack(side='left', fill='both', expand=True)
        
        scrollbar1 = tk.Scrollbar(list_frame, orient='vertical')
        scrollbar1.pack(side='right', fill='y')
        self.scanned_listbox.config(yscrollcommand=scrollbar1.set)
        scrollbar1.config(command=self.scanned_listbox.yview)
        
        # Panel derecho - Orden físico
        right_frame = tk.LabelFrame(main_frame, text="Orden Físico (Doble clic para agregar)", 
                                   font=('Arial', 12, 'bold'), bg='#f0f0f0')
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Lista del orden físico
        order_frame = tk.Frame(right_frame, bg='#f0f0f0')
        order_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.physical_listbox = tk.Listbox(order_frame, font=('Consolas', 10), 
                                          selectmode=tk.SINGLE, height=15)
        self.physical_listbox.pack(side='left', fill='both', expand=True)
        
        scrollbar2 = tk.Scrollbar(order_frame, orient='vertical')
        scrollbar2.pack(side='right', fill='y')
        self.physical_listbox.config(yscrollcommand=scrollbar2.set)
        scrollbar2.config(command=self.physical_listbox.yview)
        
        # Frame para los botones de control
        control_frame = tk.Frame(self.root, bg='#f0f0f0')
        control_frame.pack(fill='x', padx=10, pady=5)
        
        # Botones
        btn_scan = tk.Button(control_frame, text="🔍 Escanear Red", 
                           command=self.scan_network, font=('Arial', 10, 'bold'),
                           bg='#3498db', fg='white', padx=20, pady=5)
        btn_scan.pack(side='left', padx=5)
        
        btn_add = tk.Button(control_frame, text="➕ Agregar Seleccionado", 
                          command=self.add_selected, font=('Arial', 10, 'bold'),
                          bg='#27ae60', fg='white', padx=20, pady=5)
        btn_add.pack(side='left', padx=5)
        
        btn_remove = tk.Button(control_frame, text="➖ Quitar Seleccionado", 
                             command=self.remove_selected, font=('Arial', 10, 'bold'),
                             bg='#e74c3c', fg='white', padx=20, pady=5)
        btn_remove.pack(side='left', padx=5)
        
        btn_up = tk.Button(control_frame, text="⬆️ Subir", 
                         command=self.move_up, font=('Arial', 10, 'bold'),
                         bg='#f39c12', fg='white', padx=20, pady=5)
        btn_up.pack(side='left', padx=5)
        
        btn_down = tk.Button(control_frame, text="⬇️ Bajar", 
                           command=self.move_down, font=('Arial', 10, 'bold'),
                           bg='#f39c12', fg='white', padx=20, pady=5)
        btn_down.pack(side='left', padx=5)
        
        btn_clear = tk.Button(control_frame, text="🗑️ Limpiar Orden", 
                            command=self.clear_physical_order, font=('Arial', 10, 'bold'),
                            bg='#e74c3c', fg='white', padx=20, pady=5)
        btn_clear.pack(side='left', padx=5)
        
        btn_update = tk.Button(control_frame, text="💾 Actualizar Veyon", 
                             command=self.update_veyon, font=('Arial', 10, 'bold'),
                             bg='#27ae60', fg='white', padx=20, pady=5)
        btn_update.pack(side='left', padx=5)
        
        btn_save = tk.Button(control_frame, text="💾 Guardar Mapeo", 
                           command=self.save_mapping, font=('Arial', 10, 'bold'),
                           bg='#9b59b6', fg='white', padx=20, pady=5)
        btn_save.pack(side='left', padx=5)
        
        btn_load = tk.Button(control_frame, text="📁 Cargar Mapeo", 
                           command=self.load_mapping, font=('Arial', 10, 'bold'),
                           bg='#9b59b6', fg='white', padx=20, pady=5)
        btn_load.pack(side='left', padx=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Listo para escanear la red")
        status_bar = tk.Label(self.root, textvariable=self.status_var, 
                             relief='sunken', anchor='w', bg='#ecf0f1')
        status_bar.pack(side='bottom', fill='x')
        
        # Configurar eventos
        self.scanned_listbox.bind('<Double-Button-1>', self.add_selected)
        self.physical_listbox.bind('<Double-Button-1>', self.remove_selected)
        
    def scan_network(self):
        """Escanea la red usando WakeMeOnLAN"""
        self.status_var.set("Escaneando red...")
        self.root.update()
        
        try:
            # Buscar WakeMeOnLAN
            wakemeonlan_path = self.find_wakemeonlan()
            if not wakemeonlan_path:
                messagebox.showerror("Error", "WakeMeOnLAN no encontrado")
                return
                
            # Crear archivo temporal
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, "wake_me_on_lan_scan.csv")
            
            # Ejecutar WakeMeOnLAN
            cmd = [wakemeonlan_path, "/scan", "/scomma", temp_file]
            result = subprocess.run(cmd, capture_output=True, timeout=120, 
                                  creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            
            if result.returncode != 0:
                messagebox.showerror("Error", f"Error escaneando: {result.stderr}")
                return
                
            # Leer resultados
            if not os.path.exists(temp_file):
                messagebox.showerror("Error", "Archivo de resultados no encontrado")
                return
                
            self.scanned_devices = []
            with open(temp_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('IP Address') and row.get('MAC Address'):
                        device = {
                            'ip': row['IP Address'],
                            'mac': row['MAC Address'],
                            'name': row.get('Computer Name', 'Unknown'),
                            'original_name': row.get('Computer Name', 'Unknown')
                        }
                        self.scanned_devices.append(device)
            
            # Actualizar lista
            self.update_scanned_list()
            
            # Limpiar archivo temporal
            try:
                os.remove(temp_file)
            except:
                pass
                
            self.status_var.set(f"Escaneo completado: {len(self.scanned_devices)} dispositivos encontrados")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error durante el escaneo: {e}")
            self.status_var.set("Error durante el escaneo")
            
    def find_wakemeonlan(self):
        """Busca WakeMeOnLAN en ubicaciones comunes"""
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "..", "WakeMeOnLAN.exe"),
            "WakeMeOnLAN.exe",
            r"C:\Users\pablo\Documentos\WakeMeOnLan\WakeMeOnLAN.exe",
        ]
        
        for path in possible_paths:
            if os.path.isfile(path):
                return path
        return None
        
    def update_scanned_list(self):
        """Actualiza la lista de dispositivos escaneados"""
        self.scanned_listbox.delete(0, tk.END)
        
        for i, device in enumerate(self.scanned_devices):
            # Verificar si tiene Veyon
            has_veyon = self.test_veyon_client(device['ip'])
            veyon_status = "✓ VEYON" if has_veyon else "✗ NO VEYON"
            
            item_text = f"{device['ip']:15} | {device['mac']:17} | {device['name']:20} | {veyon_status}"
            self.scanned_listbox.insert(tk.END, item_text)
            
    def test_veyon_client(self, ip):
        """Prueba si un cliente tiene Veyon instalado"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((ip, 11100))
            sock.close()
            return result == 0
        except:
            return False
            
    def add_selected(self, event=None):
        """Agrega el dispositivo seleccionado al orden físico"""
        selection = self.scanned_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona un dispositivo de la lista izquierda")
            return
            
        device_index = selection[0]
        device = self.scanned_devices[device_index]
        
        # Agregar al orden físico
        self.physical_order.append(device)
        
        # Actualizar lista del orden físico
        self.update_physical_list()
        
        # Remover de la lista de escaneados
        self.scanned_listbox.delete(device_index)
        self.scanned_devices.pop(device_index)
        
        self.status_var.set(f"Agregado PC-{len(self.physical_order)-1:02d} al orden físico")
        
    def remove_selected(self, event=None):
        """Remueve el dispositivo seleccionado del orden físico"""
        selection = self.physical_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona un dispositivo del orden físico")
            return
            
        device_index = selection[0]
        device = self.physical_order[device_index]
        
        # Remover del orden físico
        self.physical_order.pop(device_index)
        
        # Actualizar lista del orden físico
        self.update_physical_list()
        
        # Agregar de vuelta a la lista de escaneados
        self.scanned_devices.append(device)
        self.update_scanned_list()
        
        self.status_var.set("Dispositivo removido del orden físico")
        
    def move_up(self):
        """Mueve el elemento seleccionado hacia arriba"""
        selection = self.physical_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona un dispositivo del orden físico")
            return
            
        index = selection[0]
        if index > 0:
            # Intercambiar elementos
            self.physical_order[index], self.physical_order[index-1] = \
                self.physical_order[index-1], self.physical_order[index]
            
            # Actualizar lista
            self.update_physical_list()
            
            # Mantener selección
            self.physical_listbox.selection_set(index-1)
            
    def move_down(self):
        """Mueve el elemento seleccionado hacia abajo"""
        selection = self.physical_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona un dispositivo del orden físico")
            return
            
        index = selection[0]
        if index < len(self.physical_order) - 1:
            # Intercambiar elementos
            self.physical_order[index], self.physical_order[index+1] = \
                self.physical_order[index+1], self.physical_order[index]
            
            # Actualizar lista
            self.update_physical_list()
            
            # Mantener selección
            self.physical_listbox.selection_set(index+1)
            
    def update_physical_list(self):
        """Actualiza la lista del orden físico"""
        self.physical_listbox.delete(0, tk.END)
        
        for i, device in enumerate(self.physical_order):
            has_veyon = self.test_veyon_client(device['ip'])
            veyon_status = "✓ VEYON" if has_veyon else "✗ NO VEYON"
            
            item_text = f"PC-{i:02d}: {device['ip']:15} | {device['mac']:17} | {device['name']:20} | {veyon_status}"
            self.physical_listbox.insert(tk.END, item_text)
            
    def clear_physical_order(self):
        """Limpia el orden físico"""
        # Devolver todos los dispositivos a la lista de escaneados
        self.scanned_devices.extend(self.physical_order)
        self.physical_order.clear()
        
        # Actualizar listas
        self.update_scanned_list()
        self.update_physical_list()
        
        self.status_var.set("Orden físico limpiado")
        
    def update_veyon(self):
        """Actualiza Veyon con el orden físico configurado"""
        if not self.physical_order:
            messagebox.showwarning("Advertencia", "No hay dispositivos en el orden físico")
            return
            
        if not os.path.exists(self.veyon_cli):
            messagebox.showerror("Error", "Veyon no encontrado")
            return
            
        try:
            self.status_var.set("Actualizando Veyon...")
            self.root.update()
            
            # Eliminar computadoras existentes
            self.clear_existing_computers()
            
            # Crear ubicación
            result = subprocess.run([
                self.veyon_cli, "networkobjects", "add", "location", "SalaComputacion"
            ], capture_output=True, timeout=30)
            
            # Agregar computadoras en orden físico
            added_count = 0
            for i, device in enumerate(self.physical_order):
                result = subprocess.run([
                    self.veyon_cli, "networkobjects", "add", "computer",
                    f"PC-{i:02d}", device['ip'], device['mac'], "SalaComputacion"
                ], capture_output=True, timeout=30)
                
                if result.returncode == 0:
                    added_count += 1
                    
            messagebox.showinfo("Éxito", f"Veyon actualizado: {added_count} computadoras agregadas")
            self.status_var.set(f"Veyon actualizado: {added_count} computadoras")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error actualizando Veyon: {e}")
            self.status_var.set("Error actualizando Veyon")
            
    def clear_existing_computers(self):
        """Elimina computadoras existentes de Veyon"""
        try:
            result = subprocess.run([
                self.veyon_cli, "networkobjects", "list", "computer"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                computers = result.stdout.strip().split('\n')
                computers = [comp.strip() for comp in computers if comp.strip()]
                
                for computer in computers:
                    subprocess.run([
                        self.veyon_cli, "networkobjects", "remove", "computer", computer
                    ], capture_output=True, timeout=30)
                    
        except Exception as e:
            print(f"Error eliminando computadoras: {e}")
            
    def save_mapping(self):
        """Guarda el mapeo físico a un archivo"""
        if not self.physical_order:
            messagebox.showwarning("Advertencia", "No hay mapeo para guardar")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                mapping_data = {
                    'devices': self.physical_order,
                    'physical_order': list(range(len(self.physical_order)))
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(mapping_data, f, indent=2, ensure_ascii=False)
                    
                messagebox.showinfo("Éxito", f"Mapeo guardado en: {filename}")
                self.status_var.set(f"Mapeo guardado: {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error guardando mapeo: {e}")
                
    def load_mapping(self):
        """Carga un mapeo físico desde un archivo"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    mapping_data = json.load(f)
                    
                # Limpiar orden actual
                self.clear_physical_order()
                
                # Cargar dispositivos
                self.physical_order = mapping_data['devices']
                
                # Actualizar listas
                self.update_physical_list()
                
                messagebox.showinfo("Éxito", f"Mapeo cargado desde: {filename}")
                self.status_var.set(f"Mapeo cargado: {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando mapeo: {e}")

def main():
    """Función principal"""
    root = tk.Tk()
    app = PhysicalMappingGUISimple(root)
    root.mainloop()

if __name__ == "__main__":
    main()
