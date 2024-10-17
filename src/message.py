import random

Class Message:
    self.id = 0
    self.type = 0
    self.sender = ""
    self.content = ""

    def __init__(self, type, sender, content):
        self.id = random.randint(0, 100000)
        self.type = type
        self.sender = sender
        self.content = content

    def get_id(self):
        return self.id
    
    def get_type(self):
        return self.type

    def get_sender(self):
        return self.sender

    def get_content(self):
        return self.content

    def serialize(self):
        return f"{self.id}:{self.type}:{self.sender}:{self.content}".encode()

    def deserialize(data):
        id, type, sender, content = data.decode().split(":")
        return Message(id, type, sender, content)

    def __str__(self):
        return f"Message {self.id} from {self.sender}: {self.content}"