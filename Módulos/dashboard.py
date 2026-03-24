import tkinter as tk
from tkinter import ttk, messagebox
from Config.sets import get_connection

# ==========================================
# LÓGICA DE ACCESO A DATOS (Data Access Layer)
# ==========================================

def obtener_metricas_rapidas():
    """
    Obtiene 4 KPIs principales ejecutando conteos y sumas rápidas.
    Retorna: (total_clientes, total_pedidos, ingresos_totales, tickets_abiertos)
    """
    conn = get_connection()
    if not conn: return (0, 0, 0.0, 0)
    
    try:
        cursor = conn.cursor()
        
        # 1. Total Clientes (Asumimos ID_Tipo_Usuario = 2 es Cliente)
        cursor.execute("SELECT COUNT(*) FROM Usuario WHERE ID_Tipo_Usuario = 2;")
        t_clientes = cursor.fetchone()[0] or 0
        
        # 2. Total Pedidos
        cursor.execute("SELECT COUNT(*) FROM Pedido;")
        t_pedidos = cursor.fetchone()[0] or 0
        
        # 3. Ingresos Totales
        cursor.execute("SELECT SUM(Total) FROM Pedido;")
        ingresos = cursor.fetchone()[0] or 0.0
        
        # 4. Tickets Abiertos
        cursor.execute("SELECT COUNT(*) FROM Ticket WHERE Estado = 'Abierto';")
        t_tickets = cursor.fetchone()[0] or 0
        
        return (t_clientes, t_pedidos, float(ingresos), t_tickets)
    except Exception as e:
        print(f"Error interno al cargar métricas: {e}")
        return (0, 0, 0.0, 0)
    finally:
        if conn: conn.close()

def obtener_pedidos_recientes():
    """
    Obtiene los 5 pedidos más recientes para la vista rápida.
    """
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor()
        query = """
            SELECT TOP 5
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
        return cursor.fetchall()
    except Exception as e:
        print(f"Error interno al cargar pedidos recientes: {e}")
        return []
    finally:
        if conn: conn.close()

# ==========================================
# INTERFAZ DE USUARIO (Presentation Layer)
# ==========================================

class VistaDashboard(tk.Frame):
    """
    Vista principal que se muestra al iniciar el sistema.
    """
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_datos()

    def crear_widgets(self):
        # ---------------------------------------------------------
        # Header Principal
        # ---------------------------------------------------------
        header_frame = tk.Frame(self, bg="white")
        header_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(header_frame, text="Dashboard Principal", font=("Segoe UI", 22, "bold"), bg="white", fg="#2c3e50").pack(side="left")
        tk.Button(header_frame, text="🔄 Actualizar Todo", command=self.cargar_datos, font=("Segoe UI", 10), bg="#ecf0f1", relief="flat", padx=15, cursor="hand2").pack(side="right")

        # ---------------------------------------------------------
        # Sección 1: Tarjetas de Métricas (KPI Cards)
        # ---------------------------------------------------------
        self.cards_frame = tk.Frame(self, bg="white")
        self.cards_frame.pack(fill="x", pady=10)
        
        self.cards_frame.columnconfigure(0, weight=1)
        self.cards_frame.columnconfigure(1, weight=1)
        self.cards_frame.columnconfigure(2, weight=1)
        self.cards_frame.columnconfigure(3, weight=1)

        # Crear 4 tarjetas elegantes
        self.lbl_clientes = self.crear_tarjeta(self.cards_frame, 0, "Clientes Activos", "0", "#3498db")   # Azul
        self.lbl_pedidos = self.crear_tarjeta(self.cards_frame, 1, "Pedidos Totales", "0", "#9b59b6")     # Morado
        self.lbl_ingresos = self.crear_tarjeta(self.cards_frame, 2, "Ingresos Brutos", "₡ 0.00", "#27ae60") # Verde
        self.lbl_tickets = self.crear_tarjeta(self.cards_frame, 3, "Tickets Pendientes", "0", "#e74c3c")   # Rojo

        # ---------------------------------------------------------
        # Sección 2: Últimos Pedidos (Mini-Tabla)
        # ---------------------------------------------------------
        tk.Label(self, text="Últimos 5 Pedidos Registrados", font=("Segoe UI", 14, "bold"), bg="white", fg="#34495e").pack(anchor="w", pady=(25, 10))

        style = ttk.Style()
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))
        
        columnas = ("id", "cliente", "fecha", "total", "estado")
        self.tabla = ttk.Treeview(self, columns=columnas, show="headings", height=6)
        
        self.tabla.heading("id", text="ID")
        self.tabla.heading("cliente", text="Cliente")
        self.tabla.heading("fecha", text="Fecha")
        self.tabla.heading("total", text="Total")
        self.tabla.heading("estado", text="Estado")

        self.tabla.column("id", width=60, anchor="center")
        self.tabla.column("cliente", width=250, anchor="w")
        self.tabla.column("fecha", width=160, anchor="center")
        self.tabla.column("total", width=120, anchor="e")
        self.tabla.column("estado", width=130, anchor="center")
        
        # Colores consistentes en el sistema
        self.tabla.tag_configure("Pendiente", background="#fff3cd", foreground="#856404")
        self.tabla.tag_configure("Pagado", background="#d4edda", foreground="#155724")
        self.tabla.tag_configure("Cancelado", background="#f8d7da", foreground="#721c24")
        
        self.tabla.pack(fill="both", expand=True)

    def crear_tarjeta(self, parent, col, titulo, valor_inicial, color_borde):
        """
        Genera un Frame estilo tarjeta con un borde de color en la parte superior.
        """
        card = tk.Frame(parent, bg="#f8f9fa", bd=1, relief="groove")
        # Línea de color de acento
        color_line = tk.Frame(card, bg=color_borde, height=4)
        color_line.pack(fill="x", side="top")
        
        card.grid(row=0, column=col, sticky="nsew", padx=10)
        
        tk.Label(card, text=titulo, font=("Segoe UI", 11), bg="#f8f9fa", fg="#7f8c8d").pack(pady=(15, 0))
        lbl_valor = tk.Label(card, text=valor_inicial, font=("Segoe UI", 24, "bold"), bg="#f8f9fa", fg="#2c3e50", pady=10)
        lbl_valor.pack()
        
        return lbl_valor

    def cargar_datos(self):
        """
        Refresca todas las métricas KPIs y los pedidos de la tabla concurrente.
        """
        # 1. Actualizar KPI Cards
        clientes, pedidos, ingresos, tickets = obtener_metricas_rapidas()
        self.lbl_clientes.config(text=str(clientes))
        self.lbl_pedidos.config(text=str(pedidos))
        self.lbl_ingresos.config(text=f"₡ {ingresos:,.2f}")
        self.lbl_tickets.config(text=str(tickets))
        
        # 2. Actualizar Tabla
        for item in self.tabla.get_children(): self.tabla.delete(item)
        recientes = obtener_pedidos_recientes()
        
        if recientes:
            for p in recientes:
                # p = (id, cliente, fecha, total, estado)
                fecha = p[2]
                str_fecha = fecha.strftime("%Y-%m-%d %H:%M") if hasattr(fecha, 'strftime') else str(fecha)
                
                try:
                    str_total = f"₡ {float(p[3]):,.2f}" if p[3] is not None else "₡ 0.00"
                except Exception:
                    str_total = str(p[3])
                    
                estado = p[4]
                self.tabla.insert("", "end", values=(p[0], p[1], str_fecha, str_total, estado), tags=(estado,))

# Wrapper de Inicialización
def mostrar_dashboard(contenedor):
    VistaDashboard(contenedor)
