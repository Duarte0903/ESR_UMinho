import random

# TOKENS

CHECK_VIDEO = "CHECK_VIDEO"

def check_video(video: str):
    return f'{random.randrange(1, 100000)} {CHECK_VIDEO} {video}'