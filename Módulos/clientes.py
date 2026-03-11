import tkinter as tk
from tkinter import ttk

# función que muestra los clientes predeterminados hasta que se inserten nuevos de la BD
def mostrar_clientes(contenedor):
    tk.Label(contenedor, text="Base de Datos de Clientes", font=("Segoe UI", 18, "bold"), bg="white").pack(anchor="w")
    
    style = ttk.Style()
    style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
    
    columnas = ("id", "nombre", "comportamiento", "status")
    tabla = ttk.Treeview(contenedor, columns=columnas, show="headings")
    tabla.heading("id", text="ID"); tabla.heading("nombre", text="Nombre")
    tabla.heading("comportamiento", text="Frecuencia"); tabla.heading("status", text="Estado")
    
    datos = [("001", "Maria Lopez", "Compradora frecuente", "Activo"),
             ("002", "Carlos Ruiz", "Interesado en tecnología", "Lead")]
    
    for fila in datos: tabla.insert("", "end", values=fila)
    tabla.pack(fill="both", expand=True, pady=20)