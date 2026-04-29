from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Placa(Base):
    __tablename__ = "placas"

    id_placa = Column(Integer, primary_key=True, index=True)
    placa = Column(String, unique=True, index=True, nullable=False)

    vehiculo_robado = relationship("VehiculoRobado", back_populates="placa_rel", uselist=False)
    eventos = relationship("Evento", back_populates="placa_rel")


class VehiculoRobado(Base):
    __tablename__ = "vehiculos_robados"

    id_vehiculo = Column(Integer, primary_key=True, index=True)
    placa = Column(String, ForeignKey("placas.placa"), unique=True, nullable=False)
    fecha_reporte = Column(DateTime, default=datetime.utcnow)
    estado = Column(String, nullable=False)

    placa_rel = relationship("Placa", back_populates="vehiculo_robado")


class Evento(Base):
    __tablename__ = "eventos"

    id_evento = Column(Integer, primary_key=True, index=True)
    placa = Column(String, ForeignKey("placas.placa"), nullable=False)
    fecha_hora = Column(DateTime, default=datetime.utcnow)
    ubicacion = Column(String, nullable=False)
    tipo_evento = Column(String, nullable=False)

    placa_rel = relationship("Placa", back_populates="eventos")
