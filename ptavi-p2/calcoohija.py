#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from calcoo import Calculadora


class CalculadoraHija(Calculadora):

    def multiply(self):
        return self.op1 * self.op2

    def divide(self):
        if self.op2 != 0:
            return self.op1 / self.op2
        else:
            sys.exit("Division by zero is not allowed")

    def operar(self):

        if self.operador == "suma":
            return self.plus()
        elif self.operador == "resta":
            return self.minus()
        elif self.operador == "multiplica":
            return self.multiply()
        elif self.operador == "divide":
            return self.divide()
        else:
            sys.exit('Operaciones: sumar, restar, multiplicar o dividir')


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("Error: calcoohija.py operando1 operador operador2")

    operador = sys.argv[2]
    try:
        operando1 = float(sys.argv[1])
        operando2 = float(sys.argv[3])
    except ValueError:
        sys.exit("Error: Non numerical parameters")

    calcular = CalculadoraHija(operador, operando1, operando2)
    resultado = calcular.operar()
    print("Resultado (", operando1, operador, operando2, "): ", resultado)
