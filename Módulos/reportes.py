import tkinter as tk
from tkinter import ttk, messagebox
from Config.sets import get_connection

# ==========================================
# LÓGICA DE ACCESO A DATOS (Data Access Layer)
# ==========================================

def obtener_ventas_totales():
    """
    Calcula la suma total de todos los pedidos ingresados.
    """
    conn = get_connection()
    if not conn: return 0.0
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(Total) AS Total_Ventas FROM Pedido;")
        resultado = cursor.fetchone()
        return float(resultado[0]) if resultado and resultado[0] else 0.0
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar ventas totales:\n{e}")
        return 0.0
    finally:
        if conn: conn.close()

def obtener_productos_mas_vendidos():
    """
    Consulta un ranking de artículos más vendidos mediante INNER JOIN con Detalle_Pedido.
    """
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor()
        query = """
            SELECT 
                a.Nombre,
                SUM(dp.Cantidad) AS Total_Vendido
            FROM Detalle_Pedido dp
            INNER JOIN Articulo a ON dp.ID_Articulo = a.ID_Articulo
            GROUP BY a.Nombre
            ORDER BY Total_Vendido DESC;
        """
        cursor.execute(query)
        return [(f[0], f[1]) for f in cursor.fetchall()]
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar el ranking de productos:\n{e}")
        return []
    finally:
        if conn: conn.close()

def obtener_pedidos_por_estado():
    """
    Agrupa los pedidos contando cuántos existen en cada estado distinto.
    """
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor()
        query = """
            SELECT 
                Estado,
                COUNT(*) AS Cantidad
            FROM Pedido
            GROUP BY Estado;
        """
        cursor.execute(query)
        return [(f[0], f[1]) for f in cursor.fetchall()]
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar el estado de los pedidos:\n{e}")
        return []
    finally:
        if conn: conn.close()

# ==========================================
# INTERFAZ DE USUARIO (Presentation Layer)
# ==========================================

class VistaReportes(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        self.pack(fill="both", expand=True)

        self.crear_widgets()
        self.cargar_datos()

    def crear_widgets(self):
        # Cabecera con título y recarga
        header_frame = tk.Frame(self, bg="white")
        header_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(header_frame, text="Reportes del Sistema", font=("Segoe UI", 18, "bold"), bg="white").pack(side="left")
        tk.Button(header_frame, text="🔄 Recargar Métricas", command=self.cargar_datos, font=("Segoe UI", 10), bg="#ecf0f1", relief="flat", padx=10, cursor="hand2").pack(side="right")

        # -------------------------------------------------------------
        # 🔹 Sección 1: Ventas Totales (Métrica Destacada)
        # -------------------------------------------------------------
        self.frame_ventas = tk.Frame(self, bg="#edf2f7", bd=1, relief="solid", padx=20, pady=20)
        self.frame_ventas.pack(fill="x", pady=10)
        
        tk.Label(self.frame_ventas, text="Ingresos Globales", font=("Segoe UI", 12), bg="#edf2f7", fg="#2c3e50").pack()
        self.lbl_total_ventas = tk.Label(self.frame_ventas, text="₡ 0.00", font=("Segoe UI", 32, "bold"), bg="#edf2f7", fg="#27ae60")
        self.lbl_total_ventas.pack()
        
        # Contenedor Inferior para repartir las tablas a la par
        frame_tablas = tk.Frame(self, bg="white")
        frame_tablas.pack(fill="both", expand=True, pady=20)
        frame_tablas.columnconfigure(0, weight=1, pad=10)
        frame_tablas.columnconfigure(1, weight=1, pad=10)
        
        # -------------------------------------------------------------
        # 🔹 Sección 2: Productos más vendidos (Ranking)
        # -------------------------------------------------------------
        frame_prod = tk.Frame(frame_tablas, bg="white")
        frame_prod.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        tk.Label(frame_prod, text="Ranking de Productos", font=("Segoe UI", 12, "bold"), bg="white").pack(anchor="w", pady=(0,5))
        
        # Treeview Módulo
        style = ttk.Style()
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))
        
        self.tabla_prod = ttk.Treeview(frame_prod, columns=("prod", "cant"), show="headings", height=8)
        self.tabla_prod.heading("prod", text="Producto")
        self.tabla_prod.heading("cant", text="Cantidad Vendida")
        self.tabla_prod.column("prod", width=250, anchor="w")
        self.tabla_prod.column("cant", width=120, anchor="center")
        self.tabla_prod.pack(side="left", fill="both", expand=True)
        
        scroll_prod = ttk.Scrollbar(frame_prod, orient="vertical", command=self.tabla_prod.yview)
        self.tabla_prod.configure(yscrollcommand=scroll_prod.set)
        scroll_prod.pack(side="right", fill="y")
        
        # -------------------------------------------------------------
        # 🔹 Sección 3: Pedidos por estado
        # -------------------------------------------------------------
        frame_est = tk.Frame(frame_tablas, bg="white")
        frame_est.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        tk.Label(frame_est, text="Distribución por Estado", font=("Segoe UI", 12, "bold"), bg="white").pack(anchor="w", pady=(0,5))
        
        self.tabla_est = ttk.Treeview(frame_est, columns=("est", "cant"), show="headings", height=8)
        self.tabla_est.heading("est", text="Estado de Pedido")
        self.tabla_est.heading("cant", text="Cantidad de Tickets")
        self.tabla_est.column("est", width=160, anchor="center")
        self.tabla_est.column("cant", width=120, anchor="center")
        
        # Rótulos en la capa UI solicitados
        self.tabla_est.tag_configure("Pendiente", background="#fff3cd", foreground="#856404")
        self.tabla_est.tag_configure("Pagado", background="#d4edda", foreground="#155724")
        self.tabla_est.tag_configure("Cancelado", background="#f8d7da", foreground="#721c24")
        
        self.tabla_est.pack(side="left", fill="both", expand=True)
        
        scroll_est = ttk.Scrollbar(frame_est, orient="vertical", command=self.tabla_est.yview)
        self.tabla_est.configure(yscrollcommand=scroll_est.set)
        scroll_est.pack(side="right", fill="y")

    def cargar_datos(self):
        """
        Limpia y ejecuta consultas concurrentemente para poblar el Dashboard de Ventas.
        """
        for item in self.tabla_prod.get_children(): self.tabla_prod.delete(item)
        for item in self.tabla_est.get_children(): self.tabla_est.delete(item)
        
        # Análisis: 1. Suma Monetaria
        total_ventas = obtener_ventas_totales()
        self.lbl_total_ventas.config(text=f"₡ {total_ventas:,.2f}")
        
        # Análisis: 2. Ranking de Salida de Elementos
        productos = obtener_productos_mas_vendidos()
        if productos:
            for p in productos:
                self.tabla_prod.insert("", "end", values=p)
                
        # Análisis: 3. Tasa de conversión de Pedidos
        estados = obtener_pedidos_por_estado()
        if estados:
            for e in estados:
                # e = (Estado, Cantidad). El TAG dinámico activa el fondo
                estado_tag = e[0]
                self.tabla_est.insert("", "end", values=e, tags=(estado_tag,))

# Función Directriz conectada al Menú Principal
def mostrar_reportes(contenedor):
    VistaReportes(contenedor)
