from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Estadia
from schemas import EstadiaResponse

router = APIRouter(prefix="/estadias", tags=["Estadías"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[EstadiaResponse])
def get_estadias(db: Session = Depends(get_db)):
    return db.query(Estadia).all()
