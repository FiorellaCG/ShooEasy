from tkinter import messagebox
from Config.sets import get_connection

def eliminar_ticket(id_ticket):
    """
    Borra permanentemente el registro del Ticket basado en su ID principal.
    """
    conn = get_connection()
    if not conn: 
        return False
        
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Ticket WHERE ID_Ticket = ?;", (id_ticket,))
        conn.commit()
        return True
        
    except Exception as e:
        messagebox.showerror("Error de Borrado", f"No se pudo eliminar el ticket de la base de datos.\n\nDetalle técnico:\n{e}")
        return False
    finally:
        if conn: 
            conn.close()


def actualizar_ticket(id_ticket, nuevo_estado):
    """
    Actualiza la columna Estado de un ticket existente.
    """
    conn = get_connection()
    if not conn: 
        return False
        
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE Ticket SET Estado = ? WHERE ID_Ticket = ?;", (nuevo_estado, id_ticket))
        conn.commit()
        return True
        
    except Exception as e:
        messagebox.showerror("Error de Actualización", f"No se pudo actualizar el estado del ticket.\n\nDetalle técnico:\n{e}")
        return False
    finally:
        if conn: 
            conn.close()
