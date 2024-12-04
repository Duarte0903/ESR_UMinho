import netifaces

def get_local_address():
    try:
        # Obter os endereços da interface especificada
        if "eth0" in netifaces.interfaces():
            addresses = netifaces.ifaddresses("eth0")
            
            # Verificar se a interface possui endereços IPv4
            if netifaces.AF_INET in addresses:
                ipv4_info = addresses[netifaces.AF_INET]
                
                # Retornar o endereço IP da interface
                if len(ipv4_info) > 0:
                    return ipv4_info[0]['addr']
    except Exception as e:
        print("Erro ao obter o IP da interface:", e)

    return None

def generate_metrics(delays):
    return sorted([(key, calc_metric(float(delay[0]), int(delay[1]))) for key, delay in delays.items()], key=lambda x: x[1])
         

def calc_metric(delay:float, jumps:int):
    # delay 0.7 jumps 0.3

    delay_normalized = delay/1 # Máximo de 1 segundo (eu sei que estou a dividir por 1)
    jumps_normalized = jumps/64

    delay_penalized = delay_normalized ** 2
    jumps_penalized = jumps_normalized ** 1.5

    return (0.7 * delay_penalized) + (0.3 * jumps_penalized)