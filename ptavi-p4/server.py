#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""
import json
import socketserver
import sys
import time


class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """
    dicc_datos = {}
    dicc_user = {}

    def handle(self):
        """
        handle method of the server class
        (all requests will be handled by this method)
        """
        self.json2registered()
        for line in self.rfile:
            mensaje = line.decode('utf-8')

            if mensaje != '\r\n':
                message = mensaje[0:-2].split(' ')
                usuario = message[1].split(':')

                if message[0] != "REGISTER" and message[0] != "Expires:":
                    print('Error404: REGISTER not found')

                if message[0] == "Expires:":
                    tiempo_cad = (time.time() + int(message[1]))
                    tiempo_exp = time.strftime('%Y-%m-%d %H:%M:%S',
                                               time.localtime(tiempo_cad))
                    tiempo_act = time.strftime('%Y-%m-%d %H:%M:%S',
                                               time.localtime())
                    if int(message[1]) == 0 or tiempo_act >= tiempo_exp:
                        del self.dicc_user[user]
                        self.register2json()
                    else:
                        # print(tiempo_exp)
                        self.dicc_datos['Address'] = self.client_address[0]
                        self.dicc_datos['Expires'] = tiempo_exp
                        # self.dicc_datos = {'Address': self.client_address[0],
                        # 'Expires: ': tiempo_exp}
                        self.dicc_user[user] = self.dicc_datos
                        self.register2json()

                user = usuario[-1]
                print(message[0], message[1])

        print(self.dicc_user)
        self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")

    def register2json(self):
        with open("registered.json", "w") as fichero:
            json.dump(self.dicc_user, fichero, indent=2)

    def json2registered(self):
        try:
            with open("registered.json", 'r')as json_file:
                self.dicc_user = json.load(json_file)
        except FileNotFoundError:
            print("File not found")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python3 server.py puerto")
    Port = int(sys.argv[1])
    # Listens at localhost ('') port 6001
    # and calls the SIPRegisterHandler class to manage the request
    serv = socketserver.UDPServer(('', Port), SIPRegisterHandler)

    print("Lanzando servidor UDP de eco...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado servidor")
