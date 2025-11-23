from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Evento, Estadia
from schemas import EventoCreate, EventoResponse
from datetime import datetime
from utils import calcular_minutos

router = APIRouter(prefix="/eventos", tags=["Eventos"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=dict)
def registrar_evento(evento: EventoCreate, db: Session = Depends(get_db)):
    """
    Registra un evento de entrada o salida de un vehículo.
    
    - Para entrada: Crea una nueva estadía
    - Para salida: Cierra la estadía abierta y calcula el tiempo
    """
    # Validar que el tipo sea correcto
    if evento.tipo not in ["entrada", "salida"]:
        raise HTTPException(
            status_code=400,
            detail="El tipo debe ser 'entrada' o 'salida'"
        )
    
    # Registrar el evento
    nuevo_evento = Evento(placa=evento.placa, tipo=evento.tipo)
    db.add(nuevo_evento)
    db.commit()

    # LÓGICA DE ESTADÍAS
    if evento.tipo == "entrada":
        # Verificar si ya hay una estadía abierta para esta placa
        estadia_abierta = (
            db.query(Estadia)
            .filter(Estadia.placa == evento.placa, Estadia.salida == None)
            .first()
        )
        
        if estadia_abierta:
            raise HTTPException(
                status_code=400,
                detail=f"El vehículo {evento.placa} ya tiene una entrada registrada sin salida"
            )
        
        # Crear nueva estadía
        est = Estadia(placa=evento.placa, entrada=datetime.utcnow())
        db.add(est)
        db.commit()
        
        return {
            "message": "Entrada registrada exitosamente",
            "placa": evento.placa,
            "tipo": "entrada",
            "timestamp": nuevo_evento.timestamp
        }
    
    else:  # salida
        # Cerrar estadía abierta
        estadia = (
            db.query(Estadia)
            .filter(Estadia.placa == evento.placa, Estadia.salida == None)
            .first()
        )

        if not estadia:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró una entrada sin salida para la placa {evento.placa}"
            )

        estadia.salida = datetime.utcnow()
        estadia.minutos_total = calcular_minutos(estadia.entrada, estadia.salida)
        db.commit()
        
        return {
            "message": "Salida registrada exitosamente",
            "placa": evento.placa,
            "tipo": "salida",
            "timestamp": nuevo_evento.timestamp,
            "minutos_total": estadia.minutos_total,
            "tarifa_estimada": estadia.minutos_total * 80
        }


@router.get("/", response_model=list[EventoResponse])
def listar_eventos(db: Session = Depends(get_db)):
    """Lista todos los eventos registrados"""
    return db.query(Evento).all()


@router.get("/{placa}", response_model=list[EventoResponse])
def obtener_eventos_placa(placa: str, db: Session = Depends(get_db)):
    """Obtiene todos los eventos de una placa específica"""
    eventos = db.query(Evento).filter(Evento.placa == placa).all()
    
    if not eventos:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron eventos para la placa {placa}"
        )
    
    return eventos
