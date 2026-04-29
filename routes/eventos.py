from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Evento, Placa
from schemas import EventoCreate, EventoResponse

router = APIRouter(prefix="/eventos", tags=["Eventos"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=EventoResponse)
def crear_evento(evento: EventoCreate, db: Session = Depends(get_db)):
    """Crea un nuevo evento manualmente"""
    # Asegurar que la placa exista
    placa_maestra = db.query(Placa).filter(Placa.placa == evento.placa).first()
    if not placa_maestra:
        nueva_placa = Placa(placa=evento.placa)
        db.add(nueva_placa)
        db.commit()

    nuevo_evento = Evento(
        placa=evento.placa,
        ubicacion=evento.ubicacion,
        tipo_evento=evento.tipo_evento
    )
    db.add(nuevo_evento)
    db.commit()
    db.refresh(nuevo_evento)
    return nuevo_evento

@router.get("/", response_model=list[EventoResponse])
def listar_eventos(db: Session = Depends(get_db)):
    """Lista todos los eventos registrados"""
    return db.query(Evento).all()

@router.get("/{placa}", response_model=list[EventoResponse])
def obtener_eventos_placa(placa: str, db: Session = Depends(get_db)):
    """Obtiene todos los eventos asociados a una placa específica"""
    eventos = db.query(Evento).filter(Evento.placa == placa).all()
    if not eventos:
        raise HTTPException(status_code=404, detail=f"No se encontraron eventos para la placa {placa}")
    return eventos

@router.delete("/{evento_id}")
def eliminar_evento(evento_id: int, db: Session = Depends(get_db)):
    """Elimina un evento por su ID"""
    db_evento = db.query(Evento).filter(Evento.id_evento == evento_id).first()
    if not db_evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    db.delete(db_evento)
    db.commit()
    return {"message": "Evento eliminado exitosamente"}
