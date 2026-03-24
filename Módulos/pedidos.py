import tkinter as tk
from tkinter import ttk, messagebox
from Config.sets import get_connection
from Módulos.crudpedido import eliminar_pedido, actualizar_pedido


def obtener_pedidos():
    """
    Retorna todos los pedidos realizando un JOIN entre Pedido y Usuario.
    Ordenado por fecha descendente.
    """
    conn = get_connection()
    if not conn:
        return []

    pedidos = []
    try:
        cursor = conn.cursor()
        query = """
            SELECT 
                p.ID_Pedido,
                u.Nombre + ' ' + ISNULL(u.Primer_Apellido, '') AS Cliente,
                p.Fecha_Pedido,
                p.Total,
                p.Estado
            FROM Pedido p
            INNER JOIN Usuario u ON p.ID_Usuario = u.ID_Usuario
            ORDER BY p.Fecha_Pedido DESC;
        """
        cursor.execute(query)
        filas = cursor.fetchall()

        for fila in filas:
            pedidos.append((
                fila.ID_Pedido,
                fila.Cliente,
                fila.Fecha_Pedido,
                fila.Total,
                fila.Estado
            ))
            
    except Exception as e:
        messagebox.showerror("Error de consulta", f"Error al obtener los pedidos:\n{e}")
    finally:
        if conn:
            conn.close()

    return pedidos


class VistaPedidos(tk.Frame):
    """
    Clase para englobar la vista de Pedidos en la interfaz.
    """
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.pack(fill="both", expand=True)

        self.crear_widgets()
        self.cargar_datos()

    def crear_widgets(self):
        # Título principal
        tk.Label(self, text="Gestión de Pedidos", font=("Segoe UI", 18, "bold"), bg="white").pack(anchor="w", pady=(0, 15))
        
        # Contenedor de botones superiores
        frame_acciones = tk.Frame(self, bg="white")
        frame_acciones.pack(fill="x", pady=5)

        tk.Button(frame_acciones, text="🔄 Recargar", command=self.cargar_datos, font=("Segoe UI", 10), bg="#ecf0f1", relief="flat", padx=10, cursor="hand2").pack(side="left", padx=5)
        
        tk.Button(frame_acciones, text="🗑️ Eliminar Pedido", command=self.borrar_seleccionado, font=("Segoe UI", 10, "bold"), bg="#e74c3c", fg="white", relief="flat", padx=10, cursor="hand2").pack(side="right", padx=15)
        tk.Button(frame_acciones, text="📝 Actualizar Estado", command=self.actualizar_seleccionado, font=("Segoe UI", 10, "bold"), bg="#f39c12", fg="white", relief="flat", padx=10, cursor="hand2").pack(side="right", padx=10)
        
        # Configuración de la tabla (Treeview)
        style = ttk.Style()
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))
        
        columnas = ("id", "cliente", "fecha", "total", "estado")
        self.tabla = ttk.Treeview(self, columns=columnas, show="headings")
        
        # Encabezados
        self.tabla.heading("id", text="ID")
        self.tabla.heading("cliente", text="Cliente")
        self.tabla.heading("fecha", text="Fecha de Pedido")
        self.tabla.heading("total", text="Total")
        self.tabla.heading("estado", text="Estado")

        # Ajuste de comportamiento de las columnas
        self.tabla.column("id", width=60, anchor="center")
        self.tabla.column("cliente", width=250, anchor="w")
        self.tabla.column("fecha", width=160, anchor="center")
        self.tabla.column("total", width=120, anchor="e")  # Montos suelen alinearse a la derecha
        self.tabla.column("estado", width=130, anchor="center")
        
        # Colores personalizados usando tag_configure
        self.tabla.tag_configure("Pendiente", background="#fff3cd", foreground="#856404")
        self.tabla.tag_configure("Pagado", background="#d4edda", foreground="#155724")
        self.tabla.tag_configure("Cancelado", background="#f8d7da", foreground="#721c24")
        
        # Componente de Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetado
        self.tabla.pack(side="left", fill="both", expand=True, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

    def cargar_datos(self):
        """
        Limpia el árbol (Treeview) para insertar los datos más recientes desde BD.
        """
        for registro in self.tabla.get_children():
            self.tabla.delete(registro)
            
        pedidos = obtener_pedidos()
        
        if pedidos:
            for p in pedidos:
                id_pedido = p[0]
                cliente = p[1]
                fecha = p[2]
                total = p[3]
                estado = p[4] 

                # Formatear la fecha
                if hasattr(fecha, 'strftime'):
                    str_fecha = fecha.strftime("%Y-%m-%d %H:%M") 
                else:
                    str_fecha = str(fecha)
                
                # Formatear el total (monetario) con un símbolo y 2 decimales
                try:
                    str_total = f"${float(total):,.2f}" if total is not None else "$0.00"
                except Exception:
                    str_total = str(total)
                
                # El tag será el mismo estado ('Pendiente', 'Pagado', 'Cancelado') para pintar la fila
                self.tabla.insert("", "end", values=(id_pedido, cliente, str_fecha, str_total, estado), tags=(estado,))

    def borrar_seleccionado(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Por favor selecciona un pedido de la tabla primero.")
            return
            
        valores = self.tabla.item(seleccion[0])["values"]
        id_ped, c_nombre = valores[0], valores[1]
        
        if messagebox.askyesno("Confirmar", f"¿Deseas eliminar permanentemente el Pedido #{id_ped} perteneciente a {c_nombre}?\n\n¡Advertencia: esto también borrará todo su registro de artículos comprados!"):
            if eliminar_pedido(id_ped):
                messagebox.showinfo("Éxito", "El pedido fue erradicado correctamente del sistema.")
                self.cargar_datos()

    def actualizar_seleccionado(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Por favor selecciona un pedido de la tabla primero.")
            return
            
        valores = self.tabla.item(seleccion[0])["values"]
        id_ped, estado_actual = valores[0], valores[4]
        
        modal_act = tk.Toplevel(self)
        modal_act.title(f"Administrar Estado (Pedido #{id_ped})")
        modal_act.geometry("300x200")
        modal_act.configure(bg="white")
        modal_act.grab_set() 
        modal_act.resizable(False, False)
        
        modal_act.update_idletasks()
        x = (modal_act.winfo_screenwidth() // 2) - 150
        y = (modal_act.winfo_screenheight() // 2) - 100
        modal_act.geometry(f"+{x}+{y}")
        
        tk.Label(modal_act, text="Cambiar Estado", font=("Segoe UI", 14, "bold"), bg="white").pack(pady=15)
        
        var_estado = tk.StringVar(value=estado_actual)
        cmb_estado = ttk.Combobox(modal_act, textvariable=var_estado, values=["Pendiente", "Pagado", "Cancelado"], state="readonly", font=("Segoe UI", 12))
        cmb_estado.pack(pady=10)
        
        def guardar_cambio():
            nuevo_est = var_estado.get()
            if nuevo_est == estado_actual:
                modal_act.destroy()
                return
                
            if actualizar_pedido(id_ped, nuevo_est):
                messagebox.showinfo("Éxito", f"El pedido ahora está '{nuevo_est}'.", parent=modal_act)
                modal_act.destroy()
                self.cargar_datos()
                
        tk.Button(modal_act, text="Completar Actualización", command=guardar_cambio, font=("Segoe UI", 10, "bold"), bg="#27ae60", fg="white", relief="flat", cursor="hand2", pady=5).pack(fill="x", padx=30, pady=10)

# Wrapper compatible para conectar el módulo con la ventana principal directamente
def mostrar_pedidos(contenedor):
    """
    Punto de entrada oficial que instancia la vista desde main.py
    """
    VistaPedidos(contenedor)