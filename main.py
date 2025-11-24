from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routes import eventos, estadias, facturas

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Zonas de Parqueo Pago",
    description="Sistema de automatización para el cobro en zonas de parqueo pago",
    version="1.0.0",
)

# Configurar CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(eventos.router)
app.include_router(estadias.router)
app.include_router(facturas.router)


@app.get("/")
def root():
    """Endpoint raíz de la API"""
    return {
        "mensaje": "API de Zonas de Parqueo Pago",
        "version": "1.0.0",
        "documentacion": "/docs",
        "endpoints": {
            "eventos": "/eventos",
            "estadias": "/estadias",
            "facturas": "/facturas",
        },
    }


@app.get("/health")
def health_check():
    """Endpoint para verificar el estado de la API"""
    return {"status": "ok", "message": "API funcionando correctamente"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=80)
