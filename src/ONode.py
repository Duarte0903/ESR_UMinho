import sys, socket, threading

import utils.ports as Portas

from NodeDatabase import NodeDatabase
from NodeWorker import NodeWorker

class ONode:
    def __init__(self):
        self.nodoSocket = None

        self.manager = None

        self.status = True

    def run(self):
        self.nodoSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nodoSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.nodoSocket.bind(('', Portas.NODO))
        self.nodoSocket.listen()

        self.manager = NodeDatabase()

        while self.status:
            clientSocket, (addr, port) = self.nodoSocket.accept()
            worker = NodeWorker(clientSocket, (addr, port), self.manager)
            threading.Thread(target=worker.run, args=()).start()

    def stop(self):
        self.status = False
        self.nodoSocket.close()
        print("Nodo closed")

def main():
    node = ONode()
    try:
        node.run()
    except KeyboardInterrupt:
        print("Stopping node...")
        node.stop()
        sys.exit(0)

if __name__ == "__main__":
    main()