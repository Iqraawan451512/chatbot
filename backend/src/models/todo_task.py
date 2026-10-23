from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
import uuid
from datetime import datetime, date
from .user import User
from .todo_list import TodoList  # noqa: F401  (registers the todolist table for the list_id foreign key)


class TodoTaskBase(SQLModel):
    user_id: uuid.UUID = Field(foreign_key="user.id")
    description: str = Field(nullable=False)
    status: str = Field(default="incomplete", regex="^(incomplete|completed)$")  # Enum: 'incomplete' or 'completed'
    due_date: Optional[date] = Field(default=None)
    priority: int = Field(default=0)  # -1 (low), 0 (normal), 1 (high)


class TodoTask(TodoTaskBase, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    list_id: Optional[uuid.UUID] = Field(default=None, foreign_key="todolist.id")  # The titled list this task belongs to
    parent_id: Optional[uuid.UUID] = Field(default=None, foreign_key="todotask.id")  # Set on sub-items (one level deep)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)

    # Relationship
    user: User = Relationship(back_populates="todo_tasks")