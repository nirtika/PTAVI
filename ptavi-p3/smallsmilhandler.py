#!/usr/bin/python3
# -*- coding: utf-8 -*-


from xml.sax.handler import ContentHandler
from xml.sax import make_parser


class SmallSMILHandler(ContentHandler):

    def __init__(self):
        """ Constructor. Inicializamos las variables """

        # crear diccionarios para cada etiqeita
        self.dicc_root = {}
        self.dicc_region = {}
        self.dicc_img = {}
        self.dicc_audio = {}
        self.dicc_textstream = {}

        # crear lista vacia
        self.list = []

    def startElement(self, name, attrs):
        """ Método que se llama cuando se abre una etiqueta """

        if name == 'root-layout':
            # guardar los atributos en el diccionario
            self.dicc_root['etiqueta'] = name
            self.dicc_root['width'] = attrs.get('width', "")
            self.dicc_root['height'] = attrs.get('height', "")
            self.dicc_root['bg-color'] = attrs.get('background-color', "")

            self.list.append(self.dicc_root.copy())

        elif name == 'region':
            self.dicc_region['etiqueta'] = name
            self.dicc_region['id'] = attrs.get('id', "")
            self.dicc_region['top'] = attrs.get('top', "")
            self.dicc_region['bottom'] = attrs.get('bottom', "")
            self.dicc_region['right'] = attrs.get('right', "")
            self.dicc_region['left'] = attrs.get('left', "")

            self.list.append(self.dicc_region.copy())

        elif name == 'img':
            self.dicc_img['etiqueta'] = name
            self.dicc_img['src'] = attrs.get('src', "")
            self.dicc_img['region'] = attrs.get('region', "")
            self.dicc_img['begin'] = attrs.get('begin', "")
            self.dicc_img['dur'] = attrs.get('dur', "")

            self.list.append(self.dicc_img.copy())

        elif name == 'audio':
            self.dicc_audio['etiqueta'] = name
            self.dicc_audio['src'] = attrs.get('src', "")
            self.dicc_audio['begin'] = attrs.get('begin', "")
            self.dicc_audio['dur'] = attrs.get('dur', "")

            self.list.append(self.dicc_audio.copy())

        elif name == 'textstream':
            self.dicc_textstream['etiqueta'] = name
            self.dicc_textstream['src'] = attrs.get('src', "")
            self.dicc_textstream['region'] = attrs.get('region', "")

            self.list.append(self.dicc_textstream.copy())

    def get_tags(self):
        return self.list


if __name__ == "__main__":
    """Programa principal"""

    parser = make_parser()
    smilHandler = SmallSMILHandler()
    parser.setContentHandler(smilHandler)
    parser.parse(open('karaoke.smil'))
    print(smilHandler.get_tags())
