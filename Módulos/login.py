import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from Config.sets import get_connection

def validar_usuario(usuario, contrasena):
    """
    Verifica las credenciales en Base de Datos y trae los datos de sesión.
    Retorna tupla: (ID_Usuario, Nombre, ID_Tipo_Usuario, Rol) o None si falla.
    """
    conn = get_connection()
    if not conn: return None
    try:
        cursor = conn.cursor()
        query = """
            SELECT 
                u.ID_Usuario,
                u.Nombre,
                tu.ID_Tipo_Usuario,
                tu.Rol
            FROM Usuario u
            INNER JOIN Tipo_Usuario tu ON u.ID_Tipo_Usuario = tu.ID_Tipo_Usuario
            WHERE u.Usuario_Login = ? AND u.Contrasena = ?;
        """
        cursor.execute(query, (usuario, contrasena))
        resultado = cursor.fetchone()
        
        return resultado if resultado else None
    except Exception as e:
        messagebox.showerror("Error Interno", f"Fallo al validar acceso:\n{e}")
        return None
    finally:
        if conn: conn.close()

def crear_usuario(nombre, apellido1, apellido2, correo, telefono, fecha_nac, usuario, contrasena, modal):
    """
    Añade un usuario nuevo predeterminado al rol 2 (Cliente).
    """
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM Usuario WHERE Usuario_Login = ?;", (usuario,))
        count_docs = cursor.fetchone()
        if count_docs and count_docs[0] > 0:
            messagebox.showwarning("Error", "El usuario ya existe", parent=modal)
            return False

        query = """
            INSERT INTO Usuario 
            (Nombre, Primer_Apellido, Segundo_Apellido, Correo, Telefono, Fecha_Nacimiento, Usuario_Login, Contrasena, ID_Tipo_Usuario)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 2);
        """
        
        ap2_val = apellido2 if apellido2 else None
        tel_val = telefono if telefono else None
        fnac_val = fecha_nac if fecha_nac else None
        
        cursor.execute(query, (nombre, apellido1, ap2_val, correo, tel_val, fnac_val, usuario, contrasena))
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Excepción SQL", f"No se pudo registrar el usuario:\n{e}", parent=modal)
        return False
    finally:
        if conn: conn.close()

# INTERFAZ DE USUARIO (Presentation Layer)

class LoginWindow:
    def __init__(self, root, on_success_callback):
        self.root = root
        self.on_success_callback = on_success_callback
        
        # Contenedor que ocupará toda la pantalla reemplazando todo lo normal
        self.frame = tk.Frame(self.root, bg="#2c3e50")
        self.frame.pack(fill="both", expand=True)
        
        self.crear_widgets()
        
    def crear_widgets(self):
        # Caja de Login limpia y minimalista
        login_box = tk.Frame(self.frame, bg="white", bd=2, relief="groove", padx=40, pady=40)
        login_box.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(login_box, text="ShopEasy", font=("Segoe UI", 24, "bold"), bg="white", fg="#2980b9").pack(pady=(0, 5))
        tk.Label(login_box, text="Portal de Acceso", font=("Segoe UI", 12), bg="white", fg="#7f8c8d").pack(pady=(0, 20))
        
        # Entradas
        tk.Label(login_box, text="Usuario:", font=("Segoe UI", 10, "bold"), bg="white", fg="#34495e").pack(anchor="w")
        self.entry_usu = ttk.Entry(login_box, font=("Segoe UI", 11), width=30)
        self.entry_usu.pack(pady=(0, 15), ipady=3)
        self.entry_usu.focus()
        
        tk.Label(login_box, text="Contraseña:", font=("Segoe UI", 10, "bold"), bg="white", fg="#34495e").pack(anchor="w")
        self.entry_pwd = ttk.Entry(login_box, font=("Segoe UI", 11), width=30, show="*")
        self.entry_pwd.pack(pady=(0, 25), ipady=3)
        
        # Botones Cta
        btn_login = tk.Button(login_box, text="Iniciar Sesión", command=self.hacer_login, font=("Segoe UI", 11, "bold"), bg="#27ae60", fg="white", relief="flat", cursor="hand2")
        btn_login.pack(fill="x", ipady=5, pady=(0, 10))
        
        btn_reg = tk.Button(login_box, text="Registrarse", command=self.abrir_registro, font=("Segoe UI", 10), bg="#ecf0f1", fg="#2c3e50", relief="flat", cursor="hand2")
        btn_reg.pack(fill="x", ipady=3)
        
        # Atajos de Teclado
        self.root.bind('<Return>', lambda event: self.hacer_login())
        
    def hacer_login(self):
        usu = self.entry_usu.get().strip()
        pwd = self.entry_pwd.get().strip()
        
        if not usu or not pwd:
            messagebox.showwarning("Atención", "Campos vacíos detectados. Revisa tus credenciales.")
            return
            
        usuario_db = validar_usuario(usu, pwd)
        if usuario_db:
            mensaje = f"Inicio de sesión exitoso.\nBienvenido, {usuario_db[1]} ({usuario_db[3]})"
            messagebox.showinfo("Acceso Autorizado", mensaje)
            
            # Limpiar atajos antes de salir y borrar frame
            self.root.unbind('<Return>')
            self.frame.destroy()
            
            # Notificar al ruteador del main para que construya la app pertinente
            self.on_success_callback(usuario_db)
        else:
            messagebox.showerror("Acceso Denegado", "Usuario o contraseña inválidos. Inténtalo de nuevo.")
            
    def abrir_registro(self):
        modal = tk.Toplevel(self.root)
        modal.title("Nuevo Registro - Cliente")
        modal.geometry("450x580")
        modal.configure(bg="white")
        modal.grab_set()
        modal.resizable(False, False)
        
        modal.update_idletasks()
        x = (modal.winfo_screenwidth() // 2) - (450 // 2)
        y = (modal.winfo_screenheight() // 2) - (580 // 2)
        modal.geometry(f"+{x}+{y}")
        
        tk.Label(modal, text="Registro ShopEasy", font=("Segoe UI", 18, "bold"), bg="white", fg="#2980b9").pack(pady=15)
        
        form_frame = tk.Frame(modal, bg="white")
        form_frame.pack(fill="both", expand=True, padx=40)
        form_frame.columnconfigure(1, weight=1)
        
        v_nom = tk.StringVar()
        v_ap1 = tk.StringVar()
        v_ap2 = tk.StringVar()
        v_cor = tk.StringVar()
        v_tel = tk.StringVar()
        v_fna = tk.StringVar()
        v_usu = tk.StringVar()
        v_pwd = tk.StringVar()
        
        fila = 0
        def agregar_fila(label, textvariable, es_password=False, es_fecha=False):
            nonlocal fila
            tk.Label(form_frame, text=label, font=("Segoe UI", 10), bg="white").grid(row=fila, column=0, sticky="w", pady=6)
            
            if es_fecha:
                ent = DateEntry(
                    form_frame,
                    textvariable=textvariable,
                    width=20,
                    background='darkblue',
                    foreground='white',
                    borderwidth=2,
                    date_pattern='yyyy-mm-dd',
                    font=("Segoe UI", 10)
                )
            else:
                ent = ttk.Entry(form_frame, textvariable=textvariable, font=("Segoe UI", 10), show="*" if es_password else "")
                
            ent.grid(row=fila, column=1, sticky="ew", pady=6)
            fila += 1
            
        agregar_fila("Nombre *:", v_nom)
        agregar_fila("Primer Apellido *:", v_ap1)
        agregar_fila("Segundo Apellido:", v_ap2)
        agregar_fila("Correo *:", v_cor)
        agregar_fila("Teléfono:", v_tel)
        agregar_fila("Nacimiento *:", v_fna, es_fecha=True)
        agregar_fila("Usuario *:", v_usu)
        agregar_fila("Contraseña *:", v_pwd, es_password=True)
        
        def accionar_registro():
            nom = v_nom.get().strip()
            ap1 = v_ap1.get().strip()
            cor = v_cor.get().strip()
            usu = v_usu.get().strip()
            pwd = v_pwd.get().strip()
            
            if not nom or not ap1 or not cor or not usu or not pwd:
                messagebox.showwarning("Alerta", "Completa todos los campos obligatorios (*) antes de continuar.", parent=modal)
                return
                
            if "@" not in cor or "." not in cor:
                messagebox.showwarning("Validación", "Digita un formato de correo electrónico válido.", parent=modal)
                return
                
            exito = crear_usuario(nom, ap1, v_ap2.get().strip(), cor, v_tel.get().strip(), v_fna.get().strip(), usu, pwd, modal)
            if exito:
                messagebox.showinfo("Completado", "El usuario fue creado y habilitado en el sistema exitosamente.", parent=modal)
                modal.destroy()
                
        tk.Button(modal, text="Verificar y Registrar", command=accionar_registro, bg="#3498db", fg="white", font=("Segoe UI", 11, "bold"), relief="flat", cursor="hand2").pack(fill="x", padx=40, pady=(15, 20), ipady=5)
