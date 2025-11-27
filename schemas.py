from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class EventoCreate(BaseModel):
    placa: str
    tipo: str  # entrada / salida


class EventoResponse(BaseModel):
    id: int
    placa: str
    tipo: str
    timestamp: datetime

    class Config:
        from_attributes = True


class EstadiaResponse(BaseModel):
    id: int
    placa: str
    entrada: datetime
    salida: Optional[datetime]
    minutos_total: Optional[int]

    class Config:
        from_attributes = True


class FacturaResponse(BaseModel):
    id: int
    placa: str
    minutos: int
    tarifa_minuto: float
    total: float
    fecha: datetime

    class Config:
        from_attributes = True
