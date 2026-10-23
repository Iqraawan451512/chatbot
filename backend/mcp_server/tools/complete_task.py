"""
MCP Tool: complete_task
Marks a specific task as completed
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


async def complete_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mark a specific task as completed

    Expected params:
    - user_id: str (UUID of the user)
    - task_id: str (UUID of the task to mark as completed)
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

            # If task is already completed, return appropriate message
            if task.status == "completed":
                return {
                    "success": True,
                    "message": f"Task '{task.description}' is already marked as completed.",
                    "task": {
                        "id": str(task.id),
                        "description": task.description,
                        "status": task.status,
                        "due_date": task.due_date.isoformat() if task.due_date else None,
                        "priority": task.priority,
                        "created_at": task.created_at.isoformat(),
                        "updated_at": task.updated_at.isoformat(),
                        "completed_at": task.completed_at.isoformat() if task.completed_at else None
                    }
                }

            # Update task status to completed
            task.status = "completed"
            from datetime import datetime
            task.completed_at = datetime.utcnow()
            task.updated_at = datetime.utcnow()

            # Commit changes
            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "success": True,
                "message": f"Task '{task.description}' has been marked as completed.",
                "task": {
                    "id": str(task.id),
                    "description": task.description,
                    "status": task.status,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "priority": task.priority,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None
                }
            }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error completing task: {str(e)}"
        }