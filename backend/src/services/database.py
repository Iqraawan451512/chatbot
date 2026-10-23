from sqlmodel import create_engine, Session
from typing import Generator
import os
from ..models.user import User
from ..models.conversation import Conversation
from ..models.message import Message
from ..models.todo_list import TodoList
from ..models.todo_task import TodoTask


# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo_chatbot.db")

# Create engine
engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    """Create database tables"""
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)
    _add_missing_columns()


def _add_missing_columns():
    """
    create_all() never alters existing tables, so add columns introduced
    after a database was first created.
    """
    from sqlalchemy import inspect, text

    uuid_type = "CHAR(32)" if engine.dialect.name == "sqlite" else "UUID"
    new_columns = [
        ("user", "password_hash", "VARCHAR(255)"),
        ("todotask", "list_id", uuid_type),
        ("todotask", "parent_id", uuid_type),
    ]

    inspector = inspect(engine)
    for table, column, column_type in new_columns:
        existing = {col["name"] for col in inspector.get_columns(table)}
        if column not in existing:
            with engine.begin() as conn:
                conn.execute(text(f'ALTER TABLE "{table}" ADD COLUMN {column} {column_type}'))


def get_session() -> Generator[Session, None, None]:
    """Get database session"""
    with Session(engine) as session:
        yield session


def validate_agent_access_only():
    """
    This function conceptually validates that only authorized agents
    (through MCP tools) can access the database.

    In a real implementation, you would have additional security layers
    to ensure that only the AI agent through approved MCP tools can
    perform database operations.
    """
    pass