import os, threading, time, socket

from utils.VideoStream import VideoStream
from utils.Streaming import Streaming

import utils.bootstrap as Bootstrapper
import utils.ports as Portas
import utils.messages as Messages

class ServerDatabase:    
    def __init__(self, server_id):
        self.id = server_id
        self.neighbours = Bootstrapper.get_neighbours_server(self.id)

        self.videos = self.loadVideos()
        self.videosStreaming = {}

        self.sendProbes()

        self.viewedMessages = {}

    def sendProbes(self):
        probeMessage = Messages.probeRequest(0, time.time()).encode('utf-8')
        for neighbour in self.neighbours:
            probingSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                probingSocket.connect((neighbour, Portas.NODO))
            except ConnectionRefusedError:
                probingSocket.close()
                continue

            probingSocket.sendall(probeMessage)

            time.sleep(0.01)

            probingSocket.sendall(Messages.disconnectMessage().encode('utf-8'))

            probingSocket.close()

    def loadVideos(self):
        videos = {}
        with os.scandir("videos") as video_dir:
            for video_file in video_dir:
                videos[video_file.name] = VideoStream(video_file.name)

        return videos

    def checkVideo(self, video: str):
        return video in self.videos

    def lambdaStreamInit(self, video, videoObj, stream):
        streamThread = threading.Thread(target=stream.run, args=())
        streamThread.start()

        print(f'Stream do vídeo {video} iniciada')

        streamThread.join()
        del self.videosStreaming[videoObj]
        print(f'Stream do vídeo {video} fechada')

        videoObj.resetVideo()

    def enableStream(self, video: str):
        videoObj = self.videos[video]
        if videoObj not in self.videosStreaming:
            stream = Streaming(videoObj)
            self.videosStreaming[videoObj] = stream

            threading.Thread(target=self.lambdaStreamInit, args=(video, videoObj, stream)).start()
        else:
            self.connectUser(videoObj)
        return True

    def getFrame(self, video: str):
        return self.videosStreaming[self.videos[video]].getFrame()

    def connectUser(self, videoObj):
        self.videosStreaming[videoObj].connectUser()

    def disconnectUser(self, video: str):
        self.videosStreaming[self.videos[video]].disconnectUser()

    def checkViewedMessage(self, id: int, message):
        if id in self.viewedMessages.keys():
            return True
        else:
            self.viewedMessages[id] = message
            return False