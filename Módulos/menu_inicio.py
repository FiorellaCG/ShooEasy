import tkinter as tk
from Config.sets import accent

#Esta función basicmaente despliega las metricas en buena teoría donde se ven los datos de los clientes :D
def mostrar_dashboard(contenedor):
    tk.Label(contenedor, text="Panel de Control", font=("Segoe UI", 22, "bold"), 
             bg="white", fg="#333").pack(anchor="w")
    
    cards_frame = tk.Frame(contenedor, bg="white")
    cards_frame.pack(fill="x", pady=30)

    metrics = [("Ventas Hoy", "$1,250", "#27ae60"), 
               ("Tickets", "4", "#e74c3c"), 
               ("Nuevos Leads", "+15", "#f39c12")]
    
    # Alineamiento de metricas y demás
    
    for title, val, col in metrics:
        f = tk.Frame(cards_frame, bg=col, padx=20, pady=20, width=200)
        f.pack(side="left", padx=10)
        f.pack_propagate(False)
        tk.Label(f, text=val, fg="white", bg=col, font=("Arial", 18, "bold")).pack()
        tk.Label(f, text=title, fg="white", bg=col).pack()