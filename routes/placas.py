from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Placa, VehiculoRobado, Evento
from schemas import PlacaCreate, PlacaResponse, VerificacionPlaca
from datetime import datetime

router = APIRouter(prefix="/placas", tags=["Placas"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=PlacaResponse)
def crear_placa(placa: PlacaCreate, db: Session = Depends(get_db)):
    """Crea una nueva placa en el sistema"""
    db_placa = db.query(Placa).filter(Placa.placa == placa.placa).first()
    if db_placa:
        raise HTTPException(status_code=400, detail="La placa ya está registrada")
    nueva_placa = Placa(placa=placa.placa)
    db.add(nueva_placa)
    db.commit()
    db.refresh(nueva_placa)
    return nueva_placa

@router.get("/", response_model=list[PlacaResponse])
def listar_placas(db: Session = Depends(get_db)):
    """Lista todas las placas"""
    return db.query(Placa).all()

@router.delete("/{placa_id}")
def eliminar_placa(placa_id: int, db: Session = Depends(get_db)):
    """Elimina una placa por su ID"""
    db_placa = db.query(Placa).filter(Placa.id_placa == placa_id).first()
    if not db_placa:
        raise HTTPException(status_code=404, detail="Placa no encontrada")
    db.delete(db_placa)
    db.commit()
    return {"message": "Placa eliminada exitosamente"}

@router.post("/verificar", response_model=dict)
def verificar_placa(info: VerificacionPlaca, db: Session = Depends(get_db)):
    """
    Verifica si una placa está listada como robada.
    Si lo está, genera un evento con la información enviada.
    """
    # Verificar si la placa existe en la tabla de vehículos robados
    vehiculo_robado = db.query(VehiculoRobado).filter(VehiculoRobado.placa == info.placa).first()
    
    if vehiculo_robado:
        # La placa está reportada como robada, generar el evento
        # Primero asegurar que la placa exista en la tabla maestra de Placas
        placa_maestra = db.query(Placa).filter(Placa.placa == info.placa).first()
        if not placa_maestra:
            # Si no existe en la tabla principal pero sí en la de robados (inconsistencia rara), la creamos
            placa_maestra = Placa(placa=info.placa)
            db.add(placa_maestra)
            db.commit()

        nuevo_evento = Evento(
            placa=info.placa,
            ubicacion=info.ubicacion,
            tipo_evento=info.tipo_evento,
            fecha_hora=datetime.utcnow()
        )
        db.add(nuevo_evento)
        db.commit()
        db.refresh(nuevo_evento)

        # TODO: Implementar el envío de alerta al CAI de policía más cercano a futuro

        return {
            "alerta": True,
            "mensaje": f"ALERTA: La placa {info.placa} reportada como robada ha sido detectada.",
            "evento_generado": {
                "id_evento": nuevo_evento.id_evento,
                "placa": nuevo_evento.placa,
                "ubicacion": nuevo_evento.ubicacion,
                "tipo_evento": nuevo_evento.tipo_evento,
                "fecha_hora": nuevo_evento.fecha_hora
            }
        }
    else:
        return {
            "alerta": False,
            "mensaje": f"La placa {info.placa} no está reportada como robada."
        }
