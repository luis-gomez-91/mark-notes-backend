from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session, joinedload, selectinload
from typing import List
from ..schemas import NotesResponse
from ..models import Nota
from ..database import get_db
from ..auth import get_current_user
import logging

router = APIRouter()

logger = logging.getLogger("uvicorn.error")

@router.get("/notas", response_model=List[NotesResponse])
async def get_notas(
    request: Request, 
    current_user_id: str = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    logger.info("ENTRO LISTADO NOTAS")
    logger.info(f"Authorization header: {request.headers.get('authorization')}")
    for k, v in request.headers.items():
        logger.info(f"{k}: {v}")

    try:
        body_bytes = await request.body()
        logger.info(f"BODY: {body_bytes.decode('utf-8')}")
    except Exception as e:
        logger.error(f"No se pudo leer el body: {e}")

    notas = db.query(Nota)\
              .filter(Nota.user_id == current_user_id)\
              .options(
                  selectinload(Nota.tags),
                  selectinload(Nota.folder)
              ).all()
    return notas
