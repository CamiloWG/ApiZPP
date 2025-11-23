from sqlalchemy import Column, Integer, String, DateTime, Float
from database import Base
from datetime import datetime


class Evento(Base):
    __tablename__ = "eventos"

    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String, index=True)
    tipo = Column(String)  # "entrada" o "salida"
    timestamp = Column(DateTime, default=datetime.utcnow)


class Estadia(Base):
    __tablename__ = "estadias"

    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String, index=True)
    entrada = Column(DateTime)
    salida = Column(DateTime, nullable=True)
    minutos_total = Column(Integer, nullable=True)


class Factura(Base):
    __tablename__ = "facturas"

    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String)
    minutos = Column(Integer)
    tarifa_minuto = Column(Float, default=80)  # 80 pesos por minuto
    total = Column(Float)
    fecha = Column(DateTime, default=datetime.utcnow)
