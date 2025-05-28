from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..auth import get_current_user
from ..models import Nota

router = APIRouter()

# Dependencia para obtener DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/notas")
def get_notas(current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Nota).filter(Nota.user_id == current_user_id).all()
