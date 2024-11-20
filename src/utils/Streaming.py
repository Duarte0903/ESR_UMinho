class Streaming:
    def __init__(self, video):
        self.video = video

        self.usersConnected = 1

        self.lastFrameSize = 0
        self.lastFrame = b''

    def setFrame(self, frameSize, frame):
        self.lastFrameSize = frameSize
        self.lastFrame = frame

    def getFrame(self):
        return (self.lastFrameSize, self.frame)

    def run(self):
        while this.usersConnected > 0:

        pass