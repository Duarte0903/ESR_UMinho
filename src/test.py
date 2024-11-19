import socket

import utils.ports as Ports

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect(("10.0.10.10", Ports.SERVER))