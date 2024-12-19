from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox
import sys
import pyodbc
import json
from conexion import conectar_sqlserver

conexion = conectar_sqlserver()

telefono_encontrado = False


def buscar_deuda_por_telefono(numero_telefono: int):
    """
    Busca un número de teléfono en la columna 'telefono' de la tabla 'deudas'.
    Si existe, devuelve el 'username' y 'deuda'.

    Args:
        numero_telefono (int): Número telefónico a buscar.

    Returns:
        tuple: Tupla con 'username' y 'deuda', o None si no se encuentra el número.
    """
    # Convierte el número de teléfono a cadena
    numero_telefono_str = str(numero_telefono)

    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT username, deuda FROM deudas WHERE telefono = ?", numero_telefono_str)
        resultado = cursor.fetchone()  # Obtiene el primer resultado

        if resultado:
            username, deuda = resultado  # Almacena los valores de 'username' y 'deuda'
            return username, deuda  # Retorna una tupla con 'username' y 'deuda'
        else:
            return None  # Si no se encuentra el número, retorna None
    except Exception as e:
        print(f"Error al buscar la deuda: {e}")
        return None

def actualizar_deuda(numero_telefono: int, abono: float):
    """
    Actualiza la deuda de un usuario, restando el abono.
    """
    resultado = buscar_deuda_por_telefono(numero_telefono)

    if resultado:
        username, deuda_actual = resultado
        print(f"Deuda actual para {username}: {deuda_actual}")

        nueva_deuda = max(deuda_actual - abono, 0)
        if nueva_deuda == 0:
            print("La nueva deuda no puede ser negativa, estableciendo deuda a 0.")

        try:
            cursor = conexion.cursor()
            # Actualiza la deuda en la base de datos
            cursor.execute("UPDATE deudas SET deuda = ? WHERE telefono = ?", nueva_deuda, numero_telefono)
            conexion.commit()  # Asegura que los cambios se guarden

            print(f"Deuda actualizada exitosamente. Nueva deuda: {nueva_deuda}")
            return True
        except Exception as e:
            print(f"Error al actualizar la deuda: {e}")
            return False
    else:
        print("No se encontró el número telefónico en la base de datos.")
        return False





class MainWindow(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("interfaz.ui", self)

        # Conectar el botón 'buscarUsuario' al método 'buscar_usuario'
        self.buscarUsuario.clicked.connect(self.buscar_usuario)

        # Conectar el botón 'abonarDeuda' al método 'abonar_deuda'
        self.abonarDeuda.clicked.connect(self.abonar_deuda)

    def buscar_usuario(self):
        try:
            # Obtener el número de teléfono desde un QTextEdit llamado 'identificador'
            numero_telefono = self.identificador.toPlainText().strip()

            # Verificar que el número no esté vacío
            if not numero_telefono:
                self.mostrar_error("El campo de número de teléfono está vacío.")
                return

            # Intentar convertir el número a entero
            try:
                numero_telefono = int(numero_telefono)
            except ValueError:
                self.mostrar_error("El número de teléfono ingresado no es válido.")
                return

            # Llamar a la función buscar_deuda_por_telefono
            resultado = buscar_deuda_por_telefono(numero_telefono)

            if resultado:
                username, deuda = resultado
                # Mostrar el resultado en los QLineEdit correspondientes
                self.nombreCliente.setText(username)
                self.deudaCliente.setText(str(deuda))
            else:
                self.mostrar_error("No se encontró el número o ocurrió un error al consultar.")

        except Exception as e:
            self.mostrar_error(f"Se produjo un error: {str(e)}")

    def abonar_deuda(self):
        try:
            # Obtener el número de teléfono desde el QTextEdit
            numero_telefono = self.identificador.toPlainText().strip()

            # Verificar que el número no esté vacío
            if not numero_telefono:
                self.mostrar_error("El campo de número de teléfono está vacío.")
                return

            # Intentar convertir el número a entero
            try:
                numero_telefono = int(numero_telefono)
            except ValueError:
                self.mostrar_error("El número de teléfono ingresado no es válido.")
                return

            # Obtener el valor del abono desde el QLineEdit llamado 'abono'
            abono_texto = self.abono.text().strip()

            # Verificar que el campo del abono no esté vacío
            if not abono_texto:
                self.mostrar_error("El campo de abono está vacío.")
                return

            try:
                abono = float(abono_texto)
            except ValueError:
                self.mostrar_error("El valor del abono no es válido.")
                return

            # Llamar a la función actualizar_deuda
            if actualizar_deuda(numero_telefono, abono):
                # Una vez que se actualiza la deuda, volvemos a hacer la consulta
                resultado = buscar_deuda_por_telefono(numero_telefono)

                if resultado:
                    username, deuda = resultado
                    # Mostrar los nuevos valores en los QLineEdit correspondientes
                    self.nombreCliente.setText(username)
                    self.deudaCliente.setText(str(deuda))
                    QMessageBox.information(self, "Éxito", "Deuda actualizada exitosamente.")
                else:
                    self.mostrar_error("No se pudo obtener los datos actualizados.")

        except Exception as e:
            self.mostrar_error(f"Se produjo un error: {str(e)}")

    def mostrar_error(self, mensaje):
        # Función para mostrar mensajes de error
        QMessageBox.critical(self, "Error", mensaje)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MainWindow()
    ventana.show()  # QDialog usa show() para mostrarse
    sys.exit(app.exec_())