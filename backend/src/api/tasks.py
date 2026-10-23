"""
Tasks API Endpoints
Direct REST access to the signed-in user's tasks so the UI can show and edit
the real task list. All operations go through the same MCP tools the agent uses.
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

import sys
from pathlib import Path

# Add the backend directory to the Python path to resolve imports
backend_dir = Path(__file__).resolve().parents[2]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from mcp_server.server import get_mcp_server
from src.services.auth_service import get_current_user_id, authorize_user


router = APIRouter()


def _unwrap(result: Dict[str, Any]) -> Dict[str, Any]:
    """Turn a failed tool result into an HTTP error"""
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Request failed"))
    return result


@router.get("/api/{user_id}/tasks")
async def list_tasks_endpoint(user_id: str, current_user_id: uuid.UUID = Depends(get_current_user_id)):
    user_uuid = authorize_user(user_id, current_user_id)
    result = await get_mcp_server().call_tool("list_tasks", {"user_id": str(user_uuid)})
    return _unwrap(result)


@router.post("/api/{user_id}/tasks")
async def add_task_endpoint(
    user_id: str, request: Dict[str, Any], current_user_id: uuid.UUID = Depends(get_current_user_id)
):
    user_uuid = authorize_user(user_id, current_user_id)
    description = str(request.get("description", "")).strip()
    if not description:
        raise HTTPException(status_code=400, detail="Task description cannot be empty")
    params = {"user_id": str(user_uuid), "task_description": description}
    if request.get("list_id"):
        params["list_id"] = request["list_id"]
    if request.get("parent_id"):
        params["parent_id"] = request["parent_id"]
    result = await get_mcp_server().call_tool("add_task", params)
    return _unwrap(result)


@router.patch("/api/{user_id}/tasks/{task_id}")
async def update_task_endpoint(
    user_id: str, task_id: str, request: Dict[str, Any], current_user_id: uuid.UUID = Depends(get_current_user_id)
):
    """Edit a task's description and/or status ("completed" / "incomplete")"""
    user_uuid = authorize_user(user_id, current_user_id)
    params: Dict[str, Any] = {"user_id": str(user_uuid), "task_id": task_id}

    if "description" in request:
        description = str(request["description"] or "").strip()
        if not description:
            raise HTTPException(status_code=400, detail="Task description cannot be empty")
        params["new_description"] = description
    if "status" in request:
        params["new_status"] = request["status"]

    result = await get_mcp_server().call_tool("update_task", params)
    return _unwrap(result)


@router.post("/api/{user_id}/tasks/{task_id}/complete")
async def complete_task_endpoint(
    user_id: str, task_id: str, current_user_id: uuid.UUID = Depends(get_current_user_id)
):
    user_uuid = authorize_user(user_id, current_user_id)
    result = await get_mcp_server().call_tool(
        "complete_task", {"user_id": str(user_uuid), "task_id": task_id}
    )
    return _unwrap(result)


@router.delete("/api/{user_id}/tasks/{task_id}")
async def delete_task_endpoint(
    user_id: str, task_id: str, current_user_id: uuid.UUID = Depends(get_current_user_id)
):
    user_uuid = authorize_user(user_id, current_user_id)
    result = await get_mcp_server().call_tool(
        "delete_task", {"user_id": str(user_uuid), "task_id": task_id}
    )
    return _unwrap(result)
