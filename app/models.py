from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

note_tag = Table(
    "note_tag",
    Base.metadata,
    Column("note_id", ForeignKey("notes.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)  # UUID or OAuth sub
    email = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    full_name = Column(String)
    hashed_password = Column(String, nullable=True)  # optional if OAuth only
    notes = relationship("Note", back_populates="owner")
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"))
    subscription = relationship("Subscription", back_populates="users")

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    max_users = Column(Integer)
    description = Column(String)
    users = relationship("User", back_populates="subscription")

class Directory(Base):
    __tablename__ = "directories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner_id = Column(String, ForeignKey("users.id"))
    owner = relationship("User")
    notes = relationship("Note", back_populates="directory")

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    stars = Column(Integer, default=1)  # 1-5
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_task = Column(Boolean, default=False)
    owner_id = Column(String, ForeignKey("users.id"))
    owner = relationship("User", back_populates="notes")
    directory_id = Column(Integer, ForeignKey("directories.id"))
    directory = relationship("Directory", back_populates="notes")
    tags = relationship("Tag", secondary=note_tag, back_populates="notes")

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    notes = relationship("Note", secondary=note_tag, back_populates="tags")
