import struct, socket

import utils.messages as Messages

class NodeWorker:
    def __init__(self, clientSocket, clientInfo, manager):
        self.clientSocket = clientSocket
        self.clientInfo = clientInfo

        self.clientUDPPort = 0
        
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.manager = manager

        self.requested_video = None
        
        self.status = True
        self.streaming = True

    def checkVideoOnSystem(self, videoRequested: str):
        if self.manager.checkVideo(videoRequested):
            return True
            
        # Lógica para pedir aos vizinhos se alguém tem vídeo
        neighbours = self.manager.getNeighbours()
        return False

    def run(self):
        print(f'Cliente {self.clientInfo[0]} conectado com sucesso')
        while self.status:
            request = self.clientSocket.recv(1024).decode('utf-8')

            # Handle de perdas de conexão
            if not request:
                print(f'Cliente {self.clientInfo[0]} desconectado inesperadamente')
                self.streaming = False
                self.status = False 
                return
                
            request_tokens = request.split(' ')
            if self.manager.checkViewedMessage(int(request_tokens[0]), request_tokens):
                continue

            if request_tokens[1] == Messages.CHECK_VIDEO:
                self.clientSocket.send(struct.pack('?', self.checkVideoOnSystem()))
                
            elif request_tokens[1] == Messages.PROBING:
                self.manager.handleProbing(request_tokens, self.clientInfo[0])
                
            elif request_tokens[1] == Messages.READY:
                self.requested_video = request_tokens[2]
                self.clientUDPPort = int(request_tokens[3])
                threading.Thread(target=self.startStream, args=()).start()
                
            elif request_tokens[1] == Messages.DISCONNECT:
                self.streaming = False
                self.status = False
                continue
                
        print(f'Cliente {self.clientInfo[0]} desconectado com sucesso')