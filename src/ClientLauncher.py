import sys
from tkinter import Tk
from Client import Client

import utils.ports as Portas
if __name__ == "__main__":
	try:
		serverAddr = "10.0.10.10"
		serverPort = Portas.SERVER
		rtpPort = None
		fileName = None	
	except:
		print("[Usage: ClientLauncher.py Server_name Server_port RTP_port Video_file]\n")	
	
	root = Tk()
	
	# Create a new client
	app = Client(root, serverAddr, serverPort, rtpPort, fileName)
	app.master.title("RTPClient")	
	root.mainloop()
	