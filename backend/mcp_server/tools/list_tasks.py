"""
MCP Tool: list_tasks
Retrieves all tasks for a user, optionally filtered by status
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


async def list_tasks(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    List all tasks for a user, optionally filtered by status

    Expected params:
    - user_id: str (UUID of the user)
    - status_filter: str (optional, "all", "completed", "incomplete")
    """
    try:
        # Validate required parameters
        if "user_id" not in params:
            return {
                "success": False,
                "message": "Missing required parameter: user_id is required"
            }

        user_id_str = params["user_id"]

        # Validate user_id format
        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            return {
                "success": False,
                "message": f"Invalid user_id format: {user_id_str}"
            }

        # Get status filter if provided
        status_filter = params.get("status_filter", "all")
        if status_filter not in ["all", "completed", "incomplete"]:
            return {
                "success": False,
                "message": f"Invalid status_filter: {status_filter}. Must be 'all', 'completed', or 'incomplete'."
            }

        # Create a new database session
        with next(get_session()) as session:
            # Build the query based on status filter
            query = select(TodoTask).where(TodoTask.user_id == user_id)

            if status_filter != "all":
                query = query.where(TodoTask.status == status_filter)

            # Oldest first, so "task 1" always refers to the same task
            query = query.order_by(TodoTask.created_at.asc())

            # Execute query
            tasks = session.exec(query).all()

            # Format tasks for response
            formatted_tasks = []
            for task in tasks:
                formatted_task = {
                    "id": str(task.id),
                    "list_id": str(task.list_id) if task.list_id else None,
                    "parent_id": str(task.parent_id) if task.parent_id else None,
                    "description": task.description,
                    "status": task.status,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "priority": task.priority,
                    "created_at": task.created_at.isoformat(),
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None
                }
                formatted_tasks.append(formatted_task)

            return {
                "success": True,
                "count": len(formatted_tasks),
                "tasks": formatted_tasks,
                "message": f"You have {len(formatted_tasks)} task(s) in your list."
            }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error listing tasks: {str(e)}"
        }