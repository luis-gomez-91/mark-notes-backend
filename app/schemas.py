from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int
    class Config:
        orm_mode = True

class DirectoryBase(BaseModel):
    name: str

class DirectoryCreate(DirectoryBase):
    pass

class Directory(DirectoryBase):
    id: int
    class Config:
        orm_mode = True

class NoteBase(BaseModel):
    title: str
    content: str
    stars: int = 1
    is_task: bool = False
    directory_id: Optional[int] = None
    tag_ids: Optional[List[int]] = []

class NoteCreate(NoteBase):
    pass

class Note(NoteBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    tags: List[Tag] = []
    class Config:
        orm_mode = True

class Subscription(BaseModel):
    id: int
    name: str
    max_users: int
    description: str
    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: Optional[str] = None

class User(UserBase):
    id: str
    is_active: bool
    subscription: Optional[Subscription]
    class Config:
        orm_mode = True
