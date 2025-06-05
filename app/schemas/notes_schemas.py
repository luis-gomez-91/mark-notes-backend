from pydantic import BaseModel, UUID4
from typing import Optional, List

class NoteCreate(BaseModel):
    user_id: UUID4 # Asume que necesitas enviar el user_id al crear, aunque en rutas protegidas se toma del token
    language_iso: str
    title: str # Asumo que querrás un título al crear una nota
    content: Optional[str] = None

class NoteResponse(BaseModel):
    id: UUID4
    user_id: UUID4
    title: str
    content: Optional[str] = None # Incluye contenido si se devuelve
    starred: bool = False
    is_archived: bool = False
    is_deleted: bool = False
    # No incluyas folder o tags aquí si solo es la respuesta básica de creación
    # Para la respuesta detallada, usa NotesResponse

    model_config = {
        "from_attributes": True
    }

class TagResponse(BaseModel):
    id: UUID4
    name: str
    user_id: UUID4

    model_config = {
        "from_attributes": True
    }

class FolderResponse(BaseModel):
    id: UUID4
    user_id: UUID4
    name: str

    model_config = {
        "from_attributes": True
    }

class NotesResponse(BaseModel):
    id: UUID4
    title: str
    content: Optional[str]
    starred: bool
    is_archived: bool
    is_deleted: bool
    folder: Optional[FolderResponse] = None # Hacerlo Optional
    tags: List[TagResponse] = []

    model_config = {
        "from_attributes": True
    }