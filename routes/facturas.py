from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from billing import generar_factura
from schemas import FacturaResponse

router = APIRouter(prefix="/facturas", tags=["Facturas"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/{placa}", response_model=FacturaResponse)
def crear_factura(placa: str, db: Session = Depends(get_db)):
    factura = generar_factura(placa, db)

    if not factura:
        return {"error": "No hay estadía finalizada para esta placa"}

    return factura
