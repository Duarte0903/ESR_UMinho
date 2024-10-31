import socket
import sys
import threading
import time

class Node:
    def __init__(self, endereco="10.0.10.10"):
        self.neighbours = []
        self.interface_status = {}
        self.monitoring_rec = {}
        self.server_address = endereco
        self.incoming_server = "-1"
        self.PACKET_TTL = -1
        self.lock = threading.Lock()

    # Função de inicialização da estrutura das interfaces
    def init_status(self):
        with self.lock:
            for n in self.neighbours:
                self.interface_status[n] = 0  # inicializar todas as interfaces como inativas

    def make_probe(self, server_id, timeStamp, n_steps, probe_round):
        packet : bytes
        message = ""
        message = f'{server_id};{timeStamp};{n_steps};{probe_round}'
        print(message)
        return message.encode('utf-8')

    # Função que tem como objetivo descobrir qual o delay mínimo entre todos os servidores presentes na estrutura de monitorização "monitoring_rec"
    def min_delay(self):
        min_server = ('', 10000)

        with self.lock:
            for id in self.monitoring_rec:
                delay = self.monitoring_rec[id]['delay']
                if delay < min_server[1]:
                    min_server = (id, delay)

        if self.incoming_server != min_server[0]:
            self.incoming_server = min_server[0]
            return True
        else:
            return False

    # Função que tem como objetivo efetuar um novo pedido de stream ao próximo salto em direção ao novo servidor na situação em que o servidor ótimo deixa de ser o servidor de quem o nodo está a receber a stream para o servidor alternativo a esse
    def request_new_server(self):
        with self.lock:
            for id in self.monitoring_rec:  # desativar todas as interfaces que levam a servidores
                ip = self.monitoring_rec[id]['ip']
                self.interface_status[ip] = 0

            next_step = self.monitoring_rec[self.incoming_server]['ip']  # ver qual é o próximo passo para o incoming_server

            stream_flag = any(flag == 1 for flag in self.interface_status.values())

        if stream_flag:  # só faz um novo pedido se a stream alguma vez foi pedida
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto("movie.Mjpeg".encode('utf-8'), (next_step, 5000))

    # Função que tem como objetivo fazer o pedido da lista de vizinhos e do TTL dos pacotes de monitorização ao nodo 
    def get_neighbours(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        msg = "get_neighbours"
        s.sendto(msg.encode('utf-8'), (self.server_address, 2000))
        resposta, server_add = s.recvfrom(1024)

        self.PACKET_TTL = int(resposta.decode('utf-8').split(";")[1])
        print("PACKET_TTL =", self.PACKET_TTL)

        self.neighbours = resposta.decode('utf-8').split(";")[0].split(" ")

    # Função responsável por processar o pedido de um vídeo chegado de um nodo cliente ou de outro nodo intermédio
    def request_video_processing(self, s, msg, add):
        stream_flag = False

        with self.lock:
            stream_flag = any(flag == 1 for flag in self.interface_status.values())

            if not stream_flag:
                for server_id in self.monitoring_rec:
                    next_step = self.monitoring_rec[server_id]['ip']  # fazer o pedido ao servidor com menor delay
                    s.sendto(msg, (next_step, 5000))
                threading.Thread(target=self.difusion_service).start()

            print(f'JA TENHO O VIDEO ATIVEI A INTERFACE::: {add[0]}')
            self.interface_status[add[0]] = 1

    # Serviço que se encontra sempre disponível à espera de pacotes de pedido de vídeo vindos de clientes para a porta 5000
    def request_video_service(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        HOST = ''
        PORT = 5000
        s.bind((HOST, PORT))

        while True:
            msg, add = s.recvfrom(1024)
            print("\n\n\n Recebi:: \n\n\n", msg.decode('utf-8'))
            threading.Thread(target=self.request_video_processing, args=(s, msg, add)).start()

    # Função que tem como objetivo processar os pacotes de prova enviados pelo servidor para a rede.
    def probe_processing(self, s, msg, address):
        metrics = msg.decode('utf-8').split(";")
        id = metrics[0]
        port = 4000
        print("Recebi a mensagem ::", metrics)
        send_timeStamp = time.time()
        rcv_timeStamp = float(metrics[1])
        steps = int(metrics[2])
        probe_round = int(metrics[3])

        packet = self.make_probe(id, rcv_timeStamp, steps+1, probe_round) # fazer a nova probe

        for n in self.neighbours:
            if n != address[0] and steps < self.PACKET_TTL:
                s.sendto(packet, (n, port))

        incoming_delay = (send_timeStamp - rcv_timeStamp) * 1e3

        with self.lock:
            if id in self.monitoring_rec:
                server_monitoring = self.monitoring_rec[id]
                old_delay = server_monitoring['delay']
                alpha = 0.1
                delay = alpha * old_delay + (1 - alpha) * incoming_delay

                if self.monitoring_rec[id]['probe_round'] < probe_round:
                    self.monitoring_rec[id]['delay'] = delay
                    self.monitoring_rec[id]['steps'] = steps + 1
                    self.monitoring_rec[id]['ip'] = address[0]
                    self.monitoring_rec[id]['probe_round'] = probe_round
                    print(f"Server Record {id} Atualizado:: delay:{delay}, steps:{steps + 1}, ip:{address[0]}")
            else:
                self.monitoring_rec[id] = {
                    'delay': incoming_delay,
                    'steps': steps + 1,
                    'probe_round': probe_round,
                    'ip': address[0]
                }
                print(f"Server Record {id} Criado:: delay:{incoming_delay}, steps:{steps + 1}, ip:{address[0]}")

        changed = self.min_delay()  # atualizar qual é o servidor com menor delay neste momento

        if changed:
            self.request_new_server()

    # Serviço que está sempre em execução à escuta de pacotes de monitorização na porta 4000. Estes pacotes quando são recebidos são encaminhados para uma thread que é criada com o propósito de processar o pacote
    def probe_service(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        HOST = ''
        PORT = 4000
        s.bind((HOST, PORT))
        print(f"A receber probes no: {HOST}:{PORT}")

        while True:
            msg, address = s.recvfrom(1024)
            print("recebi probe:", msg)
            threading.Thread(target=self.probe_processing, args=(s, msg, address)).start()

    # Função que permite fazer o reenvio do vídeo para os vizinhos cujas interfaces estejam ativas
    def difusion_processing(self, s, msg, add):  # controlled flooding
        incoming_ip = add[0]
        print(f"Received video from {incoming_ip}")
        
        with self.lock:
            for id in self.monitoring_rec:
                print(f"Checking monitoring record for {id}: {self.monitoring_rec[id]}")
            
            if incoming_ip == self.monitoring_rec[self.incoming_server]['ip']:
                print(f'Sending video to active interfaces from: {incoming_ip}')
                for ip, status in self.interface_status.items():
                    if ip != incoming_ip and status:
                        print(f"Sending video to: {ip}")  
                        try:
                            s.sendto(msg, (ip, 6000))
                            print(f"Video sent to {ip} successfully.")
                        except Exception as e:
                            print(f"Failed to send video to {ip}: {e}")
            else:
                print(f"Incoming video not from the optimal server ({self.incoming_server}), ignoring.")



    # Serviço que se encontra sempre disponível na porta 6000 que trata dos pacotes de vídeo vindos de um servidor
    def difusion_service(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        HOST = ''
        PORT = 6000
        s.bind((HOST, PORT))

        print(f"A receiving video on: {HOST}:{PORT}")

        while True:
            msg, add = s.recvfrom(20480)
            print(f"Received video from {add[0]}")  # Log the incoming video source
            threading.Thread(target=self.difusion_processing, args=(s, msg, add)).start()


    def main(self):
        self.get_neighbours()
        self.init_status()
        print(self.neighbours)
        threading.Thread(target=self.request_video_service).start()
        threading.Thread(target=self.probe_service).start()

if __name__ == "__main__":
    node = Node()
    node.main()