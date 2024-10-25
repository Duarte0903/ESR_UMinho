import socket
import json
import threading

class BootstrapService:
    def __init__(self, config_file: str, port: int = 2000):
        self.config_file = config_file
        self.port = port

    def start_service(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('', self.port))
        print(f"Bootstrap service listening on port: {self.port}")

        while True:
            try:
                msg, addr = s.recvfrom(1024)
                print("Received neighbours request from:", addr)
                threading.Thread(target=self.process_request, args=(s, addr)).start()
            except Exception as e:
                print(f"Error receiving data: {e}")

    def process_request(self, s: socket.socket, address: tuple):
        try:
            neighbours_response = self.get_neighbours(address[0])
            message = " ".join(neighbours_response[0]) + ";" + str(neighbours_response[1])
            print("Sending neighbours response:", message)
            s.sendto(message.encode('utf-8'), address)
        except Exception as e:
            print(f"Error processing request from {address}: {e}")

    def get_neighbours(self, ip: str):
        try:
            with open(self.config_file) as f:
                config = json.load(f)
                response = config['nodes'].get(ip, []) # Se o IP não existir, devolve uma lista vazia
                ttl = config.get("TTL", 6)  # TTL fica a 6 se não for especificado
                print("Neighbours for IP", ip, ":", response)
                return (response, ttl)
        except FileNotFoundError:
            print(f"Config file {self.config_file} not found.")
            return ([], 6)
        except json.JSONDecodeError:
            print("Error decoding JSON in the configuration file.")
            return ([], 6)
