import socket
import threading
import sys

class Server:
    self.host = 0
    self.port = 0

    def __init__ (self, host, port):
        self.host = host
        self.port = port

    def handle_client(conn, addr):
        print(f'Connected by {addr}')
        with conn:
            while True:
                data = conn.recv(1024)
                
                if not data:
                    print(f'Connection closed by {addr}')
                    break

                print(f'Received from {addr}: {data.decode()}')
                response = f"Echo: {data.decode()}"
                conn.sendall(response.encode())

    def start_server(): 
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print(f'Server listening on {self.host}:{self.port}')

        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()

def main():
    server = Server(10.0.16.10, 42069)
    server.start_server()

if __name__ == '__main__':
    main()