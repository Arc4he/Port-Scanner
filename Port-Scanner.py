#!/usr/bin/env python3

import socket
import argparse
from concurrent.futures import ThreadPoolExecutor
import signal # Keyboard signal
import sys
from termcolor import colored


open_sockets = []

def def_handler(sg, frame):
    print(colored(f"[!] Leaving the program ...", 'red'))

    for socket in open_sockets:
        socket.close()
    sys.exit(1)

signal.signal(signal.SIGINT, def_handler) # Ctrl+C


# For aguments of the Script
# Help 
def get_arguments():
    parser = argparse.ArgumentParser(description='Fast TCP Port Scanner')
    parser.add_argument("-t", "--target", dest="target", required=True, help="Victim target to Scann (Ex: -t 192.138.1.1)")
    parser.add_argument("-p", "--port", dest="port", required=True, help="Port range to Scann (Ex: -p 1-100, -p 22,80, -p 21)")
    options = parser.parse_args()

    return options.target, options.port
# Socket 
def create_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1) # No more tha 1 s
    
    open_sockets.append(s)

    return s

# Scanner function
def port_scanner(port, host):
    
    s = create_socket()

    try:
        s.connect((host, port))
        s.sendall(b"HEAD / HTTP/1.0\r\n\r\n") # Header
        response = s.recv(1024)
        response = response.decode(errors='ignore').split('\n')
        if response:
            print(colored(f"\n[+] {port} - OPEN\n", 'green'))
            
            # Header
            for line in response:
                print(colored(f"\t{line}", 'white'))

        else:
            print(colored(f"\n[+] {port} - OPEN\n", 'green'))
        
    except (socket.timeout, ConnectionRefusedError): 
        pass
     
    finally:
        s.close()

def scan_ports(ports, target,):

    with ThreadPoolExecutor(max_workers=100) as executor:
        executor.map(lambda port: port_scanner(port, target), ports)

# Str
def parse_ports(ports_str):
    
    if '-' in ports_str:
       start, end = map(int, ports_str.split('-')) # typecast
       return range(start, end+1) 
    elif ',' in ports_str:
        return map(int, ports_str.split(','))
    else:
        return (int(ports_str),)

# Main
def main():
    target, ports_str = get_arguments()
    ports = parse_ports(ports_str)
    scan_ports(ports, target)

if __name__ == '__main__':
    main()
