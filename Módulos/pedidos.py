import tkinter as tk
from tkinter import ttk

def mostrar_pedidos(contenedor):
    tk.Label(contenedor, text="Gestión de Pedidos", font=("Segoe UI", 18, "bold"), bg="white").pack(anchor="w")
    
    # tabla para evitar envíos duplicados o faltantes según requeirmietos
    style = ttk.Style()
    style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
    
    columnas = ("id", "cliente", "producto", "estado")
    tree = ttk.Treeview(contenedor, columns=columnas, show="headings")
    tree.heading("id", text="Orden #"); tree.heading("cliente", text="Cliente")
    tree.heading("producto", text="Producto"); tree.heading("estado", text="Estado")
    
    # datos de ejemplo
    datos = [("101", "Maria Lopez", "Laptop Pro", "Enviado"),
             ("102", "Carlos Ruiz", "Mouse Gamer", "Pendiente")]
    
    for item in datos: tree.insert("", "end", values=item)
    tree.pack(fill="both", expand=True, pady=20)