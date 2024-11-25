import socket, time

import utils.bootstrap as Bootstrapper
import utils.aux as Aux
import utils.ports as Portas
import utils.messages as Messages

class NodeDatabase:
    def __init__(self):
        self.neighbours = Bootstrapper.get_neighbours(Aux.get_local_address())
        self.neighboursDelay = {}

        self.videosStreaming = {}

        self.TTL = 0

        self.viewedMessages = {}

    def getNeighbours(self):
        return self.neighbours

    def handleProbing(self, currentTTL, sender):
        self.TTL = int(currentTTL[2]) + 1

        if sender not in self.neighboursDelay.keys():
            self.neighboursDelay[sender] = time.time() - float(currentTTL[3])

        if self.checkViewedMessage(int(currentTTL[0]), currentTTL):
            return

        probeMessage = Messages.probeRequest(self.TTL, time.time(), currentTTL[0]).encode('utf-8')

        for neighbour in self.neighbours:
            probingSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                probingSocket.connect((neighbour, Portas.NODO))
            except ConnectionRefusedError:
                probingSocket.close()
                continue

            probingSocket.sendall(probeMessage)

            time.sleep(0.03)

            probingSocket.sendall(Messages.disconnectMessage().encode('utf-8'))

            probingSocket.close()

    def checkViewedMessage(self, id: int, message):
        if id in self.viewedMessages.keys():
            return True
        else:
            self.viewedMessages[id] = message
            return False

