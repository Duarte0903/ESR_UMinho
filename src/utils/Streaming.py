import time

from utils.VideoStream import VideoStream
from utils.RtpPacket import RtpPacket

class Streaming:
    def __init__(self, video, udpSocket=None):
        self.video = video

        self.viewers = 1

        self.udpSocket = udpSocket

        self.lastFrameSize = 0
        self.lastFrame = b''

    def setFrame(self, frameSize, frame):
        self.lastFrameSize = frameSize
        self.lastFrame = frame

    def getFrameFromNeighbour(self):
        # Receber dados do servidor via socket UDP
        packet, server_address = self.udpSocket.recvfrom(65535)
        
        # Criar uma instância do pacote RTP
        rtp_packet = RtpPacket()
        rtp_packet.decode(packet)
        
        # Obter o payload (frame) do pacote RTP
        frame = rtp_packet.getPayload()
        
        # Retornar o frame recebido
        
        return len(frame), frame

    def getFrame(self):
        return (self.lastFrameSize, self.lastFrame)

    def connectUser(self):
	    self.viewers += 1

    def disconnectUser(self):
        self.viewers -= 1

    def run(self):
        while self.viewers > 0:
            if isinstance(self.video, VideoStream):
                self.lastFrameSize, self.lastFrame = self.video.nextFrame()
            elif isinstance(self.video, str):
                self.lastFrameSize, self.lastFrame = self.getFrameFromNeighbour()

            time.sleep(0.04)