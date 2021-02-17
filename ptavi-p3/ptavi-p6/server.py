#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Clase (y programa principal) para un servidor de eco en UDP simple."""

import socketserver
import sys
import simplertp
import random


class EchoHandler(socketserver.DatagramRequestHandler):
    """Echo server class."""

    def handle(self):
        """Escribe dirección y puerto del cliente (de tupla client_address)."""
        # variable global
        global data_received
        print('El cliente nos manda: ', end='')
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            message_client = line.decode('utf-8')
            message = message_client.split()
            print(message_client)
            if message_client != '':
                method = message[0]
                if 'SIP/2.0' not in message or '@' not in message[1]:
                    self.wfile.write(b"SIP/2.0 400 Bad Request")
                if method == 'INVITE':
                    self.wfile.write(b"SIP/2.0 100 Trying\r\n\r\n" +
                                     b"SIP/2.0 180 Ringing\r\n\r\n" +
                                     b"SIP/2.0 200 OK\r\n\r\n")
                    data_received = message_client.split('\r\n')
                elif method == 'ACK':
                    datos_m = data_received[7]
                    datos_o = data_received[4]
                    aleat = random.randint(0, 100000)
                    RTP_header = simplertp.RtpHeader()
                    RTP_header.set_header(pad_flag=0, ext_flag=0,
                                          cc=0, marker=0, ssrc=aleat)
                    audio = simplertp.RtpPayloadMp3(AUDIO_FILE)
                    port_dest = int(datos_m.split(' ')[1])
                    ip_dest = datos_o.split(' ')[-1]
                    simplertp.send_rtp_packet(RTP_header, audio,
                                              ip_dest, port_dest)
                elif method == 'BYE':
                    self.wfile.write(b"SIP/2.0 200 OK\r\n")
                else:
                    self.wfile.write(b"SIP/2.0 405 Method Not Allowed")

            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit('Usage: python3 server.py IP port audio_file')
    DIR_IP = sys.argv[1]
    PORT = int(sys.argv[2])
    AUDIO_FILE = sys.argv[3]

    # Creamos servidor de eco y escuchamos
    serv = socketserver.UDPServer((DIR_IP, PORT), EchoHandler)
    print("Listening...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado servidor")
