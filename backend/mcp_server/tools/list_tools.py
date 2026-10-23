"""
MCP Tools: todo lists
Create, read, rename and delete titled lists that group a user's tasks
"""

from sqlmodel import Session, select
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
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

DEFAULT_LIST_TITLE = "My tasks"
MAX_TITLE_LENGTH = 100


def task_to_dict(task: TodoTask) -> Dict[str, Any]:
    return {
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


def _parse_uuid(value: Any, name: str) -> Tuple[Optional[uuid.UUID], Optional[Dict[str, Any]]]:
    try:
        return uuid.UUID(str(value)), None
    except ValueError:
        return None, {"success": False, "message": f"Invalid {name} format: {value}"}


def _clean_title(title: Any) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    title = str(title or "").strip()
    if not title:
        return None, {"success": False, "message": "List title cannot be empty."}
    if len(title) > MAX_TITLE_LENGTH:
        return None, {"success": False, "message": f"List title must be at most {MAX_TITLE_LENGTH} characters."}
    return title, None


def _user_lists(session: Session, user_id: uuid.UUID):
    statement = select(TodoList).where(TodoList.user_id == user_id).order_by(TodoList.created_at.asc())
    return session.exec(statement).all()


def get_or_create_default_list(session: Session, user_id: uuid.UUID) -> TodoList:
    """
    The list used when a task is added without naming one: the only list if
    the user has exactly one, otherwise "My tasks" (created if missing).
    """
    lists = _user_lists(session, user_id)
    if len(lists) == 1:
        return lists[0]
    for todo_list in lists:
        if todo_list.title.lower() == DEFAULT_LIST_TITLE.lower():
            return todo_list
    todo_list = TodoList(user_id=user_id, title=DEFAULT_LIST_TITLE)
    session.add(todo_list)
    session.commit()
    session.refresh(todo_list)
    return todo_list


def _adopt_orphan_tasks(session: Session, user_id: uuid.UUID) -> None:
    """Move tasks created before lists existed into the default list"""
    orphans = session.exec(
        select(TodoTask).where(TodoTask.user_id == user_id).where(TodoTask.list_id == None)  # noqa: E711
    ).all()
    if not orphans:
        return
    default_list = get_or_create_default_list(session, user_id)
    for task in orphans:
        task.list_id = default_list.id
        session.add(task)
    session.commit()


def _find_list(session: Session, user_id: uuid.UUID, list_id: uuid.UUID) -> Optional[TodoList]:
    statement = select(TodoList).where(TodoList.id == list_id).where(TodoList.user_id == user_id)
    return session.exec(statement).first()


async def get_lists(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return all of the user's lists (oldest first), each with its top-level tasks
    (oldest first); every task carries its sub-items in "subtasks"

    Expected params:
    - user_id: str (UUID of the user)
    """
    try:
        user_id, error = _parse_uuid(params.get("user_id"), "user_id")
        if error:
            return error

        with next(get_session()) as session:
            _adopt_orphan_tasks(session, user_id)
            lists = _user_lists(session, user_id)
            tasks = session.exec(
                select(TodoTask).where(TodoTask.user_id == user_id).order_by(TodoTask.created_at.asc())
            ).all()

            # Top-level items per list, each carrying its sub-items
            subtasks: Dict[uuid.UUID, list] = {}
            for task in tasks:
                if task.parent_id:
                    subtasks.setdefault(task.parent_id, []).append(task_to_dict(task))

            by_list: Dict[uuid.UUID, list] = {todo_list.id: [] for todo_list in lists}
            for task in tasks:
                if not task.parent_id and task.list_id in by_list:
                    item = task_to_dict(task)
                    item["subtasks"] = subtasks.get(task.id, [])
                    by_list[task.list_id].append(item)

            result_lists = []
            for todo_list in lists:
                list_tasks = by_list[todo_list.id]
                everything = list_tasks + [sub for t in list_tasks for sub in t["subtasks"]]
                result_lists.append({
                    "id": str(todo_list.id),
                    "title": todo_list.title,
                    "created_at": todo_list.created_at.isoformat(),
                    "task_count": len(everything),
                    "completed_count": sum(1 for t in everything if t["status"] == "completed"),
                    "tasks": list_tasks
                })

            return {
                "success": True,
                "count": len(result_lists),
                "lists": result_lists,
                "message": f"You have {len(result_lists)} list(s)."
            }

    except Exception as e:
        return {"success": False, "message": f"Error loading lists: {str(e)}"}


async def create_list(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new titled list

    Expected params:
    - user_id: str (UUID of the user)
    - title: str (list title, e.g. "Groceries")
    """
    try:
        user_id, error = _parse_uuid(params.get("user_id"), "user_id")
        if error:
            return error
        title, error = _clean_title(params.get("title"))
        if error:
            return error

        with next(get_session()) as session:
            for existing in _user_lists(session, user_id):
                if existing.title.lower() == title.lower():
                    return {"success": False, "message": f"You already have a list called '{existing.title}'."}

            todo_list = TodoList(user_id=user_id, title=title)
            session.add(todo_list)
            session.commit()
            session.refresh(todo_list)

            return {
                "success": True,
                "list_id": str(todo_list.id),
                "message": f"Created the list '{title}'.",
                "list": {"id": str(todo_list.id), "title": todo_list.title}
            }

    except Exception as e:
        return {"success": False, "message": f"Error creating list: {str(e)}"}


async def rename_list(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Rename a list

    Expected params:
    - user_id: str (UUID of the user)
    - list_id: str (UUID of the list)
    - title: str (new title)
    """
    try:
        user_id, error = _parse_uuid(params.get("user_id"), "user_id")
        if error:
            return error
        list_id, error = _parse_uuid(params.get("list_id"), "list_id")
        if error:
            return error
        title, error = _clean_title(params.get("title"))
        if error:
            return error

        with next(get_session()) as session:
            todo_list = _find_list(session, user_id, list_id)
            if not todo_list:
                return {"success": False, "message": "List not found."}

            for existing in _user_lists(session, user_id):
                if existing.id != list_id and existing.title.lower() == title.lower():
                    return {"success": False, "message": f"You already have a list called '{existing.title}'."}

            old_title = todo_list.title
            todo_list.title = title
            todo_list.updated_at = datetime.utcnow()
            session.add(todo_list)
            session.commit()

            return {
                "success": True,
                "message": f"Renamed the list '{old_title}' to '{title}'.",
                "list": {"id": str(todo_list.id), "title": title}
            }

    except Exception as e:
        return {"success": False, "message": f"Error renaming list: {str(e)}"}


async def delete_list(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Delete a list and every task in it

    Expected params:
    - user_id: str (UUID of the user)
    - list_id: str (UUID of the list)
    """
    try:
        user_id, error = _parse_uuid(params.get("user_id"), "user_id")
        if error:
            return error
        list_id, error = _parse_uuid(params.get("list_id"), "list_id")
        if error:
            return error

        with next(get_session()) as session:
            todo_list = _find_list(session, user_id, list_id)
            if not todo_list:
                return {"success": False, "message": "List not found."}

            tasks = session.exec(
                select(TodoTask).where(TodoTask.list_id == list_id).where(TodoTask.user_id == user_id)
            ).all()
            # Sub-items first so no row points at a deleted parent
            for task in sorted(tasks, key=lambda t: t.parent_id is None):
                session.delete(task)
                session.flush()
            title = todo_list.title
            session.delete(todo_list)
            session.commit()

            return {
                "success": True,
                "deleted_tasks": len(tasks),
                "message": f"Deleted the list '{title}' and its {len(tasks)} item(s)."
            }

    except Exception as e:
        return {"success": False, "message": f"Error deleting list: {str(e)}"}
