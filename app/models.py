from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, Table, DateTime, UniqueConstraint, Index, MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

auth_users = Table(
    'users', Base.metadata,
    Column('id', UUID(as_uuid=True), primary_key=True),
    schema='auth',
)

class Nota(Base):
    __tablename__ = "notas"

    __table_args__ = (
        Index('ix_notas_user_id', 'user_id'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    starred = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    folder_id = Column(UUID(as_uuid=True), ForeignKey("folders.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tags = relationship("Tag", secondary="note_tags", back_populates="notas")
    folder = relationship("Folder", back_populates="notas")
    versions = relationship("NoteVersion", back_populates="nota", cascade="all, delete-orphan")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id"), nullable=False)
    name = Column(String(50), nullable=False)
    notas = relationship("Nota", secondary="note_tags", back_populates="tags")
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_user_tagname"),)



class NoteTag(Base):
    __tablename__ = "note_tags"

    note_id = Column(UUID(as_uuid=True), ForeignKey("notas.id"), primary_key=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.id"), primary_key=True)


class Folder(Base):
    __tablename__ = "folders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    notas = relationship("Nota", back_populates="folder")



class NoteVersion(Base):
    __tablename__ = "note_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    note_id = Column(UUID(as_uuid=True), ForeignKey("notas.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    nota = relationship("Nota", back_populates="versions")
