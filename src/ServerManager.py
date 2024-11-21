import os, threading, time

from utils.VideoStream import VideoStream
from utils.Streaming import Streaming
import utils.bootstrap as Bootstrapper

class ServerManager:    
    def __init__(self, server_id):
        self.id = server_id
        self.neighbours = Bootstrapper.get_neighbours_server(self.id)

        self.videos = self.loadVideos()
        self.streamingCurrently = {}

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

        streamThread.join()
        del self.streamingCurrently[videoObj]
        print(f'Stream do vídeo {video} fechada')

    def enableStream(self, video: str):
        videoObj = self.videos[video]
        if videoObj not in self.streamingCurrently:
            stream = Streaming(videoObj)
            self.streamingCurrently[videoObj] = stream

            threading.Thread(target=self.lambdaStreamInit, args=(video, videoObj, stream)).start()

            time.sleep(0.01) # Cooldown para dar tempo de inicializar a stream na base de dados
        else:
            self.connectUser(videoObj)

    def getFrame(self, video: str):
        return self.streamingCurrently[self.videos[video]].getFrame()

    def connectUser(self, videoObj):
        self.streamingCurrently[videoObj].connectUser()

    def disconnectUser(self, video: str):
        self.streamingCurrently[self.videos[video]].disconnectUser()