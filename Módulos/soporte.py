import tkinter as tk
from tkinter import ttk, messagebox
from Config.sets import get_connection

# ==========================================
# LÓGICA DE ACCESO A DATOS (Data Access Layer)
# ==========================================

def obtener_usuarios():
    """Retorna lista de usuarios para el ComboBox del modal: [(ID, Nombre Apellido)]"""
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor()
        # Se busca solo usuarios activos para soporte
        cursor.execute("SELECT ID_Usuario, Nombre + ' ' + ISNULL(Primer_Apellido, '') FROM Usuario WHERE Activo = 1;")
        return [(row[0], row[1].strip()) for row in cursor.fetchall()]
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar usuarios:\n{e}")
        return []
    finally:
        if conn: conn.close()

def obtener_articulos():
    """Retorna lista de artículos para el ComboBox del modal: [(ID, Nombre)]"""
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ID_Articulo, Nombre FROM Articulo;")
        return [(row[0], row[1]) for row in cursor.fetchall()]
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar artículos:\n{e}")
        return []
    finally:
        if conn: conn.close()

def obtener_tickets():
    """
    Retorna todos los tickets haciendo JOIN con Usuario y (opcionalmente) Articulo.
    """
    conn = get_connection()
    if not conn: return []
    tickets = []
    try:
        cursor = conn.cursor()
        query = """
            SELECT 
                t.ID_Ticket,
                u.Nombre + ' ' + ISNULL(u.Primer_Apellido, '') AS Cliente,
                ISNULL(a.Nombre, 'Sin artículo asignado') AS Articulo,
                t.Descripcion_Problema,
                t.Fecha_Creacion,
                t.Estado,
                t.Prioridad
            FROM Ticket t
            INNER JOIN Usuario u ON t.ID_Usuario = u.ID_Usuario
            LEFT JOIN Articulo a ON t.ID_Articulo = a.ID_Articulo
            ORDER BY t.Fecha_Creacion DESC;
        """
        cursor.execute(query)
        filas = cursor.fetchall()
        for fila in filas:
            tickets.append((
                fila.ID_Ticket,
                fila.Cliente.strip(),
                fila.Articulo,
                fila.Descripcion_Problema,
                fila.Fecha_Creacion,
                fila.Estado,
                fila.Prioridad
            ))
    except Exception as e:
        messagebox.showerror("Error de consulta", f"Error al obtener tickets:\n{e}")
    finally:
        if conn: conn.close()
    return tickets

def crear_ticket(id_usuario, id_articulo, descripcion, estado, prioridad, modal):
    """
    Inserta un nuevo ticket en la BD y maneja campos opcionales como ID_Articulo.
    """
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        
        # Opcionalidad de Artículo
        art_val = id_articulo if id_articulo else None
        
        query = """
            INSERT INTO Ticket (ID_Usuario, ID_Articulo, Descripcion_Problema, Fecha_Creacion, Estado, Prioridad)
            VALUES (?, ?, ?, GETDATE(), ?, ?);
        """
        cursor.execute(query, (id_usuario, art_val, descripcion, estado, prioridad))
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Error de inserción", f"Error al crear ticket:\n{e}", parent=modal)
        return False
    finally:
        if conn: conn.close()


# ==========================================
# INTERFAZ DE USUARIO (Presentation Layer)
# ==========================================

class VistaSoporte(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.pack(fill="both", expand=True)

        self.crear_widgets()
        self.cargar_datos()

    def crear_widgets(self):
        # Título
        tk.Label(self, text="Tickets de Soporte", font=("Segoe UI", 18, "bold"), bg="white").pack(anchor="w", pady=(0, 15))
        
        # Frame Botones
        frame_acciones = tk.Frame(self, bg="white")
        frame_acciones.pack(fill="x", pady=5)

        tk.Button(frame_acciones, text="🔄 Recargar", command=self.cargar_datos, font=("Segoe UI", 10), bg="#ecf0f1", relief="flat", padx=10, cursor="hand2").pack(side="left", padx=5)
        
        tk.Button(frame_acciones, text="➕ Nuevo Ticket", command=self.abrir_modal_nuevo_ticket, font=("Segoe UI", 10, "bold"), bg="#3498db", fg="white", relief="flat", padx=10, cursor="hand2").pack(side="left", padx=15)

        # Treeview Módulo
        style = ttk.Style()
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))
        
        columnas = ("id", "cliente", "articulo", "problema", "fecha", "estado", "prioridad")
        self.tabla = ttk.Treeview(self, columns=columnas, show="headings")
        
        # Encabezados
        self.tabla.heading("id", text="ID")
        self.tabla.heading("cliente", text="Cliente")
        self.tabla.heading("articulo", text="Artículo")
        self.tabla.heading("problema", text="Descripción / Problema")
        self.tabla.heading("fecha", text="Fecha")
        self.tabla.heading("estado", text="Estado")
        self.tabla.heading("prioridad", text="Prioridad")

        # Configurar Columnas
        self.tabla.column("id", width=40, anchor="center")
        self.tabla.column("cliente", width=150, anchor="w")
        self.tabla.column("articulo", width=150, anchor="w")
        self.tabla.column("problema", width=300, anchor="w")
        self.tabla.column("fecha", width=130, anchor="center")
        self.tabla.column("estado", width=100, anchor="center")
        self.tabla.column("prioridad", width=90, anchor="center")
        
        # Estilos visuales (tag_configure) solicitados:
        # Abierto -> rojo claro, En proceso -> amarillo claro, Cerrado -> verde claro
        self.tabla.tag_configure("Abierto", background="#f8d7da", foreground="#721c24")
        self.tabla.tag_configure("En proceso", background="#fff3cd", foreground="#856404")
        self.tabla.tag_configure("Cerrado", background="#d4edda", foreground="#155724")
        
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        
        self.tabla.pack(side="left", fill="both", expand=True, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

    def cargar_datos(self):
        for registro in self.tabla.get_children():
            self.tabla.delete(registro)
            
        tickets = obtener_tickets()
        
        if tickets:
            for t in tickets:
                id_ticket, cliente, articulo, descripcion, fecha, estado, prioridad = t
                
                # Format Date si existe
                str_fecha = fecha.strftime("%Y-%m-%d %H:%M") if hasattr(fecha, 'strftime') else str(fecha)
                
                # Pintará automáticamente según el estado
                self.tabla.insert("", "end", values=(id_ticket, cliente, articulo, descripcion, str_fecha, estado, prioridad), tags=(estado,))

    def abrir_modal_nuevo_ticket(self):
        modal = tk.Toplevel(self)
        modal.title("Crear Nuevo Ticket")
        modal.geometry("500x550")
        modal.configure(bg="white")
        modal.grab_set() 
        modal.resizable(False, False)
        
        modal.update_idletasks()
        x = (modal.winfo_screenwidth() // 2) - (500 // 2)
        y = (modal.winfo_screenheight() // 2) - (550 // 2)
        modal.geometry(f"+{x}+{y}")
        
        tk.Label(modal, text="Registro de Problema (Soporte)", font=("Segoe UI", 16, "bold"), bg="white").pack(pady=15)
        
        form_frame = tk.Frame(modal, bg="white")
        form_frame.pack(fill="both", expand=True, padx=30)
        
        form_frame.columnconfigure(0, weight=1, minsize=100)
        form_frame.columnconfigure(1, weight=3)
        
        # Fetch Data for ComboBoxes
        usuarios_db = obtener_usuarios()
        articulos_db = obtener_articulos()
        
        lista_u = [f"{u[0]} - {u[1]}" for u in usuarios_db] if usuarios_db else ["Sin clientes"]
        lista_a = ["Ninguno"] + [f"{a[0]} - {a[1]}" for a in articulos_db] if articulos_db else ["Ninguno"]
        
        # Variables Requeridas
        var_cliente = tk.StringVar()
        var_articulo = tk.StringVar(value="Ninguno")
        var_estado = tk.StringVar(value="Abierto")
        var_prioridad = tk.StringVar(value="Media")
        
        fila = 0
        def agregar_fila(label_text, widget, expand=False):
            nonlocal fila
            tk.Label(form_frame, text=label_text, font=("Segoe UI", 10), bg="white").grid(row=fila, column=0, sticky="nw" if expand else "w", pady=5)
            widget.grid(
                row=fila,
                column=1,
                sticky="ew" if not expand else "nsew",
                pady=5
            )
            fila += 1
            
        # Cliente (Dropdown)
        cmb_cliente = ttk.Combobox(form_frame, textvariable=var_cliente, values=lista_u, state="readonly", font=("Segoe UI", 10))
        if lista_u: cmb_cliente.current(0)
        agregar_fila("Cliente *:", cmb_cliente)
        
        # Artículo (Dropdown - Opcional)
        cmb_articulo = ttk.Combobox(form_frame, textvariable=var_articulo, values=lista_a, state="readonly", font=("Segoe UI", 10))
        agregar_fila("Artículo:", cmb_articulo)
        
        # Descripción/Problema (Caja de Texto Grande)
        txt_descripcion = tk.Text(form_frame, font=("Segoe UI", 10), height=6, wrap="word", relief="groove")
        agregar_fila("Descripción *:", txt_descripcion, expand=True)
        
        # Estado (Combo)
        cmb_estado = ttk.Combobox(form_frame, textvariable=var_estado, values=["Abierto", "En proceso", "Cerrado"], state="readonly", font=("Segoe UI", 10))
        agregar_fila("Estado *:", cmb_estado)
        
        # Prioridad (Combo)
        cmb_prioridad = ttk.Combobox(form_frame, textvariable=var_prioridad, values=["Baja", "Media", "Alta"], state="readonly", font=("Segoe UI", 10))
        agregar_fila("Prioridad *:", cmb_prioridad)
        
        def guardar():
            # Retrieve Values
            cliente_sel = var_cliente.get()
            articulo_sel = var_articulo.get()
            descripcion = txt_descripcion.get("1.0", tk.END).strip()
            estado = var_estado.get()
            prioridad = var_prioridad.get()
            
            # Validation
            if not cliente_sel or cliente_sel == "Sin clientes" or not descripcion:
                messagebox.showwarning("Atención", "El Cliente y la Descripción son obligatorios.", parent=modal)
                return
                
            # Parse IDs from strings "ID - Nombre"
            id_usuario = int(cliente_sel.split(" - ")[0])
            id_articulo = int(articulo_sel.split(" - ")[0]) if articulo_sel != "Ninguno" else None
            
            # Ejecutar Inserción SQL
            exito = crear_ticket(id_usuario, id_articulo, descripcion, estado, prioridad, modal)
            
            if exito:
                messagebox.showinfo("Ticket Creado", "Problema registrado correctamente.", parent=modal)
                modal.destroy()
                self.cargar_datos() 
                
        # Acciones de Modal
        btn_frame = tk.Frame(modal, bg="white")
        btn_frame.pack(fill="x", pady=20, padx=30)
        
        btn_guardar = tk.Button(btn_frame, text="✅ Guardar Ticket", command=guardar, bg="#27ae60", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2")
        btn_guardar.pack(side="left", expand=True, fill="x", padx=(0,5), ipady=5)
        
        btn_cancelar = tk.Button(btn_frame, text="❌ Cancelar", command=modal.destroy, bg="#e74c3c", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2")
        btn_cancelar.pack(side="right", expand=True, fill="x", padx=(5,0), ipady=5)


# Wrapper compatible para que siga funcionando con la estructura original de main.py
def mostrar_soporte(contenedor):
    VistaSoporte(contenedor)
