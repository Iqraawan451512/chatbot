"""
MCP Tool: delete_task
Removes a task from the user's todo list
"""

from sqlmodel import Session, select
from typing import Dict, Any
import uuid
import sys
from pathlib import Path

# Add the backend directory to the Python path to resolve imports
backend_dir = Path(__file__).resolve().parents[3]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from src.models.todo_task import TodoTask
from src.services.database import get_session


async def delete_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove a task from the user's todo list

    Expected params:
    - user_id: str (UUID of the user)
    - task_id: str (UUID of the task to delete)
    """
    try:
        # Validate required parameters
        if "user_id" not in params or "task_id" not in params:
            return {
                "success": False,
                "message": "Missing required parameters: user_id and task_id are required"
            }

        user_id_str = params["user_id"]
        task_id_str = params["task_id"]

        # Validate user_id format
        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            return {
                "success": False,
                "message": f"Invalid user_id format: {user_id_str}"
            }

        # Validate task_id format
        try:
            task_id = uuid.UUID(task_id_str)
        except ValueError:
            return {
                "success": False,
                "message": f"Invalid task_id format: {task_id_str}"
            }

        # Create a new database session
        with next(get_session()) as session:
            # Find the task
            statement = select(TodoTask).where(TodoTask.id == task_id).where(TodoTask.user_id == user_id)
            task = session.exec(statement).first()

            if not task:
                return {
                    "success": False,
                    "message": f"Task with ID {task_id_str} not found or does not belong to user {user_id_str}"
                }

            # Remove its sub-items first, then the task itself
            subtasks = session.exec(
                select(TodoTask).where(TodoTask.parent_id == task_id).where(TodoTask.user_id == user_id)
            ).all()
            for subtask in subtasks:
                session.delete(subtask)
            session.flush()
            session.delete(task)
            session.commit()

            return {
                "success": True,
                "deleted_subtasks": len(subtasks),
                "message": f"Task '{task.description}' has been removed from your list."
            }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error deleting task: {str(e)}"
        }