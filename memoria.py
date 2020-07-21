import math
import os

def lee_aceleracion():
    dato = _lee()[0]
    return int(dato*dato//4)

def lee_techo():
    return _lee()[1]*50

def lee_impacto():
    return _lee()[2] > 0

def escribe_aceleracion(aceleracion):
    dato = int(math.sqrt(aceleracion)*2)
    _escribe(0, dato)
    return dato

def escribe_techo(distancia):
    dato = distancia//50
    _escribe(1, dato)
    return dato

def escribe_impacto(impacto):
    dato = 0
    if impacto: dato = 1
    _escribe(2, dato)
    return dato

def _lee():
    datos = []
    leido = ""
    try:
        f = open('datos.txt')
        leido = f.read()
        f.close()
    except OSError:
        pass
    if len(leido) < 5:
        datos = [24,12,0]
    else:
        aux = leido.split(" ")
        for a in aux:
            datos.append(int(a))
    return datos

def _escribe(posicion, dato):
    datos = _lee()
    datos[posicion] = dato
    f = open('datos.txt', 'w')
    f.write(str(datos[0])+" "+str(datos[1])+" "+str(datos[2]))
    f.close()