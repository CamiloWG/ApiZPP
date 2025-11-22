from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Evento, Estadia
from schemas import EventoCreate
from datetime import datetime
from utils import calcular_minutos

router = APIRouter(prefix="/eventos", tags=["Eventos"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def registrar_evento(evento: EventoCreate, db: Session = Depends(get_db)):
    nuevo_evento = Evento(placa=evento.placa, tipo=evento.tipo)
    db.add(nuevo_evento)
    db.commit()

    # LÓGICA DE ESTADÍAS
    if evento.tipo == "entrada":
        # Crear nueva estadía
        est = Estadia(placa=evento.placa, entrada=datetime.utcnow())
        db.add(est)
    else:
        # Cerrar estadía abierta
        estadia = (
            db.query(Estadia)
            .filter(Estadia.placa == evento.placa, Estadia.salida == None)
            .first()
        )

        if estadia:
            estadia.salida = datetime.utcnow()
            estadia.minutos_total = calcular_minutos(estadia.entrada, estadia.salida)

    db.commit()

    return {"message": "Evento registrado"}
