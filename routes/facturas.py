from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from billing import generar_factura
from schemas import FacturaResponse
from models import Factura

router = APIRouter(prefix="/facturas", tags=["Facturas"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/{placa}", response_model=FacturaResponse)
def crear_factura(placa: str, db: Session = Depends(get_db)):
    """
    Genera una factura para un vehículo que ya salió del parqueadero.
    
    La factura se calcula basándose en la última estadía completada
    con una tarifa de 80 pesos por minuto.
    """
    factura = generar_factura(placa, db)

    if not factura:
        raise HTTPException(
            status_code=404, 
            detail=f"No hay estadía finalizada para la placa {placa}"
        )

    return factura


@router.get("/", response_model=list[FacturaResponse])
def listar_facturas(db: Session = Depends(get_db)):
    """Lista todas las facturas generadas"""
    return db.query(Factura).all()


@router.get("/{placa}", response_model=list[FacturaResponse])
def obtener_facturas_placa(placa: str, db: Session = Depends(get_db)):
    """Obtiene todas las facturas de una placa específica"""
    facturas = db.query(Factura).filter(Factura.placa == placa).all()
    
    if not facturas:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron facturas para la placa {placa}"
        )
    
    return facturas
