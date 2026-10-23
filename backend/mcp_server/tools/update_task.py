"""
MCP Tool: update_task
Updates an existing task's properties
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


async def update_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an existing task's properties

    Expected params:
    - user_id: str (UUID of the user)
    - task_id: str (UUID of the task to update)
    - new_description: str (optional, new description)
    - new_due_date: str (optional, new due date in YYYY-MM-DD format)
    - new_status: str (optional, "completed" or "incomplete")
    - new_priority: int (optional, -1 for low, 0 for normal, 1 for high)
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

            # Track if any updates were made
            updates_made = False

            # Update description if provided
            if "new_description" in params and params["new_description"] is not None:
                task.description = params["new_description"]
                updates_made = True

            # Update due date if provided
            if "new_due_date" in params and params["new_due_date"] is not None:
                from datetime import date
                try:
                    due_date = date.fromisoformat(params["new_due_date"])
                    task.due_date = due_date
                    updates_made = True
                except ValueError:
                    return {
                        "success": False,
                        "message": f"Invalid new_due_date format: {params['new_due_date']}. Expected YYYY-MM-DD format."
                    }

            # Update status if provided
            if "new_status" in params and params["new_status"] is not None:
                new_status = params["new_status"]
                if new_status not in ["completed", "incomplete"]:
                    return {
                        "success": False,
                        "message": f"Invalid new_status: {new_status}. Must be 'completed' or 'incomplete'."
                    }

                task.status = new_status
                if new_status == "completed" and not task.completed_at:
                    from datetime import datetime
                    task.completed_at = datetime.utcnow()
                elif new_status == "incomplete":
                    task.completed_at = None

                updates_made = True

            # Update priority if provided
            if "new_priority" in params and params["new_priority"] is not None:
                new_priority = params["new_priority"]
                if isinstance(new_priority, int) and new_priority in [-1, 0, 1]:
                    task.priority = new_priority
                    updates_made = True
                else:
                    return {
                        "success": False,
                        "message": f"Invalid new_priority value: {new_priority}. Must be -1 (low), 0 (normal), or 1 (high)."
                    }

            # If no updates were made, return appropriate message
            if not updates_made:
                return {
                    "success": True,
                    "message": f"No updates were made to task {task_id_str}.",
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

            # Update the updated_at timestamp
            from datetime import datetime
            task.updated_at = datetime.utcnow()

            # Commit changes
            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "success": True,
                "message": f"Task '{task.description}' has been updated.",
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
            "message": f"Error updating task: {str(e)}"
        }