"""
MCP Tool: add_task
Adds a new task to the user's todo list
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

from src.models.todo_list import TodoList
from src.models.todo_task import TodoTask
from src.services.database import get_session
from .list_tools import get_or_create_default_list


async def add_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add a new task to the user's todo list

    Expected params:
    - user_id: str (UUID of the user)
    - task_description: str (description of the task)
    - list_id: str (optional, UUID of the list; defaults to the user's default list)
    - parent_id: str (optional, UUID of a top-level task; adds this task as its sub-item)
    - due_date: str (optional, in YYYY-MM-DD format)
    - priority: int (optional, -1 for low, 0 for normal, 1 for high)
    """
    try:
        # Validate required parameters
        if "user_id" not in params or "task_description" not in params:
            return {
                "success": False,
                "message": "Missing required parameters: user_id and task_description are required"
            }

        user_id_str = params["user_id"]
        task_description = params["task_description"]

        # Validate user_id format
        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            return {
                "success": False,
                "message": f"Invalid user_id format: {user_id_str}"
            }

        # Create a new database session
        with next(get_session()) as session:
            # A sub-item goes under its parent, in the parent's list
            parent = None
            if params.get("parent_id"):
                try:
                    parent_id = uuid.UUID(str(params["parent_id"]))
                except ValueError:
                    return {
                        "success": False,
                        "message": f"Invalid parent_id format: {params['parent_id']}"
                    }
                parent = session.exec(
                    select(TodoTask).where(TodoTask.id == parent_id).where(TodoTask.user_id == user_id)
                ).first()
                if not parent:
                    return {
                        "success": False,
                        "message": "Parent item not found."
                    }
                if parent.parent_id:
                    return {
                        "success": False,
                        "message": "Sub-items can't have their own sub-items. Add it under the main item instead."
                    }

            # Put the task in the parent's list, the requested list, or the default list
            if parent:
                todo_list = session.get(TodoList, parent.list_id) if parent.list_id else get_or_create_default_list(session, user_id)
            elif params.get("list_id"):
                try:
                    list_id = uuid.UUID(str(params["list_id"]))
                except ValueError:
                    return {
                        "success": False,
                        "message": f"Invalid list_id format: {params['list_id']}"
                    }
                todo_list = session.exec(
                    select(TodoList).where(TodoList.id == list_id).where(TodoList.user_id == user_id)
                ).first()
                if not todo_list:
                    return {
                        "success": False,
                        "message": "List not found."
                    }
            else:
                todo_list = get_or_create_default_list(session, user_id)

            # Create new task
            new_task = TodoTask(
                user_id=user_id,
                description=task_description,
                list_id=todo_list.id,
                parent_id=parent.id if parent else None
            )

            # Apply optional parameters if provided
            if "due_date" in params and params["due_date"]:
                from datetime import date
                try:
                    due_date = date.fromisoformat(params["due_date"])
                    new_task.due_date = due_date
                except ValueError:
                    return {
                        "success": False,
                        "message": f"Invalid due_date format: {params['due_date']}. Expected YYYY-MM-DD format."
                    }

            if "priority" in params and params["priority"] is not None:
                priority = params["priority"]
                if isinstance(priority, int) and priority in [-1, 0, 1]:
                    new_task.priority = priority
                else:
                    return {
                        "success": False,
                        "message": f"Invalid priority value: {priority}. Must be -1 (low), 0 (normal), or 1 (high)."
                    }

            # Add task to database
            session.add(new_task)
            session.commit()
            session.refresh(new_task)

            return {
                "success": True,
                "task_id": str(new_task.id),
                "message": (
                    f"Added '{task_description}' under '{parent.description}'." if parent
                    else f"Added '{task_description}' to {todo_list.title}."
                ),
                "task": {
                    "id": str(new_task.id),
                    "list_id": str(todo_list.id),
                    "parent_id": str(parent.id) if parent else None,
                    "list_title": todo_list.title,
                    "description": new_task.description,
                    "status": new_task.status,
                    "due_date": new_task.due_date.isoformat() if new_task.due_date else None,
                    "priority": new_task.priority,
                    "created_at": new_task.created_at.isoformat()
                }
            }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error adding task: {str(e)}"
        }