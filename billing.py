from sqlalchemy.orm import Session
from models import Estadia, Factura
from utils import calcular_minutos
from datetime import datetime


def generar_factura(placa: str, db: Session):
    estadia = (
        db.query(Estadia)
        .filter(Estadia.placa == placa, Estadia.salida != None)
        .order_by(Estadia.id.desc())
        .first()
    )

    if not estadia:
        return None

    minutos = estadia.minutos_total
    tarifa = 80  # pesos por minuto

    total = minutos * tarifa

    factura = Factura(placa=placa, minutos=minutos, tarifa_minuto=tarifa, total=total)

    db.add(factura)
    db.commit()
    db.refresh(factura)

    return factura
