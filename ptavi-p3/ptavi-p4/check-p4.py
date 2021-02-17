#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Script de comprobación de entrega de práctica

Para ejecutarlo, desde la shell:
 $ python3 check-p4.py login_gitlab

"""

import os
import random
import sys


if len(sys.argv) != 2:
    print()
    sys.exit("Usage : $ python3 check-p4.py login_gitlab")

REPO_GIT = "http://gitlab.etsit.urjc.es/" + sys.argv[1] + "/ptavi-p4"

PYTHON_FILES = [
    'client.py',
    'server.py',
    ]

FILES = [
    'README.md',
    'LICENSE',
    '.gitignore',
    'check-p4.py',
    'register.libpcap',
    '.git'
    ]

aleatorio = str(int(random.random() * 1000000))

error = 0

print()
print("Clonando el repositorio " + REPO_GIT + "\n")
os.system('git clone ' + REPO_GIT + ' /tmp/' + aleatorio + ' > /dev/null 2>&1')
try:
    student_file_list = os.listdir('/tmp/' + aleatorio)
except OSError:
    error = 1
    print("Error: No se ha podido acceder al repositorio " + REPO_GIT + ".")
    print()
    sys.exit()

if len(student_file_list) != len(FILES) + len(PYTHON_FILES):
    error = 1
    print("Error: solamente hay que subir al repositorio los ficheros")
    print("indicados en las guion de practicas, que son en total")
    print(str(len(PYTHON_FILES) + len(FILES)) + " (incluyendo .git):")

for filename in FILES + PYTHON_FILES:
    if filename not in student_file_list:
        error = 1
        print("  Error: " + filename + " no encontrado.",
              "Tienes que subirlo al repositorio.")

if not error:
    print("Parece que la entrega se ha realizado bien.")
    print()
    print("La salida de pep8 es: (si todo va bien, no ha de mostrar nada)")
    print()
    files = ['/tmp/' + aleatorio + '/' + file for file in PYTHON_FILES]
    os.system('pep8 --repeat --show-source --statistics ' + ' '.join(files))
print()
