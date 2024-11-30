from random import randint
import sys, traceback, threading, socket, struct, time

from utils.VideoStream import VideoStream
from utils.RtpPacket import RtpPacket

import utils.messages as Messages
import utils.ports as Portas

class ServerWorker:
	def __init__(self, clientSocket, clientInfo, manager):
		self.clientSocket = clientSocket
		self.clientInfo = clientInfo

		self.clientUDPPort = 0

		self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		self.manager = manager

		self.requested_video = None

		self.status = True
		self.streaming = True

	def startStream(self):
		self.clientSocket.send(struct.pack('?', self.manager.enableStream(self.requested_video, self.clientInfo[0])))
		errorCounter = 0
		while self.streaming:
			frame_size, frame = self.manager.getFrame(self.requested_video)

			# Criar o packet RTP

			# Verificar se o frame existe (fim do vídeo)
			if not frame:
				errorCounter += 1
				time.sleep(0.03)
				if errorCounter > 10:
					print("Erro ao obter um frame após 10 tentativas. A fechar...")
					break
				continue

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

		self.manager.disconnectUser(self.requested_video, self.clientInfo[0])

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
				self.clientSocket.send(struct.pack('?', False))
				continue

			if request_tokens[1] == Messages.CHECK_VIDEO:
				self.clientSocket.send(struct.pack('?', self.manager.checkVideo(request_tokens[2])))

			elif request_tokens[1] == Messages.READY:
				self.requested_video = request_tokens[2]
				self.clientUDPPort = int(request_tokens[3])
				threading.Thread(target=self.startStream, args=()).start()
			
			elif request_tokens[1] == Messages.DISCONNECT:
				self.streaming = False
				self.status = False
				continue

		print(f'Cliente {self.clientInfo[0]} desconectado com sucesso')