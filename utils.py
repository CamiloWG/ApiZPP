from datetime import datetime


def calcular_minutos(entrada, salida):
    """Calcula la diferencia en minutos entre dos timestamps"""
    diff = salida - entrada
    return int(diff.total_seconds() / 60)
