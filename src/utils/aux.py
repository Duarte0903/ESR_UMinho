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