from tkinter import messagebox
from Config.sets import get_connection

def_eliminacion_proveedor_placeholder = None

def eliminar_proveedor(id_proveedor):
    """
    Se conecta a la base de datos para borrar permanentemente un contacto de proveedor
    basado en su ID principal.
    """
    conn = get_connection()
    if not conn: 
        return False
        
    try:
        cursor = conn.cursor()
        
        # Validación extra: si el proveedor está amarrado a otras tablas (Ej. Articulos), 
        # SQL Server abortará automáticamente por FK Constraint a menos que haya CASCADE.
        # Por ahora enviamos el borrado directo.
        cursor.execute("DELETE FROM Proveedor WHERE ID_Proveedor = ?;", (id_proveedor,))
        conn.commit()
        return True
        
    except Exception as e:
        messagebox.showerror("Error de Borrado", f"No se pudo eliminar el proveedor de la base de datos. Es posible que tenga artículos asociados.\n\nDetalle técnico:\n{e}")
        return False
    finally:
        if conn: 
            conn.close()
