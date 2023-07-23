import socket
import select
import os
import sys
import fcntl
import threading

class SocketServer:
    def __init__(self, address, port, backlog=5):
        self.address = address
        self.port = port
        self.backlog = backlog
        self.socket_obj = self.create_socket()

    def create_socket(self):
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def set_socket_option(self, option, value):
        self.socket_obj.setsockopt(socket.SOL_SOCKET, option, value)

    def set_non_blocking(self):
        if sys.platform.startswith('win'):
            self.socket_obj.ioctlsocket(socket.FIONBIO, 1)
        else:
            fd = self.socket_obj.fileno()
            flags = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

    def bind_socket(self):
        self.set_socket_option(socket.SO_REUSEADDR, 1)
        self.socket_obj.bind((self.address, self.port))

    def listen_socket(self):
        self.socket_obj.listen(self.backlog)

    def bind_listen(self):
        self.bind_socket()
        self.listen_socket()

    def accept_connection(self):
        client_socket, client_address = self.socket_obj.accept()
        return client_socket, client_address

    def receive_data(self, socket_obj, buffer_size=1024):
        return socket_obj.recv(buffer_size).decode()

    def close(self):
        self.socket_obj.close()

    def handle_client(self, client_socket, client_address):
        try:
            while True:
                data = self.receive_data(client_socket)
                if not data:
                    print(f"Client {client_address[0]}:{client_address[1]} disconnected.")
                    client_socket.close()
                    break
                print(f"Received from {client_address[0]}:{client_address[1]}: {data}")
        except Exception as e:
            print(f"Error handling client {client_address[0]}:{client_address[1]}: {e}")
            client_socket.close()

    def run(self):
        self.bind_listen()
        print(f"Server listening on {self.address}:{self.port}")
        while True:
            ready_sockets, _, _ = select.select([self.socket_obj], [], [], 1)
            if ready_sockets:
                client_socket, client_address = self.accept_connection()
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_thread.start()

def get_server_port():
    if len(sys.argv) > 1:
        try:
            return int(sys.argv[1])
        except ValueError:
            pass
    return 8080  

server_port = get_server_port()
server = SocketServer('127.0.0.1', server_port)
server.run()
