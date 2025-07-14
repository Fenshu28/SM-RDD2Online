import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import json
import shutil
import winreg
from pathlib import Path
import subprocess

class RDR2SessionManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("RDR2 Session Manager")
        self.root.geometry("800x600")
        self.root.configure(bg='#2b2b2b')
        
        # Configuración de estilo
        self.setup_styles()
        
        # Variables
        self.game_path = tk.StringVar()
        self.sessions_file = "rdr2_sessions.json"
        self.startup_template = """<?xml version="1.0" encoding="UTF-8"?>
<CDataFileMgr__ContentsOfDataFileXml>
 <disabledFiles />
 <includedXmlFiles itemType="CDataFileMgr__DataFileArray" />
 <includedDataFiles />
 <dataFiles itemType="CDataFileMgr__DataFile">
  <Item>
   <filename>platform:/data/cdimages/scaleform_platform_pc.rpf</filename>
   <fileType>RPF_FILE</fileType>
  </Item>
  <Item>
   <filename>platform:/data/ui/value_conversion.rpf</filename>
   <fileType>RPF_FILE</fileType>
  </Item>
  <Item>
   <filename>platform:/data/ui/widgets.rpf</filename>
   <fileType>RPF_FILE</fileType>
  </Item>
  <Item>
   <filename>platform:/textures/ui/ui_photo_stickers.rpf</filename>
   <fileType>RPF_FILE</fileType>
  </Item>
  <Item>
   <filename>platform:/textures/ui/ui_platform.rpf</filename>
   <fileType>RPF_FILE</fileType>
  </Item>
  <Item>
   <filename>platform:/data/ui/stylesCatalog</filename>
   <fileType>aWeaponizeDisputants</fileType> <!-- collision -->
  </Item>
  <Item>
   <filename>platform:/data/cdimages/scaleform_frontend.rpf</filename>
   <fileType>RPF_FILE_PRE_INSTALL</fileType>
  </Item>
  <Item>
   <filename>platform:/textures/ui/ui_startup_textures.rpf</filename>
   <fileType>RPF_FILE</fileType>
  </Item>
  <Item>
   <filename>platform:/data/ui/startup_data.rpf</filename>
   <fileType>RPF_FILE</fileType>
  </Item>
 </dataFiles>
 <contentChangeSets itemType="CDataFileMgr__ContentChangeSet" />
 <patchFiles />
</CDataFileMgr__ContentsOfDataFileXml>{session_key}"""
        
        # Inicializar
        self.load_sessions()
        self.detect_game_path()
        self.create_ui()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar colores
        style.configure('TFrame', background='#2b2b2b')
        style.configure('TLabel', background='#2b2b2b', foreground='#ffffff')
        style.configure('TButton', background='#404040', foreground='#ffffff')
        style.configure('TEntry', fieldbackground='#404040', foreground='#ffffff')
        style.configure('Treeview', background='#404040', foreground='#ffffff')
        style.configure('Treeview.Heading', background='#505050', foreground='#ffffff')
        
    def detect_game_path(self):
        """Detecta automáticamente la ruta de instalación de RDR2"""
        paths_to_check = [
            # Steam
            r"C:\Program Files (x86)\Steam\steamapps\common\Red Dead Redemption 2\x64\data",
            r"C:\Program Files\Steam\steamapps\common\Red Dead Redemption 2\x64\data",
            # Epic Games
            r"C:\Program Files\Epic Games\Red Dead Redemption 2\x64\data",
            r"C:\Program Files (x86)\Epic Games\Red Dead Redemption 2\x64\data",
        ]
        
        # Intentar detectar desde Steam Registry
        try:
            steam_path = self.get_steam_path()
            if steam_path:
                steam_rdr2_path = os.path.join(steam_path, "steamapps", "common", "Red Dead Redemption 2", "x64", "data")
                if os.path.exists(steam_rdr2_path):
                    self.game_path.set(steam_rdr2_path)
                    return
        except:
            pass
        
        # Comprobar rutas predefinidas
        for path in paths_to_check:
            if os.path.exists(path):
                self.game_path.set(path)
                return
                
        # Si no se encuentra, dejar vacío para selección manual
        self.game_path.set("")
        
    def get_steam_path(self):
        """Obtiene la ruta de Steam desde el registro"""
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam")
            steam_path = winreg.QueryValueEx(key, "InstallPath")[0]
            winreg.CloseKey(key)
            return steam_path
        except:
            return None
            
    def create_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title_label = ttk.Label(main_frame, text="RDR2 Session Manager", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Configuración de ruta del juego
        path_frame = ttk.LabelFrame(main_frame, text="Configuración del Juego", padding="10")
        path_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(path_frame, text="Ruta del juego:").grid(row=0, column=0, sticky=tk.W)
        
        path_entry = ttk.Entry(path_frame, textvariable=self.game_path, width=60)
        path_entry.grid(row=1, column=0, padx=(0, 10), sticky=(tk.W, tk.E))
        
        browse_btn = ttk.Button(path_frame, text="Buscar", command=self.browse_game_path)
        browse_btn.grid(row=1, column=1)
        
        # Frame para crear nueva sesión
        create_frame = ttk.LabelFrame(main_frame, text="Crear Nueva Sesión", padding="10")
        create_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(create_frame, text="Nombre de la sesión:").grid(row=0, column=0, sticky=tk.W)
        self.session_name_var = tk.StringVar()
        ttk.Entry(create_frame, textvariable=self.session_name_var, width=30).grid(row=0, column=1, padx=(10, 0))
        
        ttk.Label(create_frame, text="Clave de sesión:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.session_key_var = tk.StringVar()
        ttk.Entry(create_frame, textvariable=self.session_key_var, width=30).grid(row=1, column=1, padx=(10, 0), pady=(10, 0))
        
        create_btn = ttk.Button(create_frame, text="Crear Sesión", command=self.create_session)
        create_btn.grid(row=2, column=0, columnspan=2, pady=(15, 0))
        
        # Frame para administrar sesiones
        manage_frame = ttk.LabelFrame(main_frame, text="Administrar Sesiones", padding="10")
        manage_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        # Treeview para mostrar sesiones
        self.sessions_tree = ttk.Treeview(manage_frame, columns=('name', 'key'), show='headings', height=8)
        self.sessions_tree.heading('name', text='Nombre de Sesión')
        self.sessions_tree.heading('key', text='Clave')
        self.sessions_tree.column('name', width=200)
        self.sessions_tree.column('key', width=300)
        self.sessions_tree.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Scrollbar para el treeview
        scrollbar = ttk.Scrollbar(manage_frame, orient='vertical', command=self.sessions_tree.yview)
        scrollbar.grid(row=0, column=3, sticky=(tk.N, tk.S))
        self.sessions_tree.configure(yscrollcommand=scrollbar.set)
        
        # Botones de acción
        button_frame = ttk.Frame(manage_frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=(10, 0))
        
        activate_btn = ttk.Button(button_frame, text="Activar Sesión", command=self.activate_session)
        activate_btn.grid(row=0, column=0, padx=(0, 10))
        
        delete_btn = ttk.Button(button_frame, text="Eliminar Sesión", command=self.delete_session)
        delete_btn.grid(row=0, column=1, padx=(0, 10))
        
        public_btn = ttk.Button(button_frame, text="Modo Público", command=self.activate_public_mode)
        public_btn.grid(row=0, column=2)
        
        # Frame de estado
        status_frame = ttk.LabelFrame(main_frame, text="Estado Actual", padding="10")
        status_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.status_var = tk.StringVar(value="Modo Público Activo")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                                font=('Arial', 10, 'bold'), foreground='#00ff00')
        status_label.grid(row=0, column=0)
        
        # Configurar el grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        manage_frame.columnconfigure(0, weight=1)
        manage_frame.rowconfigure(0, weight=1)
        
        # Cargar sesiones en el treeview
        self.refresh_sessions_list()
        
    def browse_game_path(self):
        """Permite seleccionar manualmente la ruta del juego"""
        path = filedialog.askdirectory(title="Seleccionar directorio x64/data de RDR2")
        if path:
            self.game_path.set(path)
            
    def load_sessions(self):
        """Carga las sesiones guardadas desde el archivo JSON"""
        try:
            if os.path.exists(self.sessions_file):
                with open(self.sessions_file, 'r') as f:
                    self.sessions = json.load(f)
            else:
                self.sessions = {}
        except:
            self.sessions = {}
            
    def save_sessions(self):
        """Guarda las sesiones en el archivo JSON"""
        try:
            with open(self.sessions_file, 'w') as f:
                json.dump(self.sessions, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar las sesiones: {str(e)}")
            
    def create_session(self):
        """Crea una nueva sesión"""
        name = self.session_name_var.get().strip()
        key = self.session_key_var.get().strip()
        
        if not name or not key:
            messagebox.showerror("Error", "Debe ingresar un nombre y una clave para la sesión")
            return
            
        if name in self.sessions:
            messagebox.showerror("Error", "Ya existe una sesión con ese nombre")
            return
            
        self.sessions[name] = key
        self.save_sessions()
        self.refresh_sessions_list()
        
        # Limpiar campos
        self.session_name_var.set("")
        self.session_key_var.set("")
        
        messagebox.showinfo("Éxito", f"Sesión '{name}' creada correctamente")
        
    def refresh_sessions_list(self):
        """Actualiza la lista de sesiones en el treeview"""
        # Limpiar treeview
        for item in self.sessions_tree.get_children():
            self.sessions_tree.delete(item)
            
        # Agregar sesiones
        for name, key in self.sessions.items():
            self.sessions_tree.insert('', tk.END, values=(name, key))
            
    def activate_session(self):
        """Activa la sesión seleccionada"""
        selection = self.sessions_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Debe seleccionar una sesión")
            return
            
        if not self.game_path.get():
            messagebox.showerror("Error", "Debe configurar la ruta del juego")
            return
            
        if not os.path.exists(self.game_path.get()):
            messagebox.showerror("Error", "La ruta del juego no existe")
            return
            
        # Obtener datos de la sesión seleccionada
        item = self.sessions_tree.item(selection[0])
        session_name = item['values'][0]
        session_key = item['values'][1]
        
        # Generar archivo startup.meta
        startup_content = self.startup_template.format(session_key=session_key)
        startup_path = os.path.join(self.game_path.get(), "startup.meta")
        
        try:
            with open(startup_path, 'w', encoding='utf-8') as f:
                f.write(startup_content)
            
            self.status_var.set(f"Sesión Privada Activa: {session_name}")
            messagebox.showinfo("Éxito", f"Sesión '{session_name}' activada correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo activar la sesión: {str(e)}")
            
    def delete_session(self):
        """Elimina la sesión seleccionada"""
        selection = self.sessions_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Debe seleccionar una sesión")
            return
            
        item = self.sessions_tree.item(selection[0])
        session_name = item['values'][0]
        
        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar la sesión '{session_name}'?"):
            del self.sessions[session_name]
            self.save_sessions()
            self.refresh_sessions_list()
            messagebox.showinfo("Éxito", f"Sesión '{session_name}' eliminada correctamente")
            
    def activate_public_mode(self):
        """Activa el modo público eliminando el archivo startup.meta"""
        if not self.game_path.get():
            messagebox.showerror("Error", "Debe configurar la ruta del juego")
            return
            
        startup_path = os.path.join(self.game_path.get(), "startup.meta")
        
        try:
            if os.path.exists(startup_path):
                os.remove(startup_path)
                
            self.status_var.set("Modo Público Activo")
            messagebox.showinfo("Éxito", "Modo público activado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo activar el modo público: {str(e)}")
            
    def run(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()

if __name__ == "__main__":
    app = RDR2SessionManager()
    app.run()