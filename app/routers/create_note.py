# app/routers/create_note.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import uuid4
from ..models import Nota
from ..schemas import NoteCreate, NoteResponse, BaseResponse, ErrorResponse
from ..database import get_db

router = APIRouter(
    prefix="/notas",
    tags=["Notas"]
)

@router.post("/", response_model=BaseResponse[NoteResponse])
def create_nota(nota: NoteCreate, db: Session = Depends(get_db)):
    print("ENTRO POSI")
    try:
        new_nota = Nota(
            id=uuid4(),
            user_id=nota.user_id,
            title="Sin título" if nota.language_iso == "es" else "Untitled"
        )
        db.add(new_nota)
        db.commit()
        db.refresh(new_nota)
        print("POSI")

        return BaseResponse(
            status="success",
            data=NoteResponse(
                id=str(new_nota.id),
                user_id=new_nota.user_id,
                title=new_nota.title
            ),
            error=None
        )
    except Exception as e:
        print("NO POSI")

        return BaseResponse(
            status="error",
            data=None,
            error=ErrorResponse(
                title="Error al crear nota",
                message=str(e)
            )
        )
