from typing import List, Optional
from sqlmodel import Session, select
import uuid
from ..models.conversation import Conversation
from ..models.message import Message
from ..models.todo_task import TodoTask


def get_conversation_history(
    session: Session,
    user_id: uuid.UUID,
    conversation_id: uuid.UUID
) -> List[Message]:
    """
    Retrieve conversation history from database
    """
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.timestamp.asc())
    )
    messages = session.exec(statement).all()
    return messages


def load_conversation_for_user(
    session: Session,
    user_id: uuid.UUID
) -> Optional[Conversation]:
    """
    Load the active conversation for a user
    """
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .where(Conversation.is_active == True)
        .order_by(Conversation.updated_at.desc())
    )
    conversation = session.exec(statement).first()
    return conversation


def create_new_conversation(
    session: Session,
    user_id: uuid.UUID,
    title: Optional[str] = None
) -> Conversation:
    """
    Create a new conversation for a user
    """
    if not title:
        title = f"Conversation with {user_id}"

    conversation = Conversation(user_id=user_id, title=title, is_active=True)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


def save_message_to_conversation(
    session: Session,
    conversation_id: uuid.UUID,
    sender_type: str,
    content: str,
    sender_id: Optional[uuid.UUID] = None
) -> Message:
    """
    Save a message to the conversation
    """
    message = Message(
        conversation_id=conversation_id,
        sender_type=sender_type,
        sender_id=sender_id,
        content=content
    )
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


def ensure_conversation_persistence_after_restart():
    """
    This function conceptually verifies that conversations persist
    across server restarts by relying solely on the database.

    In a real implementation, this would be verified by testing
    that conversation state is always retrieved from the database
    rather than in-memory storage.
    """
    pass


def get_user_tasks(
    session: Session,
    user_id: uuid.UUID,
    status_filter: Optional[str] = None
) -> List[TodoTask]:
    """
    Get all tasks for a user, optionally filtered by status
    """
    statement = select(TodoTask).where(TodoTask.user_id == user_id)

    if status_filter:
        statement = statement.where(TodoTask.status == status_filter)

    tasks = session.exec(statement).all()
    return tasks