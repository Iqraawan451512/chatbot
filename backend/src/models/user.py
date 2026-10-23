from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
import uuid
from datetime import datetime


class UserBase(SQLModel):
    email: str = Field(unique=True, nullable=False, max_length=255)
    username: Optional[str] = Field(default=None, max_length=100)


class User(UserBase, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    password_hash: Optional[str] = Field(default=None, max_length=255)

    # Relationships
    conversations: List["Conversation"] = Relationship(back_populates="user")
    messages: List["Message"] = Relationship(back_populates="sender")
    todo_tasks: List["TodoTask"] = Relationship(back_populates="user")