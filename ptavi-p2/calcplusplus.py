#!/usr/bin/python3
# -*- coding: utf-8 -*-

import csv
import sys
from calcoohija import CalculadoraHija

if __name__ == "__main__":

    if len(sys.argv) != 2:
        sys.exit("Error: calcplusplus.py <fichero>")

    with open(sys.argv[1]) as lista:

        fichero = csv.reader(lista, delimiter=",")

        for lines in fichero:
            # print(lines)
            # quitar espacios vacios de medio (4,5,,5) y la ultima comma (4,1,)
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

            print(operador, ":", resultado)
