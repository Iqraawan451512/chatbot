from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
import uuid
from datetime import datetime
from .user import User
from .conversation import Conversation


class MessageBase(SQLModel):
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id")
    sender_type: str = Field(regex="^(user|ai)$")  # Enum: 'user' or 'ai'
    sender_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")  # Foreign key to User (only for user messages)
    content: str = Field(nullable=False)
    message_type: str = Field(default="text", regex="^(text|command_result|error)$")  # Enum: 'text', 'command_result', 'error'


class Message(MessageBase, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
    sender: Optional[User] = Relationship(back_populates="messages")