from datetime import datetime


def calcular_minutos(entrada, salida):
    diff = salida - entrada
    return int(diff.total_seconds() / 60)
