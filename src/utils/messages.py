import random

# TOKENS

CHECK_VIDEO = "CHECK_VIDEO"
READY = "READY"
DISCONNECT = "DISCONNECT"
PROBING = "PROBE"

def check_video(video: str):
    return f'{random.randrange(1, 100000)} {CHECK_VIDEO} {video}'

def readyMessage(video: str, port: int):
    return f'{random.randrange(1, 100000)} {READY} {video} {port}'

def disconnectMessage():
    return f'{random.randrange(1, 100000)} {DISCONNECT}'

def probeRequest(currentTTL: int, id = 0):
    return f'{random.randrange(1, 100000) if id == 0 else id} {PROBING} {currentTTL}'