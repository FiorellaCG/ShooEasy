import tkinter as tk
from tkinter import ttk
from Config.sets import bakcgorund, sidebar, accent, text
from Módulos.clientes import mostrar_clientes
from Módulos.dashboard import mostrar_dashboard
from Módulos.pedidos import mostrar_pedidos
from Módulos.soporte import mostrar_soporte
from Módulos.marketing import mostrar_marketing
from Módulos.reportes import mostrar_reportes
from Módulos.login import LoginWindow
from Módulos.cliente import mostrar_cliente

class ShopEasyCRM:
    def __init__(self, root):
        self.root = root
        self.root.title("ShopEasy CRM - Ecommerce Solution")
        self.root.geometry("1000x600")
        
        # Paleta de colores default
        self.bg_color = "#f4f7f6"
        self.sidebar_color = "#2c3e50"
        self.accent_color = "#3498db"
        self.text_light = "#ecf0f1"
        
        self.setup_ui()

    def setup_ui(self):
        # main header
        self.main_container = tk.Frame(self.root, bg=self.bg_color)
        self.main_container.pack(fill="both", expand=True)

        # sidebar 
        self.sidebar = tk.Frame(self.main_container, bg=self.sidebar_color, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False) # Mantiene el ancho fijo

        tk.Label(self.sidebar, text="ShopEasy", fg=self.accent_color, bg=self.sidebar_color, 
                 font=("Segoe UI", 18, "bold"), pady=25).pack()

        # botones corregidos con (relief="flat")
        menu_items = [
            ("Dashboard", self.mostrar_dashboard),
            ("Clientes", self.mostrar_clientes),
            ("Pedidos", self.show_orders),
            ("Soporte", self.show_support),
            ("Marketing", self.show_marketing),
            ("Reportes", self.show_reports)
        ]

        for text, command in menu_items:
            btn = tk.Button(self.sidebar, text=text, fg=self.text_light, bg=self.sidebar_color,
                            relief="flat", anchor="w", padx=25, font=("Segoe UI", 11),
                            command=command, cursor="hand2", bd=0, 
                            activebackground=self.accent_color, activeforeground="white")
            btn.pack(fill="x", ipady=12)

        # contenido de las pantallas 
        self.content_area = tk.Frame(self.main_container, bg="white", padx=40, pady=40)
        self.content_area.pack(side="right", fill="both", expand=True)
        
        self.mostrar_dashboard()

    def limpiar_contenido(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def mostrar_dashboard(self):
        self.limpiar_contenido()
        mostrar_dashboard(self.content_area)

    def mostrar_clientes(self):
        self.limpiar_contenido()
        mostrar_clientes(self.content_area)

    # placeholders para el resto
    def show_orders(self): 
        self.limpiar_contenido()
        mostrar_pedidos(self.content_area)
        
    def show_support(self):
        self.limpiar_contenido()
        mostrar_soporte(self.content_area)
        
    def show_marketing(self):
        self.limpiar_contenido()
        mostrar_marketing(self.content_area)
        
    def show_reports(self):
        self.limpiar_contenido()
        mostrar_reportes(self.content_area)

def iniciar_aplicacion():
    root = tk.Tk()
    root.title("Gestión de Clientes - CRM")
    root.geometry("1000x600")
    
    # Manejador de enrutamiento
    def on_login_success(user_data):
        id_rol = user_data[2]
        
        # Admin(1), Soporte(3) -> Entran al CRM Full
        if id_rol in (1, 3):
            app = ShopEasyCRM(root)
        # Cliente(2) -> Vista reducida
        elif id_rol == 2:
            mostrar_cliente(root, user_data[0])
        else:
            # Fallback a Rol de bajo nivel o no identificado con control explícito
            tk.Label(root, text="Rol denegado o no identificado.", font=("Segoe UI", 20)).pack()
            
    # La aplicación en su estado primordial monta el Auth
    LoginWindow(root, on_login_success)
    
    root.mainloop()

if __name__ == "__main__":
    iniciar_aplicacion()