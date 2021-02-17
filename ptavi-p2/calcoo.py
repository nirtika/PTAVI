#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys


class Calculadora:

    def __init__(self, operador, op1, op2):
        try:
            self.operador = operador
            self.op1 = op1
            self.op2 = op2
        except ValueError:
            sys.exit("Error: Non numerical parameters")

    def plus(self):
        return self.op1 + self.op2

    def minus(self):
        return self.op1 - self.op2

    def operar(self):
        if self.operador == "suma":
            return self.plus()
        elif self.operador == "resta":
            return self.minus()
        else:
            sys.exit('Operación sólo puede ser sumar o restar.')


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("Error: calcoo.py operando1 operador operador2")

    operador = sys.argv[2]
    try:
        operando1 = float(sys.argv[1])
        operando2 = float(sys.argv[3])
    except ValueError:
        sys.exit("Error: Non numerical parameters")

    calcular = Calculadora(operador, operando1, operando2)
    # print("Resultado de (",op1,operador,op2,"): ", calcular.operar())
    resultado = calcular.operar()
    print("Resultado de (", operando1, operador, operando2, "): ", resultado)
