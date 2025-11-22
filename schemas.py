from pydantic import BaseModel
from datetime import datetime


class EventoCreate(BaseModel):
    placa: str
    tipo: str  # entrada / salida


class EstadiaResponse(BaseModel):
    id: int
    placa: str
    entrada: datetime
    salida: datetime | None
    minutos_total: int | None

    class Config:
        orm_mode = True


class FacturaResponse(BaseModel):
    id: int
    placa: str
    minutos: int
    tarifa_minuto: float
    total: float
    fecha: datetime

    class Config:
        orm_mode = True
