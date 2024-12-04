import socket

def update(node1, node2, status):
    aux = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        aux.connect(("10.0.14.1", 12345))
    except ConnectionRefusedError:
        return

    aux.sendall(f'  {node1} {node2} {status}'.encode('utf-8'))

    aux.close()