from fastapi import FastAPI
from database import Base, engine
from routes import eventos, estadias, facturas

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Parking API - Proyecto Zonas de Parqueo Pago")

app.include_router(eventos.router)
app.include_router(estadias.router)
app.include_router(facturas.router)
