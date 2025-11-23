from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Estadia
from schemas import EstadiaResponse

router = APIRouter(prefix="/estadias", tags=["Estadías"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[EstadiaResponse])
def listar_estadias(db: Session = Depends(get_db)):
    """Lista todas las estadías registradas"""
    return db.query(Estadia).all()


@router.get("/activas", response_model=list[EstadiaResponse])
def listar_estadias_activas(db: Session = Depends(get_db)):
    """Lista las estadías activas (vehículos actualmente estacionados)"""
    return db.query(Estadia).filter(Estadia.salida == None).all()


@router.get("/completadas", response_model=list[EstadiaResponse])
def listar_estadias_completadas(db: Session = Depends(get_db)):
    """Lista las estadías completadas (vehículos que ya salieron)"""
    return db.query(Estadia).filter(Estadia.salida != None).all()


@router.get("/{placa}", response_model=list[EstadiaResponse])
def obtener_estadias_placa(placa: str, db: Session = Depends(get_db)):
    """Obtiene todas las estadías de una placa específica"""
    estadias = db.query(Estadia).filter(Estadia.placa == placa).all()
    
    if not estadias:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron estadías para la placa {placa}"
        )
    
    return estadias


@router.get("/{placa}/activa", response_model=EstadiaResponse)
def obtener_estadia_activa(placa: str, db: Session = Depends(get_db)):
    """Obtiene la estadía activa de una placa (si existe)"""
    estadia = (
        db.query(Estadia)
        .filter(Estadia.placa == placa, Estadia.salida == None)
        .first()
    )
    
    if not estadia:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró estadía activa para la placa {placa}"
        )
    
    return estadia
