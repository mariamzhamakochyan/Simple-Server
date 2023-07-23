import socket
import select
import os
import sys
import fcntl

class SocketClient:
    def __init__(self):
        self.socket_obj = self.create_socket()

    def create_socket(self):
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def set_non_blocking(self):
        if sys.platform.startswith('win'):
            self.socket_obj.ioctlsocket(socket.FIONBIO, 1)
        else:
            fd = self.socket_obj.fileno()
            flags = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

    def bind_socket(self, local_address, local_port):
        self.socket_obj.bind((local_address, local_port))

    def connect(self, remote_address, remote_port):
        try:
            self.socket_obj.connect((remote_address, remote_port))
        except BlockingIOError:
            ready_sockets = select.select([], [self.socket_obj], [], 5)
            if not ready_sockets[1]:
                raise TimeoutError("Connection timeout")
            err = self.socket_obj.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            if err != 0:
                raise ConnectionError(f"Failed to connect: {os.strerror(err)}")

    def send_data(self, data):
        self.socket_obj.send(data.encode())

    def receive_data(self, buffer_size=1024):
        return self.socket_obj.recv(buffer_size).decode()

    def close(self):
        self.socket_obj.close()

    def run(self):
        server_ip = input("Enter server IP address: ")
        server_port = int(input("Enter server port number: "))

        try:
            self.connect(server_ip, server_port)
            print("Connected to the server.")
        except Exception as e:
            print(f"Error connecting to the server: {e}")
            return

        try:
            while True:
                ready_sockets, _, _ = select.select([sys.stdin, self.socket_obj], [], [])

                for sock in ready_sockets:
                    if sock == self.socket_obj:
                        data = self.receive_data()
                        if not data:
                            print("Disconnected from the server.")
                            return
                        print(f"Received from server: {data}")
                    else:
                        message = input()
                        self.send_data(message)
                        if message.lower() == "exit":
                            print("Disconnected from the server.")
                            return
        except KeyboardInterrupt:
            print("Disconnected from the server.")

if __name__ == "__main__":
    client = SocketClient()
    client.run()
