import socket
import threading
import sys

class OClient:
    def __init__ (self, host, local_ip, port):
        self.host = host
        self.local_ip = local_ip
        self.port = port

    def start_client(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))
                print(f'Connected to {self.host}:{self.port}')

                while True:
                    message = input("Enter a message: ")

                    if message.lower() == 'exit':
                        print("Closing the connection...")
                        s.close()
                        break
                    
                    s.sendall(message.encode('utf-8'))
                    data = s.recv(1024)
                    print(f"Received: {data.decode('utf-8')}")
        except socket.error as e:
            print(f"Socket error: {e}")
        finally:
            if s:
                s.close()
                print("Socket closed.")

def main():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    client = OClient(hostname, local_ip, 42069)
    client.start_client()

if __name__ == '__main__':
    main()
