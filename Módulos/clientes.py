import tkinter as tk
from tkinter import ttk, messagebox
from Config.sets import get_connection

# ==========================================
# LÓGICA DE ACCESO A DATOS (Data Access Layer)
# ==========================================

def obtener_roles():
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        
        query = "SELECT ID_Tipo_Usuario, Rol FROM Tipo_Usuario;"
        cursor.execute(query)
        
        filas = cursor.fetchall()
        return [(fila[0], fila[1]) for fila in filas]

    except Exception as e:
        messagebox.showerror("Error al cargar roles", f"No se pudieron consultar los roles:\n{e}")
        return []

    finally:
        if conn:
            conn.close()

def obtener_clientes():
    """
    Retorna todos los clientes registrados en la tabla Usuario.
    """
    conn = get_connection()
    if not conn:
        return []

    clientes = []
    try:
        cursor = conn.cursor()
        query = """
            SELECT 
                ID_Usuario,
                Nombre + ' ' + Primer_Apellido + ' ' + ISNULL(Segundo_Apellido,'') AS NombreCompleto,
                Telefono,
                CASE 
                    WHEN Activo = 1 THEN 'Activo'
                    ELSE 'Inactivo' 
                END AS Estado
            FROM Usuario;
        """
        cursor.execute(query)
        filas = cursor.fetchall()

        for fila in filas:
            clientes.append((
                fila.ID_Usuario,
                fila.NombreCompleto,
                fila.Telefono if fila.Telefono else "Sin especificar",
                fila.Estado
            ))
            
    except Exception as e:
        messagebox.showerror("Error de consulta", f"Error al obtener los clientes:\n{e}")
    finally:
        if conn:
            conn.close()

    return clientes

def crear_cliente(nombre, ape1, ape2, correo, tel, fec_nac, login, pw, id_rol, activo, modal):
    """
    Inserta un nuevo cliente (Usuario) con TODOS los campos a la base de datos.
    """
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        
        # 1. Validar duplicados en Usuario_Login
        cursor.execute("SELECT COUNT(*) FROM Usuario WHERE Usuario_Login = ?;", (login,))
        if cursor.fetchone()[0] > 0:
            messagebox.showwarning("Usuario duplicado", f"El login '{login}' ya existe.", parent=modal)
            return False

        # 2. Manejo de NULLs para SQL Server
        ape2_val = ape2 if ape2 else None
        correo_val = correo if correo else None
        tel_val = tel if tel else None
        fec_nac_val = fec_nac if fec_nac else None

        # 3. Consulta parametrizada
        query = """
            INSERT INTO Usuario 
            (Nombre, Primer_Apellido, Segundo_Apellido, Correo, Telefono, 
             Fecha_Nacimiento, Usuario_Login, Contrasena, ID_Tipo_Usuario, Activo) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        
        parametros = (
            nombre, ape1, ape2_val, correo_val, tel_val, 
            fec_nac_val, login, pw, id_rol, activo
        )
        
        cursor.execute(query, parametros)
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Error de inserción", f"Ocurrió un error al guardar:\n{e}", parent=modal)
        return False
    finally:
        if conn:
            conn.close()


# ==========================================
# INTERFAZ DE USUARIO (Presentation Layer)
# ==========================================

class VistaClientes(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.pack(fill="both", expand=True)

        self.crear_widgets()
        self.cargar_datos()

    def crear_widgets(self):
        # Título
        tk.Label(self, text="Base de Datos de Clientes", font=("Segoe UI", 18, "bold"), bg="white").pack(anchor="w", pady=(0, 15))
        
        # Frame botones
        frame_acciones = tk.Frame(self, bg="white")
        frame_acciones.pack(fill="x", pady=5)

        tk.Button(frame_acciones, text="🔄 Recargar", command=self.cargar_datos, font=("Segoe UI", 10), bg="#ecf0f1", relief="flat", padx=10, cursor="hand2").pack(side="left", padx=5)
        
        tk.Button(frame_acciones, text="➕ Nuevo Cliente", command=self.abrir_modal_nuevo_cliente, font=("Segoe UI", 10, "bold"), bg="#3498db", fg="white", relief="flat", padx=10, cursor="hand2").pack(side="left", padx=15)

        # Configuración Treeview
        style = ttk.Style()
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))
        
        columnas = ("id", "nombre", "telefono", "status")
        self.tabla = ttk.Treeview(self, columns=columnas, show="headings")
        
        self.tabla.heading("id", text="ID")
        self.tabla.heading("nombre", text="Nombre completo")
        self.tabla.heading("telefono", text="Teléfono")
        self.tabla.heading("status", text="Estado")

        self.tabla.column("id", width=50, anchor="center")
        self.tabla.column("nombre", width=300, anchor="w")
        self.tabla.column("telefono", width=150, anchor="center")
        self.tabla.column("status", width=100, anchor="center")
        
        # Colores por estado (Requerimiento 3)
        self.tabla.tag_configure("Activo", background="#d4edda", foreground="#155724")
        self.tabla.tag_configure("Inactivo", background="#f8d7da", foreground="#721c24")
        
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        
        self.tabla.pack(side="left", fill="both", expand=True, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

    def cargar_datos(self):
        for registro in self.tabla.get_children():
            self.tabla.delete(registro)
            
        clientes = obtener_clientes()
        
        if clientes:
            for c in clientes:
                estado = c[3]
                self.tabla.insert("", "end", values=c, tags=(estado,))

    def abrir_modal_nuevo_cliente(self):
        modal = tk.Toplevel(self)
        modal.title("Crear Nuevo Usuario")
        modal.geometry("450x550")
        modal.configure(bg="white")
        modal.grab_set() 
        modal.resizable(False, False)
        
        # Centrar la ventana secundaria respecto a la pantalla principal (opcional pero profesional)
        modal.update_idletasks()
        x = (modal.winfo_screenwidth() // 2) - (450 // 2)
        y = (modal.winfo_screenheight() // 2) - (550 // 2)
        modal.geometry(f"+{x}+{y}")
        
        tk.Label(modal, text="Registro de Usuario", font=("Segoe UI", 16, "bold"), bg="white").pack(pady=15)
        
        form_frame = tk.Frame(modal, bg="white")
        form_frame.pack(fill="both", expand=True, padx=30)
        
        # Configurar Grid
        form_frame.columnconfigure(0, weight=1, minsize=130)
        form_frame.columnconfigure(1, weight=2)
        
        # Variables de control
        var_nombre = tk.StringVar()
        var_ape1 = tk.StringVar()
        var_ape2 = tk.StringVar()
        var_correo = tk.StringVar()
        var_telefono = tk.StringVar()
        var_fecha_nac = tk.StringVar()
        var_login = tk.StringVar()
        var_pass = tk.StringVar()
        var_activo = tk.IntVar(value=1) # Por defecto Activo
        var_rol_str = tk.StringVar()
        
        # Obtener los roles dinámicos para el combobox
        roles_db = obtener_roles()
        nombres_roles = [r[1] for r in roles_db] if roles_db else ["Sin roles"]

        # ----------------- FILAS DEL FORMULARIO -----------------
        fila = 0
        def agregar_fila(label_text, widget):
            nonlocal fila
            tk.Label(form_frame, text=label_text, font=("Segoe UI", 10), bg="white").grid(row=fila, column=0, sticky="w", pady=5)
            widget.grid(row=fila, column=1, sticky="ew", pady=5)
            fila += 1
            
        # Nombres
        agregar_fila("Nombre *:", ttk.Entry(form_frame, textvariable=var_nombre, font=("Segoe UI", 10)))
        agregar_fila("Primer Apellido *:", ttk.Entry(form_frame, textvariable=var_ape1, font=("Segoe UI", 10)))
        agregar_fila("Segundo Apellido:", ttk.Entry(form_frame, textvariable=var_ape2, font=("Segoe UI", 10)))
        
        # Contacto
        agregar_fila("Correo Electrónico:", ttk.Entry(form_frame, textvariable=var_correo, font=("Segoe UI", 10)))
        agregar_fila("Teléfono:", ttk.Entry(form_frame, textvariable=var_telefono, font=("Segoe UI", 10)))
        
        # Otros datos
        agregar_fila("Fecha Nacimiento:\n(YYYY-MM-DD)", ttk.Entry(form_frame, textvariable=var_fecha_nac, font=("Segoe UI", 10)))
        
        # Credenciales
        agregar_fila("Usuario Login *:", ttk.Entry(form_frame, textvariable=var_login, font=("Segoe UI", 10)))
        
        entry_pass = ttk.Entry(form_frame, textvariable=var_pass, font=("Segoe UI", 10), show="*")
        agregar_fila("Contraseña *:", entry_pass)
        
        # Estado (Checkbutton)
        chk_estado = tk.Checkbutton(form_frame, text="Cuenta Activa", variable=var_activo, bg="white", font=("Segoe UI", 10))
        agregar_fila("Estado:", chk_estado)
        
        # Rol (Combobox)
        cmb_rol = ttk.Combobox(form_frame, textvariable=var_rol_str, values=nombres_roles, state="readonly", font=("Segoe UI", 10))
        # Seleccionar por defecto "Cliente" si existe
        if "Cliente" in nombres_roles:
            cmb_rol.set("Cliente")
        elif nombres_roles:
            cmb_rol.current(0)
        agregar_fila("Rol Asignado *:", cmb_rol)

        # --------------------------------------------------------
        
        def guardar():
            nombre = var_nombre.get().strip()
            ape1 = var_ape1.get().strip()
            ape2 = var_ape2.get().strip()
            correo = var_correo.get().strip()
            tel = var_telefono.get().strip()
            fec_nac = var_fecha_nac.get().strip()
            login = var_login.get().strip()
            pw = var_pass.get().strip()
            activo = var_activo.get()
            rol_sel = var_rol_str.get()
            
            # 1. Validaciones básicas obligatorias
            if not nombre or not ape1 or not login or not pw or not rol_sel or rol_sel == "Sin roles":
                messagebox.showwarning("Atención", "Los campos con (*) y el Rol son obligatorios.", parent=modal)
                return
                
            # 2. Validar correo simple
            if correo and ("@" not in correo or "." not in correo):
                messagebox.showwarning("Correo inválido", "El formato del correo parece ser incorrecto.", parent=modal)
                return
                
            # 3. Buscar el ID del rol seleccionado
            id_rol = next((r[0] for r in roles_db if r[1] == rol_sel), None)
            if not id_rol:
                messagebox.showerror("Error", "No se pudo identificar el ID del rol.", parent=modal)
                return
                
            # 4. Enviar a BD
            exito = crear_cliente(nombre, ape1, ape2, correo, tel, fec_nac, login, pw, id_rol, activo, modal)
            
            if exito:
                messagebox.showinfo("Registro exitoso", f"El usuario {login} fue creado correctamente.", parent=modal)
                modal.destroy()
                self.cargar_datos() 
                
        # Botones inferiores
        btn_frame = tk.Frame(modal, bg="white")
        btn_frame.pack(fill="x", pady=20, padx=30)
        
        btn_guardar = tk.Button(btn_frame, text="✅ Guardar Usuario", command=guardar, bg="#27ae60", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2")
        btn_guardar.pack(side="left", expand=True, fill="x", padx=(0,5), ipady=5)
        
        btn_cancelar = tk.Button(btn_frame, text="❌ Cancelar", command=modal.destroy, bg="#e74c3c", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2")
        btn_cancelar.pack(side="right", expand=True, fill="x", padx=(5,0), ipady=5)


# Wrapper compatible para que siga funcionando con la estructura original de main.py
def mostrar_clientes(contenedor):
    VistaClientes(contenedor)