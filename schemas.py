from pydantic import BaseModel
from datetime import datetime


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
    salida: datetime
    minutos_total: int

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
