from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import VehiculoRobado, Placa
from schemas import VehiculoRobadoCreate, VehiculoRobadoResponse

router = APIRouter(prefix="/vehiculos_robados", tags=["Vehículos Robados"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=VehiculoRobadoResponse)
def reportar_vehiculo_robado(vehiculo: VehiculoRobadoCreate, db: Session = Depends(get_db)):
    """Reporta un vehículo como robado"""
    # Verificar si ya está reportado
    db_vehiculo = db.query(VehiculoRobado).filter(VehiculoRobado.placa == vehiculo.placa).first()
    if db_vehiculo:
        raise HTTPException(status_code=400, detail="El vehículo ya está reportado como robado")
    
    # Asegurar que la placa exista en la tabla principal de placas
    placa_maestra = db.query(Placa).filter(Placa.placa == vehiculo.placa).first()
    if not placa_maestra:
        nueva_placa = Placa(placa=vehiculo.placa)
        db.add(nueva_placa)
        db.commit()

    nuevo_reporte = VehiculoRobado(placa=vehiculo.placa, estado=vehiculo.estado)
    db.add(nuevo_reporte)
    db.commit()
    db.refresh(nuevo_reporte)
    return nuevo_reporte

@router.get("/", response_model=list[VehiculoRobadoResponse])
def listar_vehiculos_robados(db: Session = Depends(get_db)):
    """Lista todos los vehículos reportados como robados"""
    return db.query(VehiculoRobado).all()

@router.delete("/{vehiculo_id}")
def eliminar_reporte(vehiculo_id: int, db: Session = Depends(get_db)):
    """Elimina un reporte de vehículo robado por su ID"""
    db_vehiculo = db.query(VehiculoRobado).filter(VehiculoRobado.id_vehiculo == vehiculo_id).first()
    if not db_vehiculo:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    db.delete(db_vehiculo)
    db.commit()
    return {"message": "Reporte de vehículo robado eliminado exitosamente"}
