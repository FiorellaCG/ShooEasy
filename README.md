# ShopEasy CRM - Ecommerce Solution 🛒

**ShopEasy CRM** es un proyecto integral de facturación e inventario desarrollado en Python utilizando la biblioteca `tkinter` para ofrecer una interfaz nativa, gráfica y moderna. El objetivo del sistema es unificar por roles las tareas críticas de una tienda tipo Ecommerce y su CRM administrativo.

## 🌟 Características Principales
- **Sistema de Autenticación Multipanel:** Redirecciones controladas en base al rol de usuario registrado (Administrador, Cliente o Soporte).
- **Catálogo de Clientes Interactivo:** Visualización dinámica de los artículos de la tienda con soporte para añadir productos al carrito, validar inventario en tiempo real (stock) y proceder al *Checkout* relacional con pedidos en Base de Datos.
- **Dashboard Estadístico de Admin:** KPIs (Indicadores Clave de Rendimiento) limpios, interactivos y con posibilidad de ser visualizados de forma rápida.
- **Navegación Intuitiva:** Soporte robusto inter-modulos con botones directos hacia el cierre de sesión (`Salir al Login`) o para volver al nivel base del programa (`Volver`).
- **Persistencia Estable:** Sincronizado dinámicamente utilizando `pyodbc` con conectores directos a **Microsoft SQL Server**.

## 🚀 Requisitos de Instalación
Es importante tener lo siguiente disponible en tu sistema:
- **Python 3.8 o superior**.
- **Microsoft SQL Server** local activo (configurado en la ruta `Config/sets.py` y con la creación previa de bases de datos/tablas).

### Librerías Externas a Instalar
Debes instalar dos dependencias simples asegurándote de estar utilizando `pip`:
```bash
py -m pip install pyodbc tkcalendar
```
*(Es sumamente indispensable contar con estas dos librerías externas debido a que manejan el conector del Servidor y el recolector de fechas visual `tkcalendar`).*

## 📖 Instrucciones de Uso y Configuración Local
1. Clona el repositorio a una carpeta:
   ```bash
   git clone https://github.com/FiorellaCG/ShooEasy.git
   ```
2. Desplázate hasta la carpeta principal del proyecto:
   ```bash
   cd ShopEasy
   ```
3. Inicia la aplicación usando el script de inicialización (`main.py`):
   ```bash
   py main.py
   ```
4. Ingresa a la ventana inicial.

---
**Nota para Contribuyentes/Desarrollo:** Cada panel está segmentado dentro de la carpeta `Módulos/`, lo que permite poder editar las pantallas (como `clientes.py`, `dashboard.py` o `cliente.py`) limitando el ámbito del contenido y promoviendo arquitectura limpia.
