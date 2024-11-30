"""
##############################################################
# Programa: Overlay Network Visualizer
# Descrição: Permite ver em tempo real o estado dos nodos de streaming numa rede, bem como os caminhos que uma stream está a fazer desde o servidor de streaming até ao cliente que pediu um conteúdo
# Autor: Pedro Silva
# Versão: 1.11
##############################################################
"""
import tkinter as tk
import socket
import threading

nodes = {
    "n1": (980, 407),
    "n2": (842, 409),
    "n3": (39, 192),
    "n4": (32, 366),
    "n6": (455, 208),
    "n7": (455, 402),
    "n5": (28, 503),
    "n8": (27, 622),
    "n11": (452, 591),
    "n17": (559, 524),
    "n18": (745, 307)
}

edges = {
    ("n2", "n1"): 0,
    ("n2", "n18"): 0,
    ("n2", "n17"): 0,
    ("n2", "n7"): 0,
    ("n18", "n17"): 0,
    ("n18", "n7"): 0,
    ("n18", "n6"): 0,
    ("n17", "n11"): 0,
    ("n17", "n7"): 0,
    ("n6", "n3"): 0,
    ("n6", "n4"): 0,
    ("n6", "n7"): 0,
    ("n7", "n3"): 0,
    ("n7", "n4"): 0,
    ("n7", "n5"): 0,
    ("n7", "n8"): 0,
    ("n7", "n11"): 0,
    ("n11", "n5"): 0,
    ("n11", "n8"): 0
}

streamCounters = {
    "n1": (0, None),
    "n2": (0, None),
    "n3": (0, None),
    "n4": (0, None),
    "n6": (0, None),
    "n7": (0, None),
    "n5": (0, None),
    "n8": (0, None),
    "n11": (0, None),
    "n17": (0, None),
    "n18": (0, None)
}

def drawStreamCounters():
    for node, (count, string) in streamCounters.items():
        if string is not None:
            canvas.delete(string)
        x, y = nodes[node]
        streamCounters[node] = (count, canvas.create_text(x, y-20, text=f'{count}'))

def draw_network(canvas):
    for node, (x, y) in nodes.items():
        canvas.create_oval(x-10, y-10, x+10, y+10, fill="blue")
        canvas.create_text(x, y+20, text=node)

    for (start, end), _ in edges.items():
        canvas.create_line(nodes[start], nodes[end], fill="black", width=2)

    drawStreamCounters()

def update_path(canvas, node1, node2):
    count = streamCounters[node2][0]
    count += 1
    streamCounters[node2] = (count, streamCounters[node2][1])
    edges[(node1, node2) if (node1, node2) in edges else (node2, node1)] += 1

    if edges[(node1, node2) if (node1, node2) in edges else (node2, node1)] == 1:
        canvas.create_line(nodes[node1], nodes[node2], fill="red", width=2)

    drawStreamCounters()

def delete_path(canvas, node1, node2):
    count = streamCounters[node2][0]

    count -= 1
    edges[(node1, node2) if (node1, node2) in edges else (node2, node1)] -= 1

    streamCounters[node2] = (count, streamCounters[node2][1])

    if edges[(node1, node2) if (node1, node2) in edges else (node2, node1)] == 0:
        canvas.create_line(nodes[node1], nodes[node2], fill="black", width=2)
    
    drawStreamCounters()

def listener():
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind(('', 12345))
    serverSocket.listen()

    print("À escuta em " + socket.gethostname())

    while True:
        client_socket, _ = serverSocket.accept()
        data = client_socket.recv(1024).decode()[2:]

        nodess = data.split(" ")
        if int(nodess[2]) == 1:
            update_path(canvas, nodess[0], nodess[1])
        else:
            delete_path(canvas, nodess[0], nodess[1])

def start_listener():
    listener_thread = threading.Thread(target=listener, daemon=True)
    listener_thread.start()

root = tk.Tk()
canvas = tk.Canvas(root, width=1080, height=720)
canvas.pack()

draw_network(canvas)

start_listener()

root.mainloop()