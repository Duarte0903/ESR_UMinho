from tkinter import *
import tkinter.messagebox as tkMessageBox
from PIL import Image, ImageTk

import sys, socket, struct, threading, io, time

import utils.bootstrap as Bootstrapper
import utils.aux as Aux
import utils.ports as Portas
import utils.messages as Messages
from utils.RtpPacket import RtpPacket

class OClient:
    def __init__(self):
        # Atributos relacionados ao cliente
        self.tcpSocket = None
        self.udpSocket = None
        self.neighbours = []
        self.playing = False
        self.pause = False

        # Atributos da interface
        self.window = None

        self.buttonFrame = None
        self.playButton = None
        self.pauseButton = None
        self.stopButton = None

        self.videoFrame = None

    def setup(self):
        # Configuração da janela principal
        self.window = Tk()
        self.window.title("Deloitte Tube")
        self.window.geometry("600x400")  # Define dimensões iniciais da janela
        self.window.resizable(False, False)  # Evita redimensionamento
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Frame para o vídeo
        self.videoFrame = Label(self.window, bg="black", width=600, height=350)
        self.videoFrame.pack(pady=1)

        # Frame para os botões
        self.buttonFrame = Frame(self.window)
        self.buttonFrame.pack(pady=10)

        self.playButton = Button(self.buttonFrame, text="Play", width=10, command=self.play)
        self.playButton.pack(side=LEFT, padx=5)

        self.pauseButton = Button(self.buttonFrame, text="Pause", width=10, command=self.pause_video)
        self.pauseButton.pack(side=LEFT, padx=5)

        self.stopButton = Button(self.buttonFrame, text="Stop", width=10, command=self.stop)
        self.stopButton.pack(side=LEFT, padx=5)

    # Funções dos botões
    def play(self):
        if self.pause:
            self.pause = False

    def pause_video(self):
        if self.playing and not self.pause:
            self.pause = True

    def stop(self):
        if self.window:
            self.window.destroy()
            self.window = None
            
        self.playing = False
        self.pause = True
                
        if self.tcpSocket:
            try:
                self.disconnect()
                self.tcpSocket.close()
            except Exception as e:
                print(f"Erro ao fechar socket TCP: {e}")
                
        sys.exit(0)

    def on_closing(self):
        self.stop()

    def disconnect(self):
        self.tcpSocket.sendall(Messages.disconnectMessage().encode('utf-8'))

    def update_video_frame(self, frame_bytes=None):
        if frame_bytes:
            try:
                # Carregar a imagem diretamente dos bytes
                img = Image.open(io.BytesIO(frame_bytes))
                
                # Redimensionar a imagem para caber no frame da interface (opcional)
                img = img.resize((600, 350))  # Ajuste os valores conforme necessário
                
                # Converter a imagem para o formato PhotoImage do Tkinter
                if self.window is not None:
                    img_tk = ImageTk.PhotoImage(img)
                
                # Atualizar o widget da interface com a nova imagem
                self.videoFrame.configure(image=img_tk, text="")
                self.videoFrame.image = img_tk
            except Exception as e:
                pass
        else:
            # Mostrar mensagem padrão caso não haja frame disponível
            self.videoFrame.config(text="Sem vídeo disponível.", image="")

    def requestVideo(self, video_requested):
        self.tcpSocket.sendall(Messages.readyMessage(video_requested, self.udpSocket.getsockname()[1]).encode('utf-8'))
        self.receiveFrame()

    def receiveFrame(self):
        self.playing = True
        while self.playing:
            while self.pause and self.playing:
                time.sleep(0.04)
            try:
                # Receber dados do servidor via socket UDP
                packet, server_address = self.udpSocket.recvfrom(65535)
                
                # Criar uma instância do pacote RTP
                rtp_packet = RtpPacket()
                rtp_packet.decode(packet)
                
                # Obter o payload (frame) do pacote RTP
                frame = rtp_packet.getPayload()
                
                # Atualizar a interface com o frame recebido
                self.update_video_frame(frame)
            except socket.timeout:
                # Se o socket estiver fechado, interrompe o loop
                if not self.playing:
                    self.udpSocket.close()
                    break
            except Exception as e:
                print(f"Erro ao receber frame: {e}")

    def checkVideo(self, video_requested):
        self.tcpSocket.sendall(Messages.check_video(video_requested).encode('utf-8'))

        response = self.tcpSocket.recv(1)

        return struct.unpack('?', response)[0]

    def start(self):
        try:
            self.neighbours = Bootstrapper.get_neighbours(Aux.get_local_address())

            self.tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            for neighbour in self.neighbours:
                try:
                    self.tcpSocket.connect((neighbour, Portas.SERVER))
                    break
                except ConnectionRefusedError:
                    pass

            self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udpSocket.settimeout(0.6)
            self.udpSocket.bind(('', Portas.generateClientUDPPort()))
        except:
            print("Erro a conectar-se")
            if self.tcpSocket:
                self.tcpSocket.close()
            if self.udpSocket:
                self.udpSocket.close()
            sys.exit(1)

        video_requested = input("Bem-vindo ao Deloitte Tube! Escolha um vídeo para assistir: ")

        if self.checkVideo(video_requested):
            self.setup()
            threading.Thread(target=self.requestVideo, args=(video_requested,)).start()
            self.window.mainloop()
        else:
            print("Video não encontrado no sistema. A fechar...")
            sys.exit(0)


if __name__ == "__main__":
    client = OClient()
    client.start()
