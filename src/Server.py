import socket
import threading
import time
import json
import sys
from VideoStream import VideoStream
from RtpPacket import RtpPacket
from bootstrap import BootstrapService

class Server:
    def __init__(self, id: str, config_file: str = "../topologias/top2_config.json"):
        self.id = id
        self.config_file = config_file
        self.neighbours = []
        self.probe_round = 0
        self.video_streaming = True
        self.difusion_node = "10.0.0.10"
        self.clientInfo = {}
        self.bootstrap_server = BootstrapService(self.config_file)  # Servico de Bootstrap na porta 2000
        self.get_neighbours()

    def get_neighbours(self):
        with open(self.config_file) as f:
            config = json.load(f)
            self.neighbours = config['servers'].get(self.id, [])
            print("Server neighbours:", self.neighbours)

    def request_video_processing(self, s: socket.socket, msg: bytes, addr: tuple):
        print("Received a video processing request:", msg)
        filename = msg.decode('utf-8').split(";")[0]
        self.start_video_streaming(filename)

    def start_video_streaming(self, filename):
        self.clientInfo['videoStream'] = VideoStream(filename)
        self.clientInfo['rtpPort'] = 25000
        self.clientInfo['rtpAddr'] = socket.gethostbyname(self.difusion_node)
        print("Sending to Addr:", self.clientInfo['rtpAddr'], ":", self.clientInfo['rtpPort'])

        # Create a new socket for RTP/UDP
        self.clientInfo["rtpSocket"] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.clientInfo['event'] = threading.Event()
        self.clientInfo['worker'] = threading.Thread(target=self.send_rtp)
        self.clientInfo['worker'].start()

    def send_rtp(self):
        """Send RTP packets over UDP."""
        while True:
            self.clientInfo['event'].wait(0.05)
            if self.clientInfo['event'].isSet():
                break
            data = self.clientInfo['videoStream'].nextFrame()
            if data:
                frameNumber = self.clientInfo['videoStream'].frameNbr()
                try:
                    address = self.clientInfo['rtpAddr']
                    port = int(self.clientInfo['rtpPort'])
                    packet = self.make_rtp(data, frameNumber)
                    self.clientInfo['rtpSocket'].sendto(packet, (address, port))
                except Exception as e:
                    print("Connection Error:", e)
                    continue
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
        port = 5000
        s.bind(('', port))
        print(f"Listening on port: {port}")

        while True:
            msg, addr = s.recvfrom(1024)
            self.video_streaming = False
            threading.Thread(target=self.request_video_processing, args=(s, msg, addr)).start()

        s.close()

    def make_probe(self, server_id, timeStamp, n_steps, probe_round):
        packet: bytes
        message = f'{server_id};{timeStamp};{n_steps};{probe_round}'
        print(message)
        return message.encode('utf-8')

    def send_probe_service(self):
        port = 4000
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('', port))

        while True:
            packet = self.make_probe(self.id, time.time(), 0, self.probe_round)
            for neighbour in self.neighbours:
                print(f"Sending probes to: {neighbour}:{port}")
                s.sendto(packet, (neighbour, port))
            time.sleep(20)
            self.probe_round += 1

    def run(self):
        threading.Thread(target=self.bootstrap_server.start_service).start()  # Start the bootstrap server
        threading.Thread(target=self.request_video_service).start()
        threading.Thread(target=self.send_probe_service).start()

def main():
    if len(sys.argv) != 2:
        print("[Usage: python server.py <server_id>]")
        print("  <server_id>: Unique identifier for the server.")
        sys.exit(1)

    server_id = sys.argv[1]
    server = Server(server_id)
    server.run()

if __name__ == '__main__':
    main()
