import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import json
import shutil
import sys
try:
    import winreg
except ImportError:
    winreg = None  # Para compatibilidad con otros OS
from pathlib import Path
import subprocess

class RDR2SessionManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎮 RDR2 Session Manager")
        self.root.geometry("900x700")
        self.root.configure(bg='#1a1a1a')

        # Hacer la ventana no redimensionable para mejor portabilidad
        self.root.resizable(True, True)  # Permitir redimensionar para mejor UX
        self.root.minsize(800, 600)      # Tamaño mínimo

        # Centrar ventana en pantalla
        self.center_window()

        # Configuración de estilo
        self.setup_styles()

        # Variables
        self.game_path = tk.StringVar()
        # Guardar configuración en el mismo directorio del ejecutable
        self.sessions_file = self.get_config_path("rdr2_sessions.json")
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

        # Discord link desde variable de entorno o valor por defecto
        self.discord_url = os.environ.get("DISCORD_URL", "https://discord.gg/8HTjHDJ86x")

        # Inicializar
        self.load_sessions()
        self.detect_game_path()
        self.create_ui()
        
    def get_config_path(self, filename):
        """Obtiene la ruta donde guardar archivos de configuración (mismo directorio del EXE)"""
        if getattr(sys, 'frozen', False):
            # Si está compilado como EXE
            app_dir = os.path.dirname(sys.executable)
        else:
            # Si se ejecuta como script
            app_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(app_dir, filename)
    
    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores modernos (tema gaming)
        bg_primary = '#1a1a1a'      # Negro principal
        bg_secondary = '#2d2d2d'    # Gris oscuro
        bg_tertiary = '#3d3d3d'     # Gris medio
        accent_color = '#ff6b35'    # Naranja gaming
        accent_hover = '#ff8c66'    # Naranja hover
        text_primary = '#ffffff'    # Blanco
        text_secondary = '#cccccc'  # Gris claro
        success_color = '#4caf50'   # Verde éxito
        
        # Configurar estilos base
        style.configure('TFrame', background=bg_primary)
        style.configure('TLabel', background=bg_primary, foreground=text_primary, font=('Segoe UI', 9))
        style.configure('Title.TLabel', background=bg_primary, foreground=accent_color, font=('Segoe UI', 18, 'bold'))
        style.configure('Header.TLabel', background=bg_primary, foreground=text_primary, font=('Segoe UI', 11, 'bold'))
        style.configure('Status.TLabel', background=bg_primary, foreground=success_color, font=('Segoe UI', 10, 'bold'))
        
        # Botones modernos
        style.configure('Accent.TButton', 
                       background=accent_color, 
                       foreground='white',
                       font=('Segoe UI', 9, 'bold'),
                       relief='flat',
                       padding=(20, 8))
        style.map('Accent.TButton',
                 background=[('active', accent_hover), ('pressed', '#e55a2b')])
        
        style.configure('Secondary.TButton', 
                       background=bg_tertiary, 
                       foreground=text_primary,
                       font=('Segoe UI', 9),
                       relief='flat',
                       padding=(15, 6))
        style.map('Secondary.TButton',
                 background=[('active', '#4d4d4d'), ('pressed', bg_secondary)])
        
        style.configure('Danger.TButton', 
                       background='#dc3545', 
                       foreground='white',
                       font=('Segoe UI', 9),
                       relief='flat',
                       padding=(15, 6))
        style.map('Danger.TButton',
                 background=[('active', '#c82333'), ('pressed', '#bd2130')])
        
        # Campos de entrada modernos
        style.configure('Modern.TEntry', 
                       fieldbackground=bg_secondary,
                       foreground=text_primary,
                       borderwidth=1,
                       relief='solid',
                       insertcolor=text_primary,
                       font=('Segoe UI', 9))
        style.map('Modern.TEntry',
                 focuscolor=[('focus', accent_color)])
        
        # LabelFrame moderno
        style.configure('Modern.TLabelframe', 
                       background=bg_primary,
                       borderwidth=1,
                       relief='solid',
                       bordercolor=bg_tertiary)
        style.configure('Modern.TLabelframe.Label', 
                       background=bg_primary,
                       foreground=accent_color,
                       font=('Segoe UI', 10, 'bold'))
        
        # Treeview moderno
        style.configure('Modern.Treeview', 
                       background=bg_secondary,
                       foreground=text_primary,
                       fieldbackground=bg_secondary,
                       borderwidth=0,
                       font=('Segoe UI', 9))
        style.configure('Modern.Treeview.Heading', 
                       background=bg_tertiary,
                       foreground=text_primary,
                       relief='flat',
                       font=('Segoe UI', 9, 'bold'))
        style.map('Modern.Treeview.Heading',
                 background=[('active', accent_color)])
        style.map('Modern.Treeview',
                 background=[('selected', accent_color)],
                 foreground=[('selected', 'white')])
        
        # Scrollbar moderna
        style.configure('Modern.Vertical.TScrollbar',
                       background=bg_secondary,
                       troughcolor=bg_primary,
                       borderwidth=0,
                       arrowcolor=text_secondary,
                       darkcolor=bg_secondary,
                       lightcolor=bg_secondary)
        
    def detect_game_path(self):
        """Detecta automáticamente la ruta de instalación de RDR2"""
        paths_to_check = [
            # Steam
            r"C:\Program Files (x86)\Steam\steamapps\common\Red Dead Redemption 2\x64\data",
            r"C:\Program Files\Steam\steamapps\common\Red Dead Redemption 2\x64\data",
            # Epic Games
            r"C:\Program Files\Epic Games\Red Dead Redemption 2\x64\data", 
            r"C:\Program Files (x86)\Epic Games\Red Dead Redemption 2\x64\data",
            # Rockstar Games Launcher
            r"C:\Program Files\Rockstar Games\Red Dead Redemption 2\x64\data",
            r"C:\Program Files (x86)\Rockstar Games\Red Dead Redemption 2\x64\data",
        ]
        
        # Intentar detectar desde Steam Registry primero
        try:
            steam_path = self.get_steam_path()
            if steam_path:
                steam_rdr2_path = os.path.join(steam_path, "steamapps", "common", "Red Dead Redemption 2", "x64", "data")
                if os.path.exists(steam_rdr2_path):
                    self.game_path.set(steam_rdr2_path)
                    print(f"✅ RDR2 detectado automáticamente (Steam): {steam_rdr2_path}")
                    return
        except Exception as e:
            print(f"⚠️ Error detectando Steam: {e}")
        
        # Comprobar rutas predefinidas
        for path in paths_to_check:
            if os.path.exists(path):
                self.game_path.set(path)
                platform = "Steam" if "Steam" in path else "Epic Games" if "Epic" in path else "Rockstar"
                print(f"✅ RDR2 detectado automáticamente ({platform}): {path}")
                return
                
        # Si no se encuentra, dejar vacío
        print("⚠️ RDR2 no detectado automáticamente. Configuración manual requerida.")
        self.game_path.set("")
        
    def get_steam_path(self):
        """Obtiene la ruta de Steam desde el registro"""
        if not winreg:
            return None
            
        try:
            # Intentar 64-bit primero
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam")
            steam_path = winreg.QueryValueEx(key, "InstallPath")[0]
            winreg.CloseKey(key)
            return steam_path
        except:
            try:
                # Intentar 32-bit
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam")
                steam_path = winreg.QueryValueEx(key, "InstallPath")[0]
                winreg.CloseKey(key)
                return steam_path
            except:
                return None
            
    def create_ui(self):
        # Frame principal con padding optimizado
        main_frame = ttk.Frame(self.root, padding="10 10 10 10", style='TFrame')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título principal con estilo gaming
        title_frame = ttk.Frame(main_frame, style='TFrame')
        title_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        title_label = ttk.Label(title_frame, text="🎮 RDR2 SESSION MANAGER", style='Title.TLabel')
        title_label.grid(row=0, column=0, sticky=tk.W)

        # Botón de créditos y Discord alineados a la derecha
        credits_btn = ttk.Button(title_frame, text="ℹ️ Créditos", 
            command=self.show_credits, style='Secondary.TButton')
        credits_btn.grid(row=0, column=1, sticky=tk.E, padx=(0, 0))

        discord_btn = ttk.Button(title_frame, text="🟦 Discord", command=self.open_discord, style='Secondary.TButton')
        discord_btn.grid(row=0, column=2, sticky=tk.E, padx=(8, 0))

        # Expandir el espacio entre el título y el botón
        title_frame.columnconfigure(0, weight=1)
        title_frame.columnconfigure(1, weight=0)
        
        # Subtítulo debajo del título, alineado a la izquierda
        subtitle_label = ttk.Label(title_frame, text="Gestiona tus sesiones privadas con estilo", 
                      font=('Segoe UI', 9), foreground='#cccccc')
        subtitle_label.grid(row=1, column=0, sticky=tk.W, pady=(2, 0))
        
        # Configuración de ruta del juego (mejorada)
        path_frame = ttk.LabelFrame(main_frame, text="🎯 Configuración del Juego", 
                                   padding="8 8 8 8", style='Modern.TLabelframe')
        path_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 8))
        
        ttk.Label(path_frame, text="Ruta de instalación de RDR2:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 4))
        
        path_entry_frame = ttk.Frame(path_frame, style='TFrame')
        path_entry_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 2))
        
        path_entry = ttk.Entry(path_entry_frame, textvariable=self.game_path, width=65, 
                              style='Modern.TEntry', font=('Segoe UI', 9))
        path_entry.grid(row=0, column=0, padx=(0, 15), sticky=(tk.W, tk.E))
        
        browse_btn = ttk.Button(path_entry_frame, text="🔍 Buscar", 
                               command=self.browse_game_path, style='Secondary.TButton')
        browse_btn.grid(row=0, column=1)
        
        path_entry_frame.columnconfigure(0, weight=1)
        
        # Frame para crear nueva sesión (mejorado)
        create_frame = ttk.LabelFrame(main_frame, text="➕ Crear Nueva Sesión", 
                                     padding="8 8 8 8", style='Modern.TLabelframe')
        create_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 8))
        
        # Grid para los campos de entrada
        input_grid = ttk.Frame(create_frame, style='TFrame')
        input_grid.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 6))
        
        ttk.Label(input_grid, text="Nombre de la sesión:", font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=(0, 15))
        ttk.Label(input_grid, text="Clave de sesión:", font=('Segoe UI', 9, 'bold')).grid(row=0, column=1, sticky=tk.W)
        
        self.session_name_var = tk.StringVar()
        name_entry = ttk.Entry(input_grid, textvariable=self.session_name_var, width=25, 
                              style='Modern.TEntry')
        name_entry.grid(row=1, column=0, padx=(0, 15), pady=(5, 0), sticky=(tk.W, tk.E))
        
        self.session_key_var = tk.StringVar()
        key_entry = ttk.Entry(input_grid, textvariable=self.session_key_var, width=35, 
                             style='Modern.TEntry')
        key_entry.grid(row=1, column=1, pady=(5, 0), sticky=(tk.W, tk.E))
        
        input_grid.columnconfigure(0, weight=1)
        input_grid.columnconfigure(1, weight=1)
        
        # Botón para crear sesión alineado a la derecha
        btns_frame = ttk.Frame(create_frame, style='TFrame')
        btns_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.E), pady=(6, 0))

        create_btn = ttk.Button(btns_frame, text="✨ Crear Sesión", 
                               command=self.create_session, style='Accent.TButton')
        create_btn.pack(side=tk.RIGHT)
        
        # Frame para administrar sesiones (mejorado)
        manage_frame = ttk.LabelFrame(main_frame, text="🎛️ Administrar Sesiones", 
                                     padding="8 8 8 8", style='Modern.TLabelframe')
        manage_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 8))

        # Dos columnas: tabla a la izquierda, botones a la derecha
        # Container para la tabla
        table_container = ttk.Frame(manage_frame, style='TFrame')
        table_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 2), pady=(0, 0))

        # Treeview mejorado
        self.sessions_tree = ttk.Treeview(table_container, columns=('name', 'key'), 
                                         show='headings', height=8, style='Modern.Treeview')
        self.sessions_tree.heading('name', text='🎮 Nombre de Sesión')
        self.sessions_tree.heading('key', text='🔑 Clave')
        self.sessions_tree.column('name', width=220, anchor='w')
        self.sessions_tree.column('key', width=350, anchor='w')
        self.sessions_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Scrollbar mejorada
        scrollbar = ttk.Scrollbar(table_container, orient='vertical', 
                                 command=self.sessions_tree.yview, style='Modern.Vertical.TScrollbar')
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.sessions_tree.configure(yscrollcommand=scrollbar.set)

        table_container.columnconfigure(0, weight=1)
        table_container.rowconfigure(0, weight=1)

        # Botones de acción verticales a la derecha
        button_frame = ttk.Frame(manage_frame, style='TFrame')
        button_frame.grid(row=0, column=1, sticky=(tk.N, tk.E), padx=(2, 0))

        activate_btn = ttk.Button(button_frame, text="🚀 Activar Sesión", 
                                 command=self.activate_session, style='Accent.TButton')
        activate_btn.pack(fill='x', pady=(0, 6))

        delete_btn = ttk.Button(button_frame, text="🗑️ Eliminar", 
                               command=self.delete_session, style='Danger.TButton')
        delete_btn.pack(fill='x', pady=(0, 6))

        public_btn = ttk.Button(button_frame, text="🌐 Modo Público", 
                               command=self.activate_public_mode, style='Secondary.TButton')
        public_btn.pack(fill='x')

        # Ajustar columnas del manage_frame
        manage_frame.columnconfigure(0, weight=1)
        manage_frame.columnconfigure(1, weight=0)
        manage_frame.rowconfigure(0, weight=1)
        
        # Frame de estado mejorado
        status_frame = ttk.LabelFrame(main_frame, text="📊 Estado Actual", 
                                     padding="6 6 6 6", style='Modern.TLabelframe')
        status_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 2))
        
        self.status_var = tk.StringVar(value="🌐 Modo Público Activo")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, style='Status.TLabel')
        status_label.grid(row=0, column=0)
        
        # Configurar el grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        manage_frame.columnconfigure(0, weight=1)
        manage_frame.rowconfigure(0, weight=1)
        path_frame.columnconfigure(0, weight=1)
        create_frame.columnconfigure(0, weight=1)
        
        # Cargar sesiones en el treeview
        self.refresh_sessions_list()
        
        # Configurar eventos de teclado y mouse
        self.setup_events()
        
        # Verificar el estado actual al iniciar
        self.check_current_status()
        
    def setup_events(self):
        """Configura eventos de teclado y mouse"""
        # Doble clic en sesión para activar
        self.sessions_tree.bind('<Double-1>', lambda e: self.activate_session())
        
        # Enter para crear sesión
        self.root.bind('<Return>', lambda e: self.create_session() if self.session_name_var.get() or self.session_key_var.get() else None)
        
        # Delete para eliminar sesión seleccionada
        self.sessions_tree.bind('<Delete>', lambda e: self.delete_session())
        
        # F5 para refrescar
        self.root.bind('<F5>', lambda e: self.refresh_sessions_list())
        
    def check_current_status(self):
        """Verifica el estado actual del juego"""
        if not self.game_path.get():
            self.status_var.set("⚠️ Configurar ruta del juego")
            return
            
        startup_path = os.path.join(self.game_path.get(), "startup.meta")
        
        if os.path.exists(startup_path):
            try:
                with open(startup_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Intentar encontrar qué sesión está activa
                    for name, key in self.sessions.items():
                        if key in content:
                            self.status_var.set(f"🔒 Sesión Activa: {name}")
                            return
                    self.status_var.set("🔒 Sesión Privada Activa (Desconocida)")
            except:
                self.status_var.set("🔒 Sesión Privada Activa")
        else:
            self.status_var.set("🌐 Modo Público Activo")
        
    def browse_game_path(self):
        """Permite seleccionar manualmente la ruta del juego"""
        path = filedialog.askdirectory(title="Seleccionar directorio x64/data de RDR2")
        if path:
            self.game_path.set(path)
    
    def open_discord(self):
        """Abre el canal de Discord en el navegador"""
        import webbrowser
        webbrowser.open_new_tab(self.discord_url)
            
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
            messagebox.showerror("❌ Error", "Debe ingresar tanto el nombre como la clave de la sesión")
            return
            
        if name in self.sessions:
            messagebox.showerror("❌ Error", f"Ya existe una sesión con el nombre '{name}'\n\nUse un nombre diferente.")
            return
            
        self.sessions[name] = key
        self.save_sessions()
        self.refresh_sessions_list()
        
        # Limpiar campos
        self.session_name_var.set("")
        self.session_key_var.set("")
        
        messagebox.showinfo("✅ ¡Éxito!", f"Sesión '{name}' creada correctamente\n\n🎯 Ahora puedes activarla desde la lista")
        
    def refresh_sessions_list(self):
        """Actualiza la lista de sesiones en el treeview"""
        # Limpiar treeview
        for item in self.sessions_tree.get_children():
            self.sessions_tree.delete(item)
            
        # Agregar sesiones con iconos
        for name, key in self.sessions.items():
            # Truncar clave si es muy larga para mejor visualización
            display_key = key if len(key) <= 30 else key[:27] + "..."
            self.sessions_tree.insert('', tk.END, values=(f"🎮 {name}", f"🔑 {display_key}"))
            
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

    def show_credits(self):
        """Muestra información de créditos"""
        version = "0.1"
        credits_msg = f"""🎮 RDR2 Session Manager v{version}

        👨‍💻 DESARROLLADOR:
        • Fenshu28 / RacingAudio

        🛠️ TECNOLOGÍAS:
        • Python 3.x
        • Tkinter GUI
        • JSON Storage

        📝 DESCRIPCIÓN:
        Herramienta moderna para gestionar sesiones privadas 
        de Red Dead Redemption 2 de forma rápida y segura.

        🚀 FUNCIONALIDADES DESTACADAS:
        • Detección automática de la instalación de RDR2
        • Interfaz intuitiva y personalizable
        • Creación, activación y eliminación de sesiones privadas
        • Cambio instantáneo entre modo público y privado
        • Atajos de teclado para mayor productividad
        • Soporte multiplataforma (Steam y Epic)
        • Guardado seguro de tus sesiones

        💬 ¿Dudas o sugerencias? Únete al canal de Discord!!

        ¡Gracias por usar RDR2 Session Manager!"""
        
        messagebox.showinfo("ℹ️ Créditos", credits_msg)
            
    def run(self):
        """Ejecuta la aplicación con manejo de errores"""
        try:
            # Configurar el comportamiento al cerrar
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # Mostrar mensaje de bienvenida si es la primera vez
            if not self.sessions:
                self.show_welcome_message()
            
            # Iniciar el loop principal
            self.root.mainloop()
            
        except Exception as e:
            messagebox.showerror("❌ Error Fatal", 
                               f"Error inesperado en la aplicación:\n{str(e)}\n\nLa aplicación se cerrará.")
            
    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        try:
            # Guardar sesiones antes de cerrar
            if hasattr(self, 'sessions'):
                self.save_sessions()
            self.root.destroy()
        except:
            self.root.destroy()
            
    def show_welcome_message(self):
        """Muestra mensaje de bienvenida para nuevos usuarios"""
        welcome_msg = """🎮 ¡Bienvenido a RDR2 Session Manager!

🎯 PRIMEROS PASOS:
1. El programa intentará detectar tu instalación de RDR2 automáticamente
2. Si no la detecta, usa el botón "🔍 Buscar" para seleccionar la carpeta x64/data
3. Crea tus sesiones privadas con nombre y clave
4. ¡Activa y disfruta!

💡 CONSEJOS:
• Doble clic en una sesión para activarla rápidamente
• Presiona F5 para refrescar la lista
• Cierra RDR2 antes de cambiar de sesión

¿Todo claro? ¡Empecemos! 🚀"""
        
        messagebox.showinfo("🎮 ¡Bienvenido!", welcome_msg)

if __name__ == "__main__":
    try:
        app = RDR2SessionManager()
        app.run()
    except Exception as e:
        # Manejo de errores a nivel de aplicación
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Ocultar ventana principal
        messagebox.showerror("❌ Error de Inicio", 
                           f"No se pudo iniciar la aplicación:\n{str(e)}\n\nVerifica que Python y tkinter estén instalados correctamente.")
        root.destroy()