#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Programa cliente que abre un socket a un servidor."""

import socket
import sys

# Cliente UDP simple.

# Dirección IP del servidor.
datos_receptor = sys.argv[2].split('@')
dir_login = datos_receptor[-1]
SERVER = dir_login.split(':')[0]
PORT = int(dir_login.split(':')[-1])
RECEPTOR = datos_receptor[0]
METHOD = sys.argv[1]

# Contenido que vamos a enviar
if METHOD == 'INVITE':
    LINE = METHOD + ' sip:' + RECEPTOR + '@' + SERVER + ' SIP/2.0\r\n' \
           + 'Content-Type: application/sdp\r\n\r\n' \
           + 'v=0\r\n' + 'o=robin@gotham.com 127.0.0.1\r\n' + \
           's=misesion\r\n' + 't=0\r\n' + 'm=audio 34543 RTP\r\n'

else:
    LINE = METHOD + ' sip:' + RECEPTOR + '@' + SERVER + ' SIP/2.0'

if len(sys.argv) != 3:
    sys.exit('Usage: python3 client.py method receiver@IP:SIPport')
if METHOD != 'INVITE' and METHOD != 'BYE':
    sys.exit('Usage: python3 client.py method receiver@IP:SIPport')

# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((SERVER, PORT))
    print("Enviando: " + LINE)
    my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
    data = my_socket.recv(1024)
    message = data.decode('utf-8')
    print(data.decode('utf-8'))

    if message == ('SIP/2.0 100 Trying\r\n\r\n'
                   + 'SIP/2.0 180 Ringing\r\n\r\n'
                   + 'SIP/2.0 200 OK\r\n\r\n'):
        LINE = 'ACK' + ' sip:' + RECEPTOR + '@' + SERVER + ' SIP/2.0'
        print("Enviando: " + LINE)
        my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')

print("Terminando socket...")

print("Fin.")
