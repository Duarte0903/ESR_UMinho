import os

from utils.VideoStream import VideoStream
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