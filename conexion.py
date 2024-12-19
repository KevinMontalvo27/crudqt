import pyodbc
import json

# Configura la conexión a SQL Server
def conectar_sqlserver():
    """
    Establece una conexión a la base de datos SQL Server usando autenticación de Windows.
    """
    try:
        connection = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=DESKTOP-6A5LF6R\SQLEXPRESS;'
            'DATABASE=ventas;'
            'Trusted_Connection=yes;'
        )
        return connection
    except Exception as e:
        print(f"Error al conectar a SQL Server: {e}")
        return None
