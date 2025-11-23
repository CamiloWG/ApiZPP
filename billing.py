from sqlalchemy.orm import Session
from models import Estadia, Factura


def generar_factura(placa: str, db: Session):
    """
    Genera una factura para la última estadía completada de un vehículo.
    
    Args:
        placa: Placa del vehículo
        db: Sesión de base de datos
        
    Returns:
        Factura generada o None si no hay estadía completada
    """
    # Buscar la última estadía completada (con salida) para esta placa
    estadia = (
        db.query(Estadia)
        .filter(Estadia.placa == placa, Estadia.salida != None)
        .order_by(Estadia.id.desc())
        .first()
    )

    if not estadia:
        return None

    # Verificar si ya existe una factura para esta estadía
    factura_existente = (
        db.query(Factura)
        .filter(Factura.placa == placa)
        .order_by(Factura.id.desc())
        .first()
    )
    
    # Si ya hay una factura reciente, no generar otra
    if factura_existente and factura_existente.minutos == estadia.minutos_total:
        return factura_existente

    minutos = estadia.minutos_total
    tarifa = 80  # pesos por minuto

    total = minutos * tarifa

    factura = Factura(
        placa=placa, 
        minutos=minutos, 
        tarifa_minuto=tarifa, 
        total=total
    )

    db.add(factura)
    db.commit()
    db.refresh(factura)

    return factura
