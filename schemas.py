from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# --- Esqueas para Placa ---
class PlacaBase(BaseModel):
    placa: str

class PlacaCreate(PlacaBase):
    pass

class PlacaResponse(PlacaBase):
    id_placa: int

    class Config:
        from_attributes = True


# --- Esquemas para VehiculoRobado ---
class VehiculoRobadoBase(BaseModel):
    placa: str
    estado: str

class VehiculoRobadoCreate(VehiculoRobadoBase):
    pass

class VehiculoRobadoResponse(VehiculoRobadoBase):
    id_vehiculo: int
    fecha_reporte: datetime

    class Config:
        from_attributes = True


# --- Esquemas para Evento ---
class EventoBase(BaseModel):
    placa: str
    ubicacion: str
    tipo_evento: str

class EventoCreate(EventoBase):
    pass

class EventoResponse(EventoBase):
    id_evento: int
    fecha_hora: datetime

    class Config:
        from_attributes = True


# --- Esquemas para la verificación de placa ---
class VerificacionPlaca(BaseModel):
    placa: str
    ubicacion: str
    tipo_evento: str
