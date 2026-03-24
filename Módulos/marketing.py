import tkinter as tk
from tkinter import ttk, messagebox
from Config.sets import get_connection

# ==========================================
# LÓGICA DE ACCESO A DATOS (Data Access Layer)
# ==========================================

def obtener_proveedores():
    """
    Consulta la tabla Proveedor para retornar a todos los contactos comerciales registrados.
    """
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor()
        query = "SELECT ID_Proveedor, Nombre, Telefono, Correo FROM Proveedor;"
        cursor.execute(query)
        filas = cursor.fetchall()
        # Retorna el ID, Nombre, y en caso de que Teléfono/Correo sean NULL, evita nulos visuales
        return [(f.ID_Proveedor, f.Nombre, f.Telefono if f.Telefono else "N/A", f.Correo if f.Correo else "N/A") for f in filas]
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar proveedores:\n{e}")
        return []
    finally:
        if conn: conn.close()

def crear_proveedor(nombre, telefono, correo, modal):
    """
    Inserta un nuevo registro en la tabla Proveedor.
    """
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        query = "INSERT INTO Proveedor (Nombre, Telefono, Correo) VALUES (?, ?, ?);"
        
        # Manejo de Teléfono opcional (NULL)
        tel_val = telefono if telefono else None
        
        cursor.execute(query, (nombre, tel_val, correo))
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error al registrar al proveedor:\n{e}", parent=modal)
        return False
    finally:
        if conn: conn.close()

# ==========================================
# INTERFAZ DE USUARIO (Presentation Layer)
# ==========================================

class VistaMarketing(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.pack(fill="both", expand=True)

        self.crear_widgets()
        self.cargar_datos()

    def crear_widgets(self):
        # Título del Módulo
        tk.Label(self, text="Campaña de Marketing - Proveedores", font=("Segoe UI", 18, "bold"), bg="white").pack(anchor="w", pady=(0, 15))
        
        # Opciones Superiores
        frame_acciones = tk.Frame(self, bg="white")
        frame_acciones.pack(fill="x", pady=5)

        tk.Button(frame_acciones, text="🔄 Recargar", command=self.cargar_datos, font=("Segoe UI", 10), bg="#ecf0f1", relief="flat", padx=10, cursor="hand2").pack(side="left", padx=5)
        tk.Button(frame_acciones, text="➕ Nuevo Proveedor", command=self.abrir_modal_nuevo_proveedor, font=("Segoe UI", 10, "bold"), bg="#3498db", fg="white", relief="flat", padx=10, cursor="hand2").pack(side="left", padx=15)

        # Configuración Visual del Treeview
        style = ttk.Style()
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
        # Encabezados en negrita (Requerimiento 3)
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))
        
        columnas = ("id", "nombre", "telefono", "correo")
        self.tabla = ttk.Treeview(self, columns=columnas, show="headings")
        
        self.tabla.heading("id", text="ID")
        self.tabla.heading("nombre", text="Nombre Comercial")
        self.tabla.heading("telefono", text="Teléfono")
        self.tabla.heading("correo", text="Correo Electrónico")

        # Ajuste automático/adecuado de columnas
        self.tabla.column("id", width=50, anchor="center")
        self.tabla.column("nombre", width=250, anchor="w")
        self.tabla.column("telefono", width=150, anchor="center")
        self.tabla.column("correo", width=300, anchor="w")
        
        # Filas alternadas (Requerimiento 3)
        self.tabla.tag_configure("impar", background="#f9f9f9")
        self.tabla.tag_configure("par", background="white")
        
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        
        self.tabla.pack(side="left", fill="both", expand=True, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

    def cargar_datos(self):
        for registro in self.tabla.get_children():
            self.tabla.delete(registro)
            
        proveedores = obtener_proveedores()
        
        if proveedores:
            # i sirve para determinar si es par o impar visualmente
            for i, p in enumerate(proveedores):
                tag = "par" if i % 2 == 0 else "impar"
                self.tabla.insert("", "end", values=p, tags=(tag,))

    def abrir_modal_nuevo_proveedor(self):
        modal = tk.Toplevel(self)
        modal.title("Registro de Contacto (Proveedor)")
        modal.geometry("400x350")
        modal.configure(bg="white")
        modal.grab_set() 
        modal.resizable(False, False)
        
        # Centrado
        modal.update_idletasks()
        x = (modal.winfo_screenwidth() // 2) - (400 // 2)
        y = (modal.winfo_screenheight() // 2) - (350 // 2)
        modal.geometry(f"+{x}+{y}")
        
        tk.Label(modal, text="Nuevo Proveedor", font=("Segoe UI", 16, "bold"), bg="white").pack(pady=15)
        
        form_frame = tk.Frame(modal, bg="white")
        form_frame.pack(fill="both", expand=True, padx=30)
        
        form_frame.columnconfigure(0, weight=1, minsize=80)
        form_frame.columnconfigure(1, weight=3)
        
        var_nombre = tk.StringVar()
        var_telefono = tk.StringVar()
        var_correo = tk.StringVar()
        
        fila = 0
        def agregar_fila(label_text, widget):
            nonlocal fila
            tk.Label(form_frame, text=label_text, font=("Segoe UI", 10), bg="white").grid(row=fila, column=0, sticky="w", pady=5)
            widget.grid(row=fila, column=1, sticky="ew", pady=5)
            fila += 1
            
        agregar_fila("Nombre *:", ttk.Entry(form_frame, textvariable=var_nombre, font=("Segoe UI", 10)))
        agregar_fila("Teléfono:", ttk.Entry(form_frame, textvariable=var_telefono, font=("Segoe UI", 10)))
        agregar_fila("Correo *:", ttk.Entry(form_frame, textvariable=var_correo, font=("Segoe UI", 10)))
        
        def guardar():
            nombre = var_nombre.get().strip()
            tel = var_telefono.get().strip()
            correo = var_correo.get().strip()
            
            # Validación campos vacíos
            if not nombre or not correo:
                messagebox.showwarning("Incompleto", "El Nombre y el Correo son campos obligatorios.", parent=modal)
                return
                
            # Validar formato básico de correo
            if "@" not in correo or "." not in correo:
                messagebox.showwarning("Correo inválido", "Ingrese un formato de correo electrónico válido.", parent=modal)
                return
            
            exito = crear_proveedor(nombre, tel, correo, modal)
            
            if exito:
                messagebox.showinfo("Éxito", f"El proveedor {nombre} ha sido registrado.", parent=modal)
                modal.destroy()
                self.cargar_datos() 
                
        btn_frame = tk.Frame(modal, bg="white")
        btn_frame.pack(fill="x", pady=20, padx=30)
        
        btn_guardar = tk.Button(btn_frame, text="✅ Guardar", command=guardar, bg="#27ae60", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2")
        btn_guardar.pack(side="left", expand=True, fill="x", padx=(0,5), ipady=5)
        
        btn_cancelar = tk.Button(btn_frame, text="❌ Cancelar", command=modal.destroy, bg="#e74c3c", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2")
        btn_cancelar.pack(side="right", expand=True, fill="x", padx=(5,0), ipady=5)

# Integración Oficial
def mostrar_marketing(contenedor):
    """
    Función de entrada para main.py
    """
    VistaMarketing(contenedor)
