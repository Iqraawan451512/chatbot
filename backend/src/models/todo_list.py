from sqlmodel import SQLModel, Field
from typing import Optional
import uuid
from datetime import datetime


class TodoListBase(SQLModel):
    user_id: uuid.UUID = Field(foreign_key="user.id")
    title: str = Field(nullable=False, max_length=100)


class TodoList(TodoListBase, table=True):
    """A titled list (e.g. "Groceries") that groups a user's tasks"""
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
