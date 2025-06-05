from pydantic import BaseModel, UUID4
# from uuid import UUID
from typing import Optional, TypeVar, Generic, List, Generic

class NoteCreate(BaseModel):
    user_id: UUID4
    language_iso: str


class NoteResponse(BaseModel):
    id: UUID4
    user_id: UUID4
    title: str

    model_config = {
        "from_attributes": True
    }

T = TypeVar("T")

class ErrorResponse(BaseModel):
    title: str
    message: str

class BaseResponse(BaseModel, Generic[T]):
    status: str  # "success" o "error"
    data: Optional[T]
    error: Optional[ErrorResponse]

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
    folder: FolderResponse = None
    tags: List[TagResponse] = []

    model_config = {
        "from_attributes": True
    }
