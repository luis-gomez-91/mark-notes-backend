from pydantic import BaseModel, UUID4
from typing import Optional, TypeVar, Generic, List

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
    code: Optional[str]
    message: str

class BaseResponse(BaseModel, Generic[T]):
    status: str
    data: Optional[T] = None
    error: Optional[ErrorResponse] = None

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
    user_id: UUID4
    title: str
    content: Optional[str] = None
    starred: bool = False
    is_archived: bool = False
    is_deleted: bool = False
    folder: Optional[FolderResponse] = None
    tags: List[TagResponse] = []

    model_config = {
        "from_attributes": True
    }


class LoginSuccessData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: Optional[str] = None