import random

BOOTSTRAP = 2000
SERVER = 5000
NODO = 5000

# Gerador de portas aleatórias para evitar conflitos de portas durante o multi-content nos nodos
def generateClientUDPPort():
    return random.randint(1024, 49151)