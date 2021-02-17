#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Clase (y programa principal) para un servidor de eco en UDP simple."""
import random
import secrets
import socket
import socketserver
import sys
import simplertp
from uaclient import ClientHandler, write_log, log_startorend
from xml.sax import make_parser


def send_audio_server(datos_ip, datos_port):
    """enviar audio."""
    aleat = random.randint(0, 100000)
    BIT = secrets.randbits(1)
    setcsrc = []
    aleat_csrc = random.randint(0, 15)
    for i in range(aleat_csrc):
        setcsrc.append(aleat_csrc)
    RTP_header = simplertp.RtpHeader()
    RTP_header.setCSRC(setcsrc)
    RTP_header.set_header(pad_flag=0, ext_flag=0,
                          cc=len(setcsrc), marker=BIT, ssrc=aleat)
    audio = simplertp.RtpPayloadMp3(audio_path)
    simplertp.send_rtp_packet(RTP_header, audio, datos_ip, datos_port)


class EchoHandler(socketserver.DatagramRequestHandler):
    """Echo server class."""

    dicc = {}

    def handle(self):
        """Echo handle."""
        global datos_m_port, datos_o_ip
        client_ip = self.client_address[0]
        client_port = self.client_address[1]
        while 1:
            line = self.rfile.read()
            message_client = line.decode('utf-8')
            data_received = message_client.split('\r\n')
            print(message_client)
            if message_client != '':
                METHOD = message_client.split(' ')[0]
                if METHOD == 'INVITE':
                    user = username.split(':')[0]
                    content_sdp = (
                            'v=0\r\n' + 'o=' + user + ' ' + server_ip
                            + '\r\n' + 's=misesion\r\n'
                            + 't=0\r\n' + 'm=audio ' +
                            str(audio_port) + ' RTP')
                    length_sdp = str(len(bytes(content_sdp, 'utf-8')))
                    cabecera_proxy = 'VIA:SIP/2.0 ' + \
                                     str(proxy_ip) + ':' + str(proxy_port)
                    message = ("SIP/2.0 100 Trying\r\n\r\n"
                               + "SIP/2.0 180 Ringing\r\n\r\n"
                               + "SIP/2.0 200 OK\r\n"
                               + "Content-Type: application/content_sdp\r\n"
                               + "Content-Length: " + length_sdp + "\r\n\r\n"
                               + cabecera_proxy + "\r\n\r\n"
                               + content_sdp + "\r\n\r\n")
                    self.wfile.write(bytes(message, 'utf-8'))
                    datos_o_ip = data_received[6].split(' ')[1]
                    datos_m_port = data_received[9].split(' ')[1]
                    write_log(path_log, "Received from ",
                              datos_o_ip, datos_m_port, message_client)
                    write_log(path_log, "Sent to ",
                              datos_o_ip, datos_m_port, message)
                elif METHOD == 'ACK':
                    print("Sending audio...")
                    send_audio_server(datos_o_ip, int(datos_m_port))
                    write_log(path_log, "Received from ",
                              datos_o_ip, datos_m_port,
                              message_client)
                    write_log(path_log, "Sending audio to ", datos_o_ip,
                              datos_m_port, audio_path)
                    print("Audio send complete.")
                elif METHOD == 'BYE':
                    message = "SIP/2.0 200 OK\r\n\r\n"
                    self.wfile.write(bytes(message, 'utf-8'))
                    write_log(path_log, "Received from ",
                              client_ip, client_port,
                              message_client)
                    write_log(path_log, "Sent to ",
                              client_ip,
                              client_port, message)
                else:
                    message = "SIP/2.0 405 Method Not Allowed\r\n\r\n"
                    self.wfile.write(bytes(message, 'utf-8'))
                    write_log(path_log, "Received from ",
                              client_ip,
                              client_port, message_client)
                    write_log(path_log, "Sent to ", client_ip,
                              client_port, message)

            if not line:
                break


if __name__ == "__main__":

    if len(sys.argv) != 2:
        sys.exit('Usage: python3 server.py IP port audio_file')

    parser = make_parser()
    sHandler = ClientHandler()
    parser.setContentHandler(sHandler)
    parser.parse(open(sys.argv[1]))

    try:
        server_ip = sHandler.dicc_datos["server_ip"]
        server_port = int(sHandler.dicc_datos["server_port"])
        username = sHandler.dicc_datos["username"]
        audio_port = int(sHandler.dicc_datos["audio_port"])
        audio_path = sHandler.dicc_datos["audio_path"]
        path_log = sHandler.dicc_datos["path_log"]
        proxy_ip = sHandler.dicc_datos["proxy_ip"]
        proxy_port = int(sHandler.dicc_datos["proxy_port"])
    except IndexError:
        sys.exit('Usage: python uaclient.py config method option')

    try:
        serv = socketserver.UDPServer((server_ip, server_port), EchoHandler)
    except (ValueError, IndexError, socket.gaierror):
        sys.exit('Usage: python3 server.py IP port audio_file')
    try:
        print("Listening...")
        log_startorend(path_log, 'Start')
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado servidor")
        log_startorend(path_log, 'End')
