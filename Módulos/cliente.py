import tkinter as tk
from tkinter import ttk, messagebox
from Config.sets import get_connection

# ==========================================
# LÓGICA DE ACCESO A DATOS (Data Access Layer)
# ==========================================

# Carrito global simple en memoria
carrito_compras = []

def obtener_productos():
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor()
        query = """
            SELECT 
                a.ID_Articulo,
                a.Nombre,
                a.Precio,
                a.Stock,
                c.Nombre AS Categoria
            FROM Articulo a
            INNER JOIN Categoria_Articulo c ON a.ID_Categoria = c.ID_Categoria;
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Excepción al traer los productos: {e}")
        return []
    finally:
        if conn: conn.close()

def crear_pedido(id_usuario, total, modal, cb_exito):
    """
    Inserta el carrito actual en Base de Datos de manera relacional.
    """
    if not carrito_compras:
        return
        
    conn = get_connection()
    if not conn: return
    try:
        cursor = conn.cursor()
        
        # 1 y 2. Crear Pedido principal y recuperar ID en la misma ráfaga
        # PyODBC pierde el SCOPE_IDENTITY() si se llama en un execute() separado.
        cursor.execute("""
            SET NOCOUNT ON;
            INSERT INTO Pedido (ID_Usuario, Estado, Total)
            VALUES (?, 'Pendiente', ?);
            SELECT SCOPE_IDENTITY();
        """, (id_usuario, total))
        
        row_id = cursor.fetchone()
        id_pedido = row_id[0] if row_id else None
            
        if not id_pedido:
            raise Exception("No se pudo obtener el ID del pedido")
        
        # 3. Iterar e insertar los deTalles de este pedido
        for item in carrito_compras:
            sub = item["precio"] * item["cantidad"]
            cursor.execute("""
                INSERT INTO Detalle_Pedido 
                (ID_Pedido, ID_Articulo, Cantidad, Precio_Unitario, Subtotal)
                VALUES (?, ?, ?, ?, ?)
            """, (id_pedido, item["id"], item["cantidad"], item["precio"], sub))
            
        # Comiteo manual atómico
        conn.commit()
        carrito_compras.clear()
        
        messagebox.showinfo("Compra", "Pedido realizado con éxito", parent=modal)
        modal.destroy()
        
        if cb_exito:
            cb_exito()
            
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Error", str(e), parent=modal)
    finally:
        if conn: conn.close()

def agregar_al_carrito(producto):
    """
    Control combinatorio del objeto actualizando cantidades o apendando al historial volátil.
    # producto = (id, nombre, precio, stock, categoria)
    """
    id_prod = producto[0]
    precio_num = float(producto[2]) if producto[2] is not None else 0.0
    
    for item in carrito_compras:
        if item["id"] == id_prod:
            item["cantidad"] += 1
            messagebox.showinfo("Carrito", f"Producto actualizado en el carrito. \nAhora llevas {item['cantidad']} de {producto[1]}.", parent=None)
            return
            
    carrito_compras.append({
        "id": id_prod,
        "nombre": producto[1],
        "precio": precio_num,
        "cantidad": 1
    })
    
    messagebox.showinfo("Carrito", f"Producto agregado al carrito exitosamente.", parent=None)

# ==========================================
# INTERFAZ DE USUARIO (Presentation Layer)
# ==========================================

class VistaCatalogo(tk.Frame):
    def __init__(self, root, id_usuario):
        super().__init__(root, bg="white")
        self.pack(fill="both", expand=True)
        self.id_usuario = id_usuario
        
        self.crear_widgets()
        self.cargar_datos()

    def crear_widgets(self):
        header_frame = tk.Frame(self, bg="white")
        header_frame.pack(fill="x", pady=20, padx=20)
        
        tk.Label(header_frame, text="Catálogo de Productos ShopEasy", font=("Segoe UI", 24, "bold"), bg="white", fg="#2c3e50").pack(side="left")
        
        btn_frame = tk.Frame(header_frame, bg="white")
        btn_frame.pack(side="right", pady=5)
        
        tk.Button(btn_frame, text="🛒 Ver Carrito", command=self.mostrar_carrito, font=("Segoe UI", 10, "bold"), bg="#f39c12", fg="white", relief="flat", padx=10, cursor="hand2").pack(side="left", padx=10)
        tk.Button(btn_frame, text="🔄 Refrescar", command=self.cargar_datos, font=("Segoe UI", 10), bg="#ecf0f1", relief="flat", padx=10, cursor="hand2").pack(side="left")
        
        contenedor_scroll = tk.Frame(self, bg="white")
        contenedor_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.canvas = tk.Canvas(contenedor_scroll, bg="white", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(contenedor_scroll, orient="vertical", command=self.canvas.yview)
        
        self.frame_productos = tk.Frame(self.canvas, bg="white")
        self.frame_productos.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas.create_window((0, 0), window=self.frame_productos, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
    def cargar_datos(self):
        for widget in self.frame_productos.winfo_children():
            widget.destroy()
            
        productos = obtener_productos()
        if not productos:
            tk.Label(self.frame_productos, text="Catálogo en mantenimiento.", font=("Segoe UI", 12), bg="white").pack(pady=40)
            return

        col_actual = 0
        fila_actual = 0
        
        for p in productos:
            stock_real = p[3] if p[3] is not None else 0
            precio_real = p[2] if p[2] is not None else 0.0
            str_precio = f"₡ {float(precio_real):,.2f}"
            
            if stock_real > 20: 
                color_stock, txt_stock = "#27ae60", f"Stock: {stock_real} (Disponible)"
            elif 5 <= stock_real <= 20: 
                color_stock, txt_stock = "#e67e22", f"Stock: {stock_real} (Últimas unidades)"
            elif 0 < stock_real < 5: 
                color_stock, txt_stock = "#e74c3c", f"Stock: {stock_real} (¡Volando!)"
            else:
                color_stock, txt_stock = "#7f8c8d", "Agotado Temporalmente"
                
            card = tk.Frame(self.frame_productos, bg="#f8f9fa", bd=2, relief="groove")
            card.grid(row=fila_actual, column=col_actual, padx=15, pady=15, sticky="nsew")
            
            tk.Label(card, text=p[1], font=("Segoe UI", 14, "bold"), bg="#f8f9fa", fg="#2c3e50", wraplength=180, justify="center").pack(pady=(15, 5))
            tk.Label(card, text=p[4], font=("Segoe UI", 10, "italic"), bg="#f8f9fa", fg="#7f8c8d").pack(pady=(0, 10))
            tk.Label(card, text=str_precio, font=("Segoe UI", 16, "bold"), bg="#f8f9fa", fg="#27ae60").pack()
            tk.Label(card, text=txt_stock, font=("Segoe UI", 10, "bold"), bg="#f8f9fa", fg=color_stock).pack(pady=(10, 15))
            
            btn = tk.Button(card, text="➕ Agregar al Carrito", command=lambda prod=p: agregar_al_carrito(prod), font=("Segoe UI", 10, "bold"), bg="#3498db", fg="white", relief="flat", cursor="hand2", pady=5)
            
            if stock_real <= 0:
                btn.config(state="disabled", bg="#bdc3c7", text="Sin inventario")
                
            btn.pack(fill="x")
            
            col_actual += 1
            if col_actual > 2:
                col_actual = 0
                fila_actual += 1

    def mostrar_carrito(self):
        """
        Calcula totales de items, dibuja una tabla y genera el botón de finalización
        """
        if not carrito_compras:
            messagebox.showinfo("Carrito", "Tu carrito de compras está vacío actualmente.", parent=self)
            return
            
        modal = tk.Toplevel(self)
        modal.title("Orden de Compra")
        modal.geometry("600x480")
        modal.configure(bg="white")
        modal.grab_set()
        
        modal.update_idletasks()
        x = (modal.winfo_screenwidth() // 2) - (600 // 2)
        y = (modal.winfo_screenheight() // 2) - (480 // 2)
        modal.geometry(f"+{x}+{y}")
        
        tk.Label(modal, text="Resumen de Compra", font=("Segoe UI", 18, "bold"), bg="white", fg="#2c3e50").pack(pady=(15, 5))
        
        frame_tabla = tk.Frame(modal, bg="white", padx=20)
        frame_tabla.pack(fill="both", expand=True, pady=10)
        
        columnas = ("prod", "precio", "cant", "sub")
        tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=8)
        
        tabla.heading("prod", text="Producto")
        tabla.heading("precio", text="Precio U.")
        tabla.heading("cant", text="Cant.")
        tabla.heading("sub", text="Subtotal")
        
        tabla.column("prod", width=250, anchor="w")
        tabla.column("precio", width=100, anchor="e")
        tabla.column("cant", width=50, anchor="center")
        tabla.column("sub", width=120, anchor="e")
        
        total_total = 0.0
        
        for item in carrito_compras:
            sub_parcial = item["precio"] * item["cantidad"]
            total_total += sub_parcial
            
            str_p = f"₡ {item['precio']:,.2f}"
            str_s = f"₡ {sub_parcial:,.2f}"
            
            tabla.insert("", "end", values=(item["nombre"], str_p, item["cantidad"], str_s))
            
        tabla.pack(side="left", fill="both", expand=True)
        
        scroll = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        
        # Area Footer de Liquidación
        footer = tk.Frame(modal, bg="#f8f9fa", bd=1, relief="ridge", pady=15, padx=20)
        footer.pack(fill="x", side="bottom")
        
        tk.Label(footer, text="Total a Pagar:", font=("Segoe UI", 12), bg="#f8f9fa", fg="#7f8c8d").pack(side="left")
        tk.Label(footer, text=f"₡ {total_total:,.2f}", font=("Segoe UI", 20, "bold"), bg="#f8f9fa", fg="#27ae60").pack(side="left", padx=10)
        
        tk.Button(footer, text="✅ Finalizar Compra", command=lambda: crear_pedido(self.id_usuario, total_total, modal, self.cargar_datos), font=("Segoe UI", 12, "bold"), bg="#e67e22", fg="white", relief="flat", cursor="hand2", padx=20).pack(side="right")
        

# Wrapper de Invocación
def mostrar_cliente(contenedor, id_usuario):
    VistaCatalogo(contenedor, id_usuario)
