from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
import uuid
from datetime import datetime
from .user import User


class ConversationBase(SQLModel):
    user_id: uuid.UUID = Field(foreign_key="user.id")
    title: Optional[str] = Field(default=None, max_length=255)
    is_active: bool = Field(default=True)


class Conversation(ConversationBase, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")