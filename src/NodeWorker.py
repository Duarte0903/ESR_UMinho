import struct, socket, threading, time

import utils.messages as Messages

from utils.RtpPacket import RtpPacket

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

    def startStream(self, original_request):
        check = self.manager.enableStream(self.requested_video, original_request, self.clientUDPPort)
        self.clientSocket.send(struct.pack('?', check))
        if check is not True:
            return
        errorCounter = 0
        while self.streaming:
            frame_size, frame = self.manager.getFrame(self.requested_video)
            
            # Criar o packet RTP
            
            # Verificar se o frame existe (fim do vídeo)
            if not frame:
                errorCounter += 1
                time.sleep(0.1)
                if errorCounter > 10:
                    print("Erro ao obter um frame após 10 tentativas. A fechar...")
                    break
            
            seqnum = 0
            ssrc = 12345
            
            # Criar o pacote RTP
            rtp_packet = RtpPacket()
            rtp_packet.encode(
				version=2,             # Versão RTP padrão (2 bits)
				padding=0,             # Sem padding (1 bit)
				extension=0,           # Sem extensão (1 bit)
				cc=0,                  # Sem CSRCs (4 bits)
				seqnum=seqnum,         # Número de sequência
				marker=0,              # Sem marcador (1 bit)
				pt=26,                 # Tipo de payload (H.263 = 26, pode ajustar conforme necessário)
				ssrc=ssrc,             # Identificador único do stream
				payload=frame          # Frame como payload do RTP
			)
            
            # Incrementar o número de sequência para o próximo frame
            seqnum += 1
            
            # Enviar o pacote RTP através do socket UDP
            try:
                self.udpSocket.sendto(rtp_packet.getPacket(), (self.clientInfo[0], self.clientUDPPort))
            except Exception as e:
                print(f"Erro ao enviar frame: {e}")
                
            time.sleep(0.04)
            
        self.manager.disconnectUser(self.requested_video)

    def checkVideoOnSystem(self, videoRequested: str):
        if self.manager.checkVideo(videoRequested):
            return True
            
        # Lógica para pedir aos vizinhos se alguém tem vídeo
        neighbours = self.manager.getNeighbours()
        return False

    def run(self):
        print(f'Cliente {self.clientInfo[0]} conectado com sucesso')
        while self.status:
            try:
                request = self.clientSocket.recv(1024).decode('utf-8')
            except Exception:
                self.streaming = False
                self.status = False
                continue

            # Handle de perdas de conexão
            if not request:
                print(f'Cliente {self.clientInfo[0]} desconectado inesperadamente')
                self.streaming = False
                self.status = False 
                return
                
            request_tokens = request.split(' ')
            if request_tokens[1] == Messages.PROBING: # Lido mesmo que já tenha lido antes para guardar timestamps de outros nodos (exceção).
                self.manager.handleProbing(request_tokens, self.clientInfo[0])

            elif self.manager.checkViewedMessage(int(request_tokens[0]), request_tokens):
                self.clientSocket.send(struct.pack('?', False))
                continue
                
            elif request_tokens[1] == Messages.CHECK_VIDEO:
                self.clientSocket.send(struct.pack('?', self.manager.checkVideoOnSystem(self.clientInfo[0], request_tokens[2], request)))
                
            elif request_tokens[1] == Messages.READY:
                self.requested_video = request_tokens[2]
                self.clientUDPPort = int(request_tokens[3])
                threading.Thread(target=self.startStream, args=(request, )).start()
                
            elif request_tokens[1] == Messages.DISCONNECT:
                self.streaming = False
                self.status = False
                continue
                
        print(f'Cliente {self.clientInfo[0]} desconectado com sucesso')