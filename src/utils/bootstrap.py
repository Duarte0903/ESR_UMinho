import socket
import json
import threading

config_file = "topologias/top3_config.json"

def get_neighbours(ip: str):
    try:
        with open(config_file) as f:
            config = json.load(f)
            response = config['nodes'].get(ip, []) # Se o IP não existir, devolve uma lista vazia
            print("Neighbours for IP", ip, ":", response)
            return response
    except FileNotFoundError:
        print(f"Config file {config_file} not found.")
        return []
    except json.JSONDecodeError:
        print("Error decoding JSON in the configuration file.")
        return []

def get_neighbours_server(id: str):
    with open(config_file) as f:
        config = json.load(f)
        return config['servers'].get(id, [])

def getHostname(ip: str):
    with open(config_file) as f:
        config = json.load(f)
        hosts = config["hostnames"]
        for host in hosts:
            if ip in hosts[host]:
                return host

    return None