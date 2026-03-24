# paleta de colores deafualt hasta que se cambie o decidan nuevos
bakcgorund = "#f4f7f6"
sidebar = "#2c3e50"
accent = "#3498db"
text = "#ecf0f1"

# fuentes default hasta que se definan nuevos 
titulo = ("Segoe UI", 18, "bold")
texto_corriente = ("Segoe UI", 11)

import pyodbc
from tkinter import messagebox

# Configuración de base de datos
DB_SERVER = "localhost"
DB_NAME = "shopeasy"

def get_connection():
    try:
        conn_string = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost\\SQLEXPRESS;"
            "DATABASE=shopeasy;"
            "Trusted_Connection=yes;"
        )

        conn = pyodbc.connect(conn_string, timeout=5)
        return conn

    except pyodbc.InterfaceError as e:
        messagebox.showerror("Error de conexión", f"Error de Interfaz:\n{e}")
        return None
    except pyodbc.Error as e:
        messagebox.showerror("Error de base de datos", f"No se pudo conectar:\n{e}")
        return None
    except Exception as e:
        messagebox.showerror("Error inesperado", f"{e}")
        return None
