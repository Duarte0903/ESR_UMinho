from tkinter import *
import tkinter.messagebox as tkMessageBox
from PIL import Image, ImageTk
import socket
import threading
import os
import random

from RtpPacket import RtpPacket  # Adjust the import based on your structure

CACHE_FILE_NAME = "cache-"
CACHE_FILE_EXT = ".jpg"

class ClienteGUI:
    
    # Initiation..
    def __init__(self, master, addr, port):
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.handler)
        
        # Create a frame to act as the border
        self.border_color = "#3498db"  # Example RGB color
        self.border_width = 5
        
        self.border_frame = Frame(self.master, background=self.border_color)
        self.border_frame.pack(fill=BOTH, expand=True, padx=self.border_width, pady=self.border_width)
        
        # Create the main frame inside the border
        self.main_frame = Frame(self.border_frame)
        self.main_frame.pack(fill=BOTH, expand=True)
        
        self.createWidgets()
        self.addr = addr
        self.port = int(port)
        self.rtspSeq = 0
        self.sessionId = 0
        self.requestSent = -1
        self.teardownAcked = 0
        self.openRtpPort()
        self.playMovie()
        self.frameNbr = 0
        
        self.change_color()  # Start changing the color
        
    def createWidgets(self):
        """Build GUI."""
        # Create Setup button
        self.setup = Button(self.main_frame, width=20, padx=3, pady=3)
        self.setup["text"] = "Setup"
        self.setup["command"] = self.setupMovie
        self.setup.grid(row=1, column=0, padx=2, pady=2)
        
        # Create Play button        
        self.start = Button(self.main_frame, width=20, padx=3, pady=3)
        self.start["text"] = "Play"
        self.start["command"] = self.playMovie
        self.start.grid(row=1, column=1, padx=2, pady=2)
        
        # Create Pause button            
        self.pause = Button(self.main_frame, width=20, padx=3, pady=3)
        self.pause["text"] = "Pause"
        self.pause["command"] = self.pauseMovie
        self.pause.grid(row=1, column=2, padx=2, pady=2)
        
        # Create Teardown button
        self.teardown = Button(self.main_frame, width=20, padx=3, pady=3)
        self.teardown["text"] = "Teardown"
        self.teardown["command"] = self.exitClient
        self.teardown.grid(row=1, column=3, padx=2, pady=2)
        
        # Create a label to display the movie
        self.label = Label(self.main_frame, height=19)
        self.label.grid(row=0, column=0, columnspan=4, sticky=W+E+N+S, padx=5, pady=5) 
    
    def change_color(self):
        """Change the background color of the main frame randomly."""
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        color = f'#{r:02x}{g:02x}{b:02x}'  # Convert to hex format
        self.main_frame.config(bg=color)  # Change the background color
        self.master.after(500, self.change_color)  # Change color every 500 ms

    def setupMovie(self):
        """Setup button handler."""
        print("Not implemented...")
    
    def exitClient(self):
        """Teardown button handler."""
        self.master.destroy()  # Close the GUI window
        os.remove(CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT)  # Delete the cache image from video

    def pauseMovie(self):
        """Pause button handler."""
        print("Not implemented...")
    
    def playMovie(self):
        """Play button handler."""
        # Create a new thread to listen for RTP packets
        threading.Thread(target=self.listenRtp).start()
        self.playEvent = threading.Event()
        self.playEvent.clear()
    
    def listenRtp(self):        
        """Listen for RTP packets."""
        while True:
            try:
                data = self.rtpSocket.recv(20480)
                if data:
                    rtpPacket = RtpPacket()
                    rtpPacket.decode(data)
                    
                    currFrameNbr = rtpPacket.seqNum()
                    print("Current Seq Num: " + str(currFrameNbr))
                                        
                    if currFrameNbr > self.frameNbr:  # Discard the late packet
                        self.frameNbr = currFrameNbr
                        self.updateMovie(self.writeFrame(rtpPacket.getPayload()))
            except:
                # Stop listening upon requesting PAUSE or TEARDOWN
                if self.playEvent.isSet(): 
                    break
                
                self.rtpSocket.shutdown(socket.SHUT_RDWR)
                self.rtpSocket.close()
                break
                
    def writeFrame(self, data):
        """Write the received frame to a temp image file. Return the image file."""
        cachename = CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT
        with open(cachename, "wb") as file:
            file.write(data)
        
        return cachename
    
    def updateMovie(self, imageFile):
        """Update the image file as video frame in the GUI."""
        photo = ImageTk.PhotoImage(Image.open(imageFile))
        self.label.configure(image=photo, height=288) 
        self.label.image = photo
        
    def openRtpPort(self):
        """Open RTP socket bound to a specified port."""
        # Create a new datagram socket to receive RTP packets from the server
        self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Set the timeout value of the socket to 0.5sec
        self.rtpSocket.settimeout(0.5)
        
        try:
            # Bind the socket to the address using the RTP port
            self.rtpSocket.bind((self.addr, self.port))
            print('\nBind \n')
        except:
            tkMessageBox.showwarning('Unable to Bind', 'Unable to bind PORT=%d' % self.port)

    def handler(self):
        """Handler on explicitly closing the GUI window."""
        self.pauseMovie()
        if tkMessageBox.askokcancel("Quit?", "Are you sure you want to quit?"):
            self.exitClient()
        else:  # When the user presses cancel, resume playing.
            self.playMovie()

if __name__ == "__main__":
    root = Tk()
    app = ClienteGUI(root, '127.0.0.1', 25000)
    root.mainloop()
