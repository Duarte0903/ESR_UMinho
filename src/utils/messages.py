import random

# TOKENS

CHECK_VIDEO = "CHECK_VIDEO"
READY = "READY"
DISCONNECT = "DISCONNECT"

def check_video(video: str):
    return f'{random.randrange(1, 100000)} {CHECK_VIDEO} {video}'

def readyMessage(video: str, port: int):
    return f'{random.randrange(1, 100000)} {READY} {video} {port}'

def disconnectMessage():
    return f'{random.randrange(1, 100000)} {DISCONNECT}'