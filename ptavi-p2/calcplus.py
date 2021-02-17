#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from calcoohija import CalculadoraHija

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Error: calcplus.py <fichero.txt>")

    # abrir y leer fichero
    fichero = open(sys.argv[1], "r")
    lista = fichero.readlines()

    for lineas in lista:
        # print(lineas)
        # quitar la ultima comma
        lines_list = lineas.rstrip("\n").rstrip(",")
        lines = lines_list.split(",")

        # quitar espacios vacios de medio (4,5,,5) si hay
        lines = list(filter(None, lines))

        operador = lines[0]
        operando1 = float(lines[1])
        operando2 = float(lines[2])

        print(",".join(lines[1:]), end=" ==> ")

        calcular = CalculadoraHija(operador, operando1, operando2)
        resultado = calcular.operar()

        for operandodos in lines[3:]:
            try:
                operando2 = float(operandodos)
                calcular = CalculadoraHija(operador, resultado, operando2)
                resultado = calcular.operar()
            except ValueError:
                sys.exit("Error: Non numerical parameters")

        print(operador, ": ", resultado)
        fichero.close()
