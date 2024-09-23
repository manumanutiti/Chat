#!/usr/bin/env python3

import socket
import threading

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = []
        self.lock = threading.Lock()  # To handle concurrent access to clients

    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            print(f"[+] Server started on {self.host}:{self.port}")
            s.listen(5)

            while True:
                client_socket, addr = s.accept()
                print(f"[+] Connection from {addr}")
                threading.Thread(target=self.handle_client, args=(client_socket, addr)).start()

    def handle_client(self, client_socket, addr):
        client_socket.send("Enter your username: ".encode())
        username = client_socket.recv(1024).decode().strip()
        
        with self.lock:
            self.clients.append((client_socket, username, addr[0]))
        
        print(f"[+] User {username} connected from {addr[0]}")
        
        self.update_users()

        while True:
            try:
                message = client_socket.recv(1024).decode()
                if message:
                    formatted_message = f"{username}: {message}"
                    self.broadcast(formatted_message, client_socket)
                else:
                    break
            except Exception as e:
                print(f"[-] Error: {e}")
                break
        
        with self.lock:
            self.clients.remove((client_socket, username, addr[0]))
        self.broadcast(f"{username} se ha desconectado del chat.", client_socket)
        self.update_users()
        client_socket.close()
        print(f"[-] User {username} disconnected.")

    def broadcast(self, message, sender_socket):
        with self.lock:  # Lock while broadcasting
            for client_socket, _, _ in self.clients:
                if client_socket != sender_socket:
                    client_socket.send(message.encode())
        self.update_users()

    def update_users(self):
        user_list = ",".join(f"{username} ({ip})" for _, username, ip in self.clients)
        with self.lock:  # Lock while updating users
            for client_socket, _, _ in self.clients:
                client_socket.send(f"USERS:{user_list}".encode())

if __name__ == "__main__":
    server = Server("192.168.0.16", 65000)
    server.start_server()
