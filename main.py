from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routes import eventos, placas, vehiculos_robados

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Vehículos Robados",
    description="Sistema para el registro de vehículos robados y generación de eventos",
    version="2.0.0",
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
app.include_router(placas.router)
app.include_router(vehiculos_robados.router)
app.include_router(eventos.router)

@app.get("/")
def root():
    """Endpoint raíz de la API"""
    return {
        "mensaje": "API de Vehículos Robados",
        "version": "2.0.0",
        "documentacion": "/docs",
        "endpoints": {
            "placas": "/placas",
            "vehiculos_robados": "/vehiculos_robados",
            "eventos": "/eventos",
        },
    }


@app.get("/health")
def health_check():
    """Endpoint para verificar el estado de la API"""
    return {"status": "ok", "message": "API funcionando correctamente"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=80)
