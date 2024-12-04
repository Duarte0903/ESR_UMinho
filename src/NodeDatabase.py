import socket, time, struct, threading

import utils.bootstrap as Bootstrapper
import utils.aux as Aux
import utils.ports as Portas
import utils.messages as Messages
import utils.updateVisualizer as UpdateVisualizer

from utils.Streaming import Streaming

class NodeDatabase:
    def __init__(self):
        self.neighbours = Bootstrapper.get_neighbours(Aux.get_local_address())
        self.neighboursDelay = {}

        self.videosStreaming = {}

        self.TTL = 0

        self.viewedMessages = {}

    def getNeighbours(self):
        return self.neighbours

    def checkVideoOnSystem(self, sender, video_requested: str, original_request: str):
        if video_requested not in self.videosStreaming.keys():
            for neighbour in self.neighbours:
                if neighbour not in self.neighboursDelay.keys() or neighbour == sender:
                    continue
                
                aux = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    aux.connect((neighbour, Portas.NODO))
                except ConnectionRefusedError:
                    aux.close()
                    continue
                    
                aux.sendall(original_request.encode('utf-8'))

                if struct.unpack('?',  aux.recv(1))[0]:
                    aux.sendall(Messages.disconnectMessage().encode('utf-8'))
                    aux.close()
                    return True

                aux.sendall(Messages.disconnectMessage().encode('utf-8'))
                aux.close()
        else:
            return True
        return False

    def streamInit(self, video, stream, aux):
        streamThread = threading.Thread(target=stream.run, args=())
        streamThread.start()

        print(f'Stream do vídeo {video} iniciada')

        streamThread.join()
        del self.videosStreaming[video]
        print(f'Stream do vídeo {video} fechada')

        aux.sendall(Messages.disconnectMessage().encode('utf-8'))
        aux.close()

    def enableStream(self, video_requested: str, original_request: str, udpPort, sender):
        if video_requested not in self.videosStreaming.keys():
            # ordered_neighbours = sorted(sorted(self.neighboursDelay, key=lambda k: self.neighboursDelay[k][1]), key=lambda z: self.neighboursDelay[z][0])

            ordered_neighbours = Aux.generate_metrics(self.neighboursDelay)

            for neighbour in ordered_neighbours:
                aux = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                aux.connect((neighbour[0], Portas.NODO))

                aux.sendall(original_request.encode('utf-8'))

                if struct.unpack('?', aux.recv(1))[0] is not True:
                    aux.sendall(Messages.disconnectMessage().encode('utf-8'))
                    aux.close()
                    continue
                    
                udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                udpSocket.bind(('', udpPort))
                
                stream = Streaming(video_requested, udpSocket)
                self.videosStreaming[video_requested] = stream

                threading.Thread(target=self.streamInit, args=(video_requested, stream, aux)).start()

                UpdateVisualizer.update(Bootstrapper.getHostname(sender), Bootstrapper.getHostname(Aux.get_local_address()), 1)

                return True
        else:
            self.connectUser(video_requested)
            UpdateVisualizer.update(Bootstrapper.getHostname(sender), Bootstrapper.getHostname(Aux.get_local_address()), 1)
            return True
        return False

    def getFrame(self, video_requested):
        return self.videosStreaming[video_requested].getFrame()

    def handleProbing(self, currentTTL, sender):
        self.TTL = int(currentTTL[2]) + 1

        self.neighboursDelay[sender] = (time.time() - float(currentTTL[3]), int(currentTTL[2]))

        if self.checkViewedMessage(int(currentTTL[0]), currentTTL):
            return

        for neighbour in self.neighbours:
            probingSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                probingSocket.connect((neighbour, Portas.NODO))
            except ConnectionRefusedError:
                probingSocket.close()
                continue

            probeMessage = Messages.probeRequest(self.TTL, time.time(), currentTTL[0]).encode('utf-8')

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

    def connectUser(self, video):
        self.videosStreaming[video].connectUser()

    def disconnectUser(self, video, sender):
        self.videosStreaming[video].disconnectUser()
        UpdateVisualizer.update(Bootstrapper.getHostname(sender), Bootstrapper.getHostname(Aux.get_local_address()), 0)

