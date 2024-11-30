import socket
import threading
import time
import json
import sys
import os

from utils.VideoStream import VideoStream
from utils.RtpPacket import RtpPacket
from ServerWorker import ServerWorker
from ServerDatabase import ServerDatabase

import utils.ports as Portas

class Server:
    def __init__(self, server_id: str):
        self.id = server_id
        self.serverSocket = None

        self.manager = None

        self.status = True

    def run(self):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind(('', Portas.SERVER))
        self.serverSocket.listen()

        self.manager = ServerDatabase(self.id)
        
        while self.status:
            clientSocket, (addr, port) = self.serverSocket.accept()
            worker = ServerWorker(clientSocket, (addr, port), self.manager)
            threading.Thread(target=worker.run, args=()).start()

    def stop(self):
        self.status = False
        self.serverSocket.close()
        print("Server closed")

def main():
    if len(sys.argv) != 2:
        print("[Usage: python3 server.py <server_id>]")
        print("  <server_id>: Unique identifier for the server.")
        sys.exit(1)

    server_id = sys.argv[1]
    server = Server(server_id)
    try:
        server.run()
        while True: 
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping server...")
        server.stop()
        sys.exit(0)

if __name__ == '__main__':
    main()
