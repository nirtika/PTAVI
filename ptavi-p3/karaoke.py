#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from smallsmilhandler import SmallSMILHandler
import json
from urllib.request import urlretrieve


class KaraokeLocal(SmallSMILHandler):

    def __init__(self, read_file):
        parser = make_parser()
        smilHandler = SmallSMILHandler()
        parser.setContentHandler(smilHandler)
        parser.parse(open(read_file))
        self.fichero_smil = smilHandler.get_tags()

    def __str__(self):
        # Imprimr las etiqutas y atributos
        for etiquetas in self.fichero_smil:
            # crear una lista para atributos
            list_attrib = []
            for atribute, valor in etiquetas.items():
                # content_atrib = valor
                if valor != "":
                    # print(attribute, valor)
                    list_attrib += (atribute, '="', valor, '"', '\t')
            print(''.join(list_attrib))

    def to_json(self, file):
        # reemplazar .smil .json
        fichero_json = file.replace(".smil", ".json")
        with open(fichero_json, "w") as json_file:
            json.dump(self.fichero_smil, json_file, indent=4)

    def do_local(self):
        for etiquetas in self.fichero_smil:
            for atribute, valor in etiquetas.items():
                if atribute == 'src':
                    url = valor
                    if url.startswith('http://'):
                        nombre_archivo = url.split('/')
                        urlretrieve(url, nombre_archivo[-1])
                        etiquetas[atribute] = nombre_archivo[-1]
                        # print(etiquetas[atribute])


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python3 karaoke.py file.smil")

    read_file = sys.argv[1]

    karaoke = KaraokeLocal(read_file)
    karaoke.__str__()
    karaoke.to_json(read_file)
    karaoke.do_local()
    karaoke.to_json('local.json')
    karaoke.__str__()
