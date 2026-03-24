from tkinter import messagebox
from Config.sets import get_connection

def eliminar_pedido(id_pedido):
    """
    Borra permanentemente el registro del Pedido basado en su ID principal.
    Elimina preventivamente la tabla de detalles (Detalle_Pedido) en una transacción atómica 
    para no violar la llave foránea (Foreign Key constraint).
    """
    conn = get_connection()
    if not conn: 
        return False
        
    try:
        cursor = conn.cursor()
        
        # 1. Borrado dependiente
        cursor.execute("DELETE FROM Detalle_Pedido WHERE ID_Pedido = ?;", (id_pedido,))
        
        # 2. Borrado maestro
        cursor.execute("DELETE FROM Pedido WHERE ID_Pedido = ?;", (id_pedido,))
        
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback() # Abortar por si se borraron los detalles pero no el header
        messagebox.showerror("Error de Borrado", f"No se pudo eliminar el ticket de la base de datos.\n\nDetalle técnico:\n{e}")
        return False
    finally:
        if conn: 
            conn.close()


def actualizar_pedido(id_pedido, nuevo_estado):
    """
    Actualiza la columna Estado de un Pedido existente a (Pagado, Pendiente, Cancelado).
    """
    conn = get_connection()
    if not conn: 
        return False
        
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE Pedido SET Estado = ? WHERE ID_Pedido = ?;", (nuevo_estado, id_pedido))
        conn.commit()
        return True
        
    except Exception as e:
        messagebox.showerror("Error de Actualización", f"No se pudo actualizar el estado del pedido.\n\nDetalle técnico:\n{e}")
        return False
    finally:
        if conn: 
            conn.close()
