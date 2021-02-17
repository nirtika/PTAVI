#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Clase (y programa principal) para un servidor de eco en UDP simple."""
import hashlib
import secrets
import json
import socket
import socketserver
import sys
import time
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

from uaclient import write_log, log_startorend


class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    """Register server class."""

    dicc = {}
    dicc_users = {}
    user_digestdata = {}
    dicc_passwd = {}

    def handle(self):
        """Echo server class."""
        client_ip = self.client_address[0]
        client_port = self.client_address[1]
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente

            line = self.rfile.read()
            message_req = line.decode('utf-8')
            message_rec = message_req.split(' ')
            write_log(path_log, 'Received from ', client_ip,
                      str(client_port), message_req)
            print(message_req)
            if message_req != '':
                METHOD = message_rec[0]

                if 'SIP/2.0' not in message_req:
                    message = "SIP/2.0 400 Bad Request\r\n\r\n"
                    self.wfile.write(bytes(message, 'utf-8'))
                    write_log(path_log, 'Received from ', client_ip,
                              str(client_port), message)
                if METHOD == 'REGISTER':
                    username = message_rec[1].split(':')[1]
                    port = message_rec[1].split(':')[-1]
                    exp_time = message_rec[3]
                    tiempo_cad = (time.time() + int(exp_time))
                    tiempo_exp = time.strftime(
                        '%Y-%m-%d %H:%M:%S',
                        time.localtime(tiempo_cad))
                    tiempo_act = time.strftime('%Y-%m-%d %H:%M:%S',
                                               time.localtime())
                    if username not in self.dicc_users:
                        if len(message_req.split('\r\n')) == 3:
                            message = "SIP/2.0 401 Unauthorized\r\n" \
                                      "WWW-Authenticate: Digest nonce="
                            nonce = secrets.token_hex().upper()
                            self.user_digestdata[username] = nonce
                            message += '"' + nonce + '"' + "\r\n\r\n"
                            write_log(path_log, 'Sent to ',
                                      client_ip,
                                      self.client_address[1], message)
                            self.wfile.write(bytes(message, 'utf-8'))
                        else:
                            digest_response = message_req.split('"')[1]
                            self.read_passwd()
                            password = self.dicc_passwd[username]
                            nonce = self.user_digestdata[username]
                            d_response = hashlib.sha1()
                            d_response.update(bytes(nonce, 'utf-8'))
                            d_response.update(bytes(password, 'utf-8'))
                            d_response.digest()
                            proxy_response = d_response.hexdigest().upper()
                            if digest_response == proxy_response:
                                self.dicc['Address'] = client_ip
                                self.dicc['Port'] = port
                                self.dicc['Register'] = tiempo_act
                                self.dicc['Expires'] = tiempo_exp
                                self.dicc_users[username] = self.dicc
                                self.register2json()
                                message = "SIP/2.0 200 OK\r\n\r\n"
                                write_log(path_log, 'Sent to ',
                                          client_ip,
                                          port, message)
                                self.wfile.write(bytes(message, 'utf-8'))
                    else:
                        if int(message_rec[3]) == 0 \
                                or tiempo_act >= tiempo_exp:
                            del self.dicc_users[username]
                            self.register2json()
                            message = "SIP/2.0 200 OK\r\n\r\n"
                            write_log(path_log, 'Sent to ',
                                      client_ip,
                                      port, message)
                            self.wfile.write(bytes(message, 'utf-8'))
                        else:
                            self.register2json()
                            message = "SIP/2.0 200 OK\r\n\r\n"
                            write_log(path_log, 'Sent to ',
                                      client_ip,
                                      port, message)
                            self.wfile.write(bytes(message, 'utf-8'))

                elif METHOD == 'INVITE' or METHOD == 'ACK' or METHOD == 'BYE':
                    user_data = message_rec[1].split(':')[1]
                    if user_data not in self.dicc_users:
                        message = "SIP/2.0 404 User Not Found\r\n\r\n"
                        write_log(path_log, 'Sent to ', client_ip,
                                  client_port, message)
                        self.wfile.write(bytes(message, 'utf-8'))
                    else:
                        ip_user = self.dicc_users[user_data]['Address']
                        user_port = int(self.dicc_users[user_data]['Port'])
                        try:
                            with socket.socket(socket.AF_INET,
                                               socket.SOCK_DGRAM) as my_socket:
                                my_socket.setsockopt(
                                    socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                                my_socket.connect((ip_user, user_port))
                                write_log(path_log, 'Sent to ', ip_user,
                                          str(user_port), message_req)
                                my_socket.send(bytes(message_req, 'utf-8'))
                                data = my_socket.recv(1024)
                                self.wfile.write(data)
                                write_log(path_log, 'Received from ', ip_user,
                                          str(user_port), data.decode('utf-8'))
                                write_log(path_log, 'Sent to ',
                                          client_ip,
                                          client_port,
                                          data.decode('utf-8'))
                        except ConnectionRefusedError:
                            message = "Error: No server listening at " \
                                      + ip_user + " port " + str(user_port)
                            self.wfile.write(bytes(message, 'utf-8'))
                            write_log(path_log, 'Sent to ',
                                      client_ip,
                                      client_port,
                                      message)

            if not line:
                break

    def register2json(self):
        """Guardar usuarios en json."""
        with open(path_users, "w") as outfile_user:
            json.dump(self.dicc_users, outfile_user, indent=2)

    def read_passwd(self):
        """"Lee las contraseñas del fichero json."""
        with open(path_password, "r") as passwdfile:
            self.dicc_passwd = json.load(passwdfile)

    def json2registered(self):
        """"guardar en json."""
        try:
            with open(path_users, 'r')as json_file:
                self.dicc = json.load(json_file)
        except FileNotFoundError:
            print("File not found")


class ProxyHandler(ContentHandler):
    """"Proxy handler."""

    def __init__(self):
        """"Constructor. Inicializamos las variables."""
        self.dicc = {}

    def startElement(self, name, attrs):
        """"leer datos del xml y guardarlos."""
        if name == 'server':
            self.dicc["server_name"] = attrs.get('name', "")
            self.dicc["server_ip"] = attrs.get('ip', "")
            if self.dicc["server_ip"] == "":
                self.dicc["server_ip"] = '127.0.0.1'
            self.dicc["server_port"] = attrs.get('puerto', "")
        elif name == 'database':
            self.dicc["path_users"] = attrs.get('path', "")
            self.dicc["path_password"] = attrs.get('passwdpath', "")
        elif name == 'log':
            self.dicc["path_log"] = attrs.get('path', "")


if __name__ == "__main__":

    if len(sys.argv) != 2:
        sys.exit('Usage: python proxy_registrar.py config')

    parser = make_parser()
    pHandler = ProxyHandler()
    parser.setContentHandler(pHandler)
    parser.parse(open(sys.argv[1]))

    try:
        server_name = pHandler.dicc["server_name"]
        server_ip = pHandler.dicc["server_ip"]
        server_port = int(pHandler.dicc["server_port"])
        path_users = pHandler.dicc["path_users"]
        path_password = pHandler.dicc["path_password"]
        path_log = pHandler.dicc["path_log"]
    except IndexError:
        sys.exit('Usage: python uaclient.py config method option')

    serv = socketserver.UDPServer((server_ip, server_port), SIPRegisterHandler)

    print("Server " + server_name +
          " listening at port " + str(server_port) + "...")
    log_startorend(path_log, 'Start')
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        log_startorend(path_log, 'End')
        print("Finalizado servidor")
