from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session, joinedload, selectinload
from typing import List
from ..schemas import NotesResponse
from ..models import Nota
from ..database import get_db
from app.auth import get_current_user_from_api_token
import logging

router = APIRouter()

logger = logging.getLogger("uvicorn.error")

@router.get("/notas", response_model=List[NotesResponse])
async def get_notas(
    request: Request, # Mantén esto si quieres los logs del request
    current_user_id: str = Depends(get_current_user_from_api_token), # ¡Aquí usamos la nueva dependencia!
    db: Session = Depends(get_db)
):
    logger.info("ENTRO LISTADO NOTAS (Ruta protegida)")
    logger.info(f"Authorization header: {request.headers.get('authorization')}")
    # No es necesario leer el body para GET, pero si lo necesitas:
    # try:
    #     body_bytes = await request.body()
    #     logger.info(f"BODY: {body_bytes.decode('utf-8')}")
    # except Exception as e:
    #     logger.error(f"No se pudo leer el body: {e}")

    try:
        notas = db.query(Nota)\
                .filter(Nota.user_id == current_user_id)\
                .options(
                    selectinload(Nota.tags),
                    selectinload(Nota.folder)
                ).all()
        logger.info(f"Notas obtenidas para user_id: {current_user_id}. Cantidad: {len(notas)}")
        return notas
        
    except Exception as e:
        logger.error(f"Error al obtener notas para user_id {current_user_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,  detail="Error al recuperar las notas.")
