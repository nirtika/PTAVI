#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Programa cliente que abre un socket a un servidor."""
import hashlib
import random
import secrets
import socket
import sys
import time
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
import simplertp


class ClientHandler(ContentHandler):
    """class clienthandler."""

    dicc_datos = {}

    def __init__(self):
        """Constructor. Inicializamos las variables."""

    def startElement(self, name, attrs):
        """Guardar variables."""
        if name == 'account':
            self.dicc_datos["username"] = attrs.get('username', "")
            self.dicc_datos["passwd"] = attrs.get('passwd', "")
        elif name == 'uaserver':
            self.dicc_datos["server_ip"] = attrs.get('ip', "")
            if self.dicc_datos["server_ip"] == "":
                self.dicc_datos["server_ip"] = '127.0.0.1'
            self.dicc_datos["server_port"] = attrs.get('puerto', "")
        elif name == 'rtpaudio':
            self.dicc_datos["audio_port"] = attrs.get('puerto', "")
        elif name == 'regproxy':
            self.dicc_datos["proxy_ip"] = attrs.get('ip', "")
            self.dicc_datos["proxy_port"] = attrs.get('puerto', "")
        elif name == 'log':
            self.dicc_datos["path_log"] = attrs.get('path', "")
        elif name == 'audio':
            self.dicc_datos["audio_path"] = attrs.get('path', "")


def send_audio(ip, port):
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
    simplertp.send_rtp_packet(RTP_header, audio, ip, port)


def write_log(log_path, mensaje, ip, port, out_message):
    """escribir fichero log."""
    message_log = '\r\n' + time.strftime('%Y%m%d%H%M%S',
                                         time.localtime(time.time())) + " " \
                  + mensaje + ip + ":" + \
                  str(port) + " " + out_message.replace('\r\n', ' ')
    with open(log_path, "a") as outfile:
        outfile.write(message_log)


def log_startorend(log_path, state):
    """escribir log start o end."""
    message2_log = ''
    if state == 'Start':
        message2_log = '\r\n' + time.strftime('%Y%m%d%H%M%S',
                                              time.localtime(time.time())) \
                       + " " + 'Starting...' + "\r\n"
    elif state == 'End':
        message2_log = '\r\n' + time.strftime('%Y%m%d%H%M%S',
                                              time.localtime(time.time())) \
                       + " " + 'Ending...' + "\r\n"
    with open(log_path, "a") as outfile:
        outfile.write(message2_log + "\r\n")


if __name__ == "__main__":
    try:
        METHOD = sys.argv[2]
        option = sys.argv[3]
    except IndexError:
        sys.exit('Usage: python3 uaclient.py config metodo opcion')

    if len(sys.argv) != 4:
        sys.exit('Usage: python3 uaclient.py config metodo opcion')

    parser = make_parser()
    cHandler = ClientHandler()
    parser.setContentHandler(cHandler)
    parser.parse(open(sys.argv[1]))

    try:
        proxy_ip = cHandler.dicc_datos["proxy_ip"]
        proxy_port = int(cHandler.dicc_datos["proxy_port"])
        username = cHandler.dicc_datos["username"]
        password = cHandler.dicc_datos["passwd"]
        audio_port = cHandler.dicc_datos["audio_port"]
        log_path = cHandler.dicc_datos["path_log"]
        audio_path = cHandler.dicc_datos["audio_path"]

    except IndexError:
        sys.exit('Usage: python uaclient.py config METHOD option')

    if METHOD == 'REGISTER':
        LINE = METHOD + ' sip:' + username + ' SIP/2.0\r\n' \
               + 'Expires: ' + option + '\r\n'
    elif METHOD == "INVITE":
        contents_sdp = ('v=0\r\n'
                        + 'o=' + username + ' ' + proxy_ip + '\r\n'
                        + 's=misesion\r\n'
                        + 't=0\r\n'
                        + 'm=audio ' + audio_port + ' RTP')
        content_length = str(len(bytes(contents_sdp, 'utf-8')))
        cabecera_proxy = 'VIA:SIP/2.0 ' + str(proxy_ip) + ':' + str(proxy_port)
        LINE = METHOD + ' sip:' + option + ' SIP/2.0\r\n' \
            + 'Content-Type: application/sdp\r\n' \
            + 'Content-Length: ' \
            + content_length + '\r\n' + cabecera_proxy + '\r\n\r\n' \
            + contents_sdp + '\r\n'
    elif METHOD == "BYE":
        LINE = METHOD + ' sip:' + option + ' SIP/2.0\r\n'
    else:
        sys.exit('Error: method BYE, INVITE or REGISTER')

    # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
        try:
            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            my_socket.connect((proxy_ip, proxy_port))
            print("Enviando: " + LINE)
            my_socket.send(bytes(LINE, 'utf-8') + b'\r')
            data = my_socket.recv(1024)
            message = data.decode('utf-8')
            print('Recibido -- ', message)
            write_log(log_path, "Sent to ", proxy_ip, proxy_port, LINE)
            write_log(log_path, "Received from ",
                      proxy_ip, proxy_port, message)
            data_received = message.split('\r\n')
            if message.startswith('SIP/2.0 401 Unauthorized\r\n'):
                LINE = METHOD + ' sip:' + username \
                       + ' SIP/2.0\r\n' + 'Expires: ' + option
                nonce = message.split('"')[1]
                digest_rep = hashlib.sha1()
                digest_rep.update(bytes(nonce, 'utf-8'))
                digest_rep.update(bytes(password, 'utf-8'))
                digest_rep.digest()
                digest_response = digest_rep.hexdigest().upper()
                LINE += " Authorization: Digest response=" \
                        + '"' + digest_response + '"\r\n'
                print("Enviando: " + LINE)
                write_log(log_path, "Sent to ", proxy_ip, proxy_port, LINE)
                my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
                data = my_socket.recv(1024)
                message = data.decode('utf-8')
                print('Recibido -- ', message)
                write_log(log_path, "Received from ",
                          proxy_ip, proxy_port, message)

            if message.startswith('SIP/2.0 100 Trying\r\n\r\n'
                                  + 'SIP/2.0 180 Ringing\r\n\r\n'
                                  + 'SIP/2.0 200 OK\r\n'):
                LINE = 'ACK' + ' sip:' + option + ' SIP/2.0'
                my_socket.send(bytes(LINE, 'utf-8'))
                print("Enviando: " + LINE)
                write_log(log_path, "Sent to ", proxy_ip, proxy_port, LINE)
                user_data = data_received[11].split(' ')[1]
                rtp_audio = int(data_received[14].split(' ')[1])
                send_audio(user_data, rtp_audio)
                write_log(log_path, "Sending audio to ",
                          user_data, rtp_audio, audio_path)

        except KeyboardInterrupt:
            sys.exit("Finalizando cliente")

        except ConnectionRefusedError:
            write_log(log_path, "Error: No server listening at ",
                      proxy_ip, proxy_port, '')
            sys.exit(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                     + ' Error: No server listening at '
                     + proxy_ip + ' port ' + str(proxy_port))

        print("Terminando socket...")
        log_startorend(log_path, 'End')
    print("Fin.")
