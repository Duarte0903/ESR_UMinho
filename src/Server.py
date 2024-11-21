import socket
import threading
import time
import json
import sys
import os

from utils.VideoStream import VideoStream
from utils.RtpPacket import RtpPacket
from ServerWorker import ServerWorker
from ServerManager import ServerManager

import utils.ports as Portas

'''class Server:
    def __init__(self, server_id: str, config_file: str = "topologias/top3_config.json"):
        self.id = server_id
        self.config_file = config_file
        self.neighbours = []
        self.probe_round = 0
        self.difusion_node = "10.0.10.1"
        self.clientInfo = {}
        self.bootstrap_server = BootstrapService(self.config_file, Portas.BOOTSTRAP)  # porta 2000
        self.running = True
        self.lock = threading.Lock()
        self.filename = "movie.Mjpeg"  # Default video file for testing
        self.get_neighbours()

    def get_neighbours(self):
        with open(self.config_file) as f:
            config = json.load(f)
            self.neighbours = config['servers'].get(self.id, [])
            print("Server neighbours:", self.neighbours)

    def request_video_processing(self, s: socket.socket, msg: bytes, addr: tuple):
        # This method is now bypassed for testing purposes
        print("Video processing request bypassed. Starting streaming directly.")
        self.start_video_streaming(self.filename)

    def start_video_streaming(self, filename):
        with self.lock:  # Ensure thread safety
            self.clientInfo['videoStream'] = VideoStream(filename)
            self.clientInfo['rtpPort'] = 25000
            self.clientInfo['rtpAddr'] = socket.gethostbyname(self.difusion_node)
            print("Starting streaming to Addr:", self.clientInfo['rtpAddr'], ":", self.clientInfo['rtpPort'])

            # Create a new socket for RTP/UDP
            self.clientInfo["rtpSocket"] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.clientInfo['event'] = threading.Event()
            self.clientInfo['worker'] = threading.Thread(target=self.send_rtp)
            self.clientInfo['worker'].start()

    def send_rtp(self):
        """Send RTP packets over UDP."""
        while self.running:
            self.clientInfo['event'].wait(0.05)
            if self.clientInfo['event'].isSet():
                break

            try:
                with self.lock:  # Ensure thread safety
                    data = self.clientInfo['videoStream'].nextFrame()

                if data:
                    frameNumber = self.clientInfo['videoStream'].frameNbr()
                    address = self.clientInfo['rtpAddr']
                    port = int(self.clientInfo['rtpPort'])
                    packet = self.make_rtp(data, frameNumber)
                    self.clientInfo['rtpSocket'].sendto(packet, (address, port))
                else:
                    print("End of video stream reached. Restarting...")
                    # Restart the video stream
                    with self.lock:
                        self.clientInfo['videoStream'] = VideoStream(self.filename)  # Restart the video stream

            except Exception as e:
                print("Connection Error:", e)
                continue

        with self.lock:
            self.clientInfo['rtpSocket'].close()
        print("All done!")

    def make_rtp(self, payload, frameNbr):
        """RTP-packetize the video data."""
        version = 2
        padding = 0
        extension = 0
        cc = 0
        marker = 0
        pt = 26  # MJPEG type
        seqnum = frameNbr
        ssrc = 0

        rtpPacket = RtpPacket()
        rtpPacket.encode(version, padding, extension, cc, seqnum, marker, pt, ssrc, payload)
        print("Encoding RTP Packet:", seqnum)
        
        return rtpPacket.getPacket()

    def request_video_service(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        port = Portas.SERVER
        s.bind(('', port))
        print(f"Listening on port: {port}")

        while self.running:
            try:
                msg, addr = s.recvfrom(1024)
                threading.Thread(target=self.request_video_processing, args=(s, msg, addr)).start()
            except Exception as e:
                print(f"Error in receiving data: {e}")

        s.close()

    def make_probe(self):
        packet: bytes
        message = f'{self.id};{time.time()};0;{self.probe_round}'
        print(message)
        return message.encode('utf-8')

    def send_probe_service(self):
        port = 4000
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('', port))

        while self.running:
            packet = self.make_probe()
            for neighbour in self.neighbours:
                print(f"\033[93mSending probes to: {neighbour}:{port}\033[0m")
                s.sendto(packet, (neighbour, port))
            time.sleep(20)
            self.probe_round += 1

        s.close()

    def run(self):
        threading.Thread(target=self.bootstrap_server.start_service).start()
        threading.Thread(target=self.request_video_service).start()
        threading.Thread(target=self.send_probe_service).start()

    def stop(self):
        """Stop all services gracefully."""
        self.running = False
        with self.lock:
            if 'event' in self.clientInfo:
                self.clientInfo['event'].set()

def main():
    if len(sys.argv) != 2:
        print("[Usage: python3 server.py <server_id>]")
        print("  <server_id>: Unique identifier for the server.")
        sys.exit(1)

    server_id = sys.argv[1]
    server = Server(server_id)
    try:
        server.run()
        while True: 
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping server...")
        server.stop()'''

class Server:
    def __init__(self, server_id: str):
        self.id = server_id
        self.serverSocket = None

        self.manager = None

        self.status = 1

    def run(self):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind(('', Portas.SERVER))
        self.serverSocket.listen()

        self.manager = ServerManager(self.id)
        
        while self.status == 1:
            clientSocket, (addr, port) = self.serverSocket.accept()
            worker = ServerWorker(clientSocket, (addr, port), self.manager)
            threading.Thread(target=worker.run, args=()).start()

    def stop(self):
        self.status = 0
        self.serverSocket.close()
        print("Server closed")

def main():
    if len(sys.argv) != 2:
        print("[Usage: python3 server.py <server_id>]")
        print("  <server_id>: Unique identifier for the server.")
        sys.exit(1)

    server_id = sys.argv[1]
    server = Server(server_id)
    try:
        server.run()
        while True: 
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping server...")
        server.stop()

if __name__ == '__main__':
    main()
