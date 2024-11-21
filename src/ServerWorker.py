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

		self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		self.manager = manager

		self.requested_video = None

		self.status = True
		self.streaming = True

	def startStream(self):
		self.manager.enableStream(self.requested_video)
		while self.streaming:
			frame_size, frame = self.manager.getFrame(self.requested_video)

			# Criar o packet RTP

			# Verificar se o frame existe (fim do vídeo)
			if not frame:
				print("Fim do stream.")
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
				self.udpSocket.sendto(rtp_packet.getPacket(), (self.clientInfo[0], Portas.CLIENTEUDP))
			except Exception as e:
				print(f"Erro ao enviar frame: {e}")

			time.sleep(0.04)

		self.manager.disconnectUser(self.requested_video)

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
			if request_tokens[1] == Messages.CHECK_VIDEO:
				self.clientSocket.send(struct.pack('?', self.manager.checkVideo(request_tokens[2])))

			elif request_tokens[1] == Messages.READY:
				self.requested_video = request_tokens[2]
				threading.Thread(target=self.startStream, args=()).start()
			
			elif request_tokens[1] == Messages.DISCONNECT:
				self.streaming = False
				self.status = False
				continue

		print(f'Cliente {self.clientInfo[0]} desconectado com sucesso')
	
	'''SETUP = 'SETUP'
	PLAY = 'PLAY'
	PAUSE = 'PAUSE'
	TEARDOWN = 'TEARDOWN'
	
	INIT = 0
	READY = 1
	PLAYING = 2
	state = INIT

	OK_200 = 0
	FILE_NOT_FOUND_404 = 1
	CON_ERR_500 = 2
	
	clientInfo = {}
	
	def __init__(self, clientInfo):
		self.clientInfo = clientInfo
		
	def run(self):
		threading.Thread(target=self.recvRtspRequest).start()
	
	def recvRtspRequest(self):
		"""Receive RTSP request from the client."""
		connSocket = self.clientInfo['rtspSocket'][0]
		while True:            
			data = connSocket.recv(256)
			if data:
				print("Data received:\n" + data.decode("utf-8"))
				self.processRtspRequest(data.decode("utf-8"))
	
	def processRtspRequest(self, data):
		"""Process RTSP request sent from the client."""
		# Get the request type
		request = data.split('\n')
		line1 = request[0].split(' ')
		requestType = line1[0]
		
		# Get the media file name
		filename = line1[1]
		
		# Get the RTSP sequence number 
		seq = request[1].split(' ')
		
		# Process SETUP request
		if requestType == self.SETUP:
			if self.state == self.INIT:
				# Update state
				print("processing SETUP\n")
				
				try:
					self.clientInfo['videoStream'] = VideoStream(filename)
					self.state = self.READY
				except IOError:
					self.replyRtsp(self.FILE_NOT_FOUND_404, seq[1])
				
				# Generate a randomized RTSP session ID
				self.clientInfo['session'] = randint(100000, 999999)
				
				# Send RTSP reply
				self.replyRtsp(self.OK_200, seq[1])
				
				# Get the RTP/UDP port from the last line
				self.clientInfo['rtpPort'] = request[2].split(' ')[3]
		
		# Process PLAY request 		
		elif requestType == self.PLAY:
			if self.state == self.READY:
				print("processing PLAY\n")
				self.state = self.PLAYING
				
				# Create a new socket for RTP/UDP
				self.clientInfo["rtpSocket"] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				
				self.replyRtsp(self.OK_200, seq[1])
				
				# Create a new thread and start sending RTP packets
				self.clientInfo['event'] = threading.Event()
				self.clientInfo['worker']= threading.Thread(target=self.sendRtp) 
				self.clientInfo['worker'].start()
		
		# Process PAUSE request
		elif requestType == self.PAUSE:
			if self.state == self.PLAYING:
				print("processing PAUSE\n")
				self.state = self.READY
				
				self.clientInfo['event'].set()
			
				self.replyRtsp(self.OK_200, seq[1])
		
		# Process TEARDOWN request
		elif requestType == self.TEARDOWN:
			print("processing TEARDOWN\n")

			self.clientInfo['event'].set()
			
			self.replyRtsp(self.OK_200, seq[1])
			
			# Close the RTP socket
			self.clientInfo['rtpSocket'].close()
			
	def sendRtp(self):
		"""Send RTP packets over UDP."""
		while True:
			self.clientInfo['event'].wait(0.05) 
			
			# Stop sending if request is PAUSE or TEARDOWN
			if self.clientInfo['event'].isSet(): 
				break 
				
			data = self.clientInfo['videoStream'].nextFrame()
			if data: 
				frameNumber = self.clientInfo['videoStream'].frameNbr()
				try:
					address = self.clientInfo['rtspSocket'][1][0]
					port = int(self.clientInfo['rtpPort'])
					self.clientInfo['rtpSocket'].sendto(self.makeRtp(data, frameNumber),(address,port))
				except:
					print("Connection Error")
					#print('-'*60)
					#traceback.print_exc(file=sys.stdout)
					#print('-'*60)

	def makeRtp(self, payload, frameNbr):
		"""RTP-packetize the video data."""
		version = 2
		padding = 0
		extension = 0
		cc = 0
		marker = 0
		pt = 26 # MJPEG type
		seqnum = frameNbr
		ssrc = 0 
		
		rtpPacket = RtpPacket()
		
		rtpPacket.encode(version, padding, extension, cc, seqnum, marker, pt, ssrc, payload)
		
		return rtpPacket.getPacket()
		
	def replyRtsp(self, code, seq):
		"""Send RTSP reply to the client."""
		if code == self.OK_200:
			#print("200 OK")
			reply = 'RTSP/1.0 200 OK\nCSeq: ' + seq + '\nSession: ' + str(self.clientInfo['session'])
			connSocket = self.clientInfo['rtspSocket'][0]
			connSocket.send(reply.encode())
		
		# Error messages
		elif code == self.FILE_NOT_FOUND_404:
			print("404 NOT FOUND")
		elif code == self.CON_ERR_500:
			print("500 CONNECTION ERROR")'''
