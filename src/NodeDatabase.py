import socket

import utils.bootstrap as Bootstrapper
import utils.aux as Aux
import utils.ports as Portas
import utils.messages as Messages

class NodeDatabase:
    def __init__(self):
        self.neighbours = Bootstrapper.get_neighbours(Aux.get_local_address())

        self.videosStreaming = {}

        self.TTL = 0

        self.viewedMessages = {}

    def getNeighbours(self):
        return self.neighbours

    def handleProbing(self, currentTTL, sender):
        self.TTL = int(currentTTL[2]) + 1

        for neighbour in self.neighbours:
            if neighbour == sender:
                continue

            probingSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                probingSocket.connect((neighbour, Portas.NODO))
            except ConnectionRefusedError:
                probingSocket.close()
                continue

            probingSocket.sendall(Messages.probeRequest(self.TTL, currentTTL[0]).encode('utf-8'))

            probingSocket.sendall(Messages.disconnectMessage().encode('utf-8'))

            probingSocket.close()

    def checkViewedMessage(self, id: int, message):
        if id in self.viewedMessages.keys():
            return True
        else:
            self.viewedMessages[id] = message
            return False

