from tkinter import *
import tkinter.messagebox as tkMessageBox
from PIL import Image, ImageTk

import sys, socket

import utils.bootstrap as Bootstrapper
import utils.aux as Aux
import utils.ports as Portas

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

        # Frame para o vídeo
        self.videoFrame = Label(self.window, bg="black", width=80, height=20)
        self.videoFrame.pack(pady=1)

        # Frame para os botões
        buttonFrame = Frame(self.window)
        buttonFrame.pack(pady=10)

        self.playButton = Button(buttonFrame, text="Play", width=10, command=self.play)
        self.playButton.pack(side=LEFT, padx=5)

        self.pauseButton = Button(buttonFrame, text="Pause", width=10, command=self.pause_video)
        self.pauseButton.pack(side=LEFT, padx=5)

        self.stopButton = Button(buttonFrame, text="Stop", width=10, command=self.stop)
        self.stopButton.pack(side=LEFT, padx=5)

        # Iniciar o loop da interface
        self.window.mainloop()

    # Funções dos botões
    def play(self):
        if not self.playing:
            self.pause = False

    def pause_video(self):
        if self.playing and not self.pause:
            self.pause = True

    def stop(self):
        if self.playing:
            self.playing = False

    # Função para exibir um frame de vídeo (placeholder)
    def update_video_frame(self, image_path=None):
        if image_path:
            try:
                img = Image.open(image_path)
                img = img.resize((400, 300))  # Redimensionar para caber no frame
                img_tk = ImageTk.PhotoImage(img)
                self.videoFrame.configure(image=img_tk, text="")
                self.videoFrame.image = img_tk
            except Exception as e:
                tkMessageBox.showerror("Erro", f"Não foi possível carregar o frame: {e}")
        else:
            self.videoFrame.config(text="Sem vídeo disponível.", image="")

    def requestVideo(self):
        pass

    def checkVideo(self, video_requested):
        return False

    def start(self):
        try:
            self.neighbours = Bootstrapper.get_neighbours(Aux.get_local_address())

            self.tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcpSocket.connect(("10.0.10.10", Portas.SERVER)) # Hard coded para o servidor para já depois meto os vizinhos a funcionar com RTT

            self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udpSocket.bind(('', Portas.CLIENTEUDP))
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
            self.requestVideo()
        else:
            print("Video não encontrado no sistema. A fechar...")
            sys.exit(0)


if __name__ == "__main__":
    client = OClient()
    client.start()
