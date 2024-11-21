import time

class Streaming:
    def __init__(self, video):
        self.video = video

        self.viewers = 1

        self.lastFrameSize = 0
        self.lastFrame = b''

    def setFrame(self, frameSize, frame):
        self.lastFrameSize = frameSize
        self.lastFrame = frame

    def getFrame(self):
        return (self.lastFrameSize, self.lastFrame)

    def connectUser(self):
	    self.viewers += 1

    def disconnectUser(self):
        self.viewers -= 1

    def run(self):
        while self.viewers > 0:
            self.lastFrameSize, self.lastFrame = self.video.nextFrame()

            time.sleep(0.04)