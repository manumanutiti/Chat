import socket
import threading
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QPushButton
from PyQt6.QtCore import pyqtSignal, QObject, Qt
from PyQt6.QtGui import QIcon

class Communicator(QObject):
    update_users_signal = pyqtSignal(str)

class Chat(QMainWindow):
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected_users = set()  # Para mantener un conjunto de usuarios conectados
        self.communicator = Communicator()

        # Conectar la señal para actualizar usuarios
        self.communicator.update_users_signal.connect(self.update_user_list)

        # Configuración de la ventana
        self.setMinimumSize(900, 600)
        self.setWindowTitle("ASIR CLASS CHAT")

        # Área de chat
        self.chat_area = QTextEdit(self)
        self.chat_area.setGeometry(10, 10, 600, 500)
        self.chat_area.setStyleSheet("background-color: #f0f8ff; border-radius: 10px; border: 1px solid #0a0a0a; font-size:16px; font-weight: bold;")
        self.chat_area.setReadOnly(True)

        # Campo de entrada
        self.input_field = QLineEdit(self)
        self.input_field.setGeometry(10, 520, 600, 40)
        self.input_field.setStyleSheet("background-color: #ffffff; border-radius: 10px; border: 1px solid #0a0a0a; font-size: 16px")
        
        # Botón de envío
        self.button = QPushButton("SEND", self)
        self.button.setGeometry(620, 520, 250, 40)
        self.button.setStyleSheet("""background-color: #008000; color: white; border-radius: 10px; font-size: 16px; border: 1px solid #132c0d; font-weight: bold;""")
        self.button.clicked.connect(self.send_message)

        # Botón Borrar chat
        self.clear_chat = QPushButton(self)
        self.clear_chat.setIcon(QIcon("basura.png"))
        self.clear_chat.setGeometry(560, 460, 50, 50)
        self.clear_chat.setStyleSheet('''border-radius: 3px;''')
        self.clear_chat.clicked.connect(self.clear_chat_func)

        # Label para usuarios conectados
        self.label = QTextEdit(self)
        self.label.setReadOnly(True)
        self.label.setText("  USUARIOS CONECTADOS")
        self.label.setGeometry(620, 11, 250, 40)
        self.label.setStyleSheet('''background-color: #57a639; border-radius: 5px; font-size: 18px ; text-align:center; color: #ffffff; font-weight: bold;''')


        # Área de texto para mostrar usuarios conectados
        self.user_area = QTextEdit(self)
        self.user_area.setGeometry(620, 55, 250, 453)
        self.user_area.setStyleSheet('''background-color: #dbead5; border: 1px solid #4CAF50; font-size: 18px; border-radius: 5px; font-weight: bold; color: #109510''')
        self.user_area.setReadOnly(True)  # Hacer que el área sea de solo lectura

        self.show()

        # Conectar al servidor
        self.connect_to_server()

        # Iniciar hilo para recibir mensajes
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.daemon = True
        self.receive_thread.start()

    def connect_to_server(self):
        try:
            self.client_socket.connect((self.host, self.port))
            print("Conectado al servidor.")
        except Exception as e:
            print(f"Error al conectar: {e}")

    def send_message(self):
        message = self.input_field.text()
        if message:
            self.client_socket.send(message.encode())
            self.chat_area.append(f"Tú: {message}")
            self.input_field.clear()

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                if message.startswith("USERS:"):
                    self.communicator.update_users_signal.emit(message[6:])  # Emitir señal para actualizar la lista de usuarios
                elif message:  # Solo agregar mensajes no vacíos
                    self.chat_area.append(message)
            except Exception as e:
                print(f"Error al recibir mensaje: {e}")
                break

    def update_user_list(self, users):
        new_users = set(user.strip() for user in users.split(",") if user.strip())  # Filtrar entradas vacías

        # Eliminar cualquier usuario que contenga "USERS:"
        new_users = {user for user in new_users if "USERS:" not in user}

        # Limpiar el área de texto antes de actualizar
        self.user_area.clear()
        self.user_area.append("\n".join(sorted(new_users)))  # Mostrar usuarios en el área de texto

        self.connected_users = new_users  # Actualizar el conjunto de usuarios conectados


    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.send_message()  # Enviar el mensaje al presionar Enter


    def clear_chat_func(self):
        self.chat_area.clear() 


if __name__ == "__main__":
    app = QApplication(sys.argv)
    chat_client = Chat("192.168.0.12", 65000)  # Cambia la ip y el puerto según sea necesario
    sys.exit(app.exec())
