"""
Lists API Endpoints
REST access to the signed-in user's titled lists and the items in them.
All operations go through the MCP tools the agent uses.
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


@router.get("/api/{user_id}/lists")
async def get_lists_endpoint(user_id: str, current_user_id: uuid.UUID = Depends(get_current_user_id)):
    user_uuid = authorize_user(user_id, current_user_id)
    return _unwrap(await get_mcp_server().call_tool("get_lists", {"user_id": str(user_uuid)}))


@router.post("/api/{user_id}/lists")
async def create_list_endpoint(
    user_id: str, request: Dict[str, Any], current_user_id: uuid.UUID = Depends(get_current_user_id)
):
    user_uuid = authorize_user(user_id, current_user_id)
    return _unwrap(await get_mcp_server().call_tool(
        "create_list", {"user_id": str(user_uuid), "title": request.get("title")}
    ))


@router.patch("/api/{user_id}/lists/{list_id}")
async def rename_list_endpoint(
    user_id: str, list_id: str, request: Dict[str, Any], current_user_id: uuid.UUID = Depends(get_current_user_id)
):
    user_uuid = authorize_user(user_id, current_user_id)
    return _unwrap(await get_mcp_server().call_tool(
        "rename_list", {"user_id": str(user_uuid), "list_id": list_id, "title": request.get("title")}
    ))


@router.delete("/api/{user_id}/lists/{list_id}")
async def delete_list_endpoint(
    user_id: str, list_id: str, current_user_id: uuid.UUID = Depends(get_current_user_id)
):
    user_uuid = authorize_user(user_id, current_user_id)
    return _unwrap(await get_mcp_server().call_tool(
        "delete_list", {"user_id": str(user_uuid), "list_id": list_id}
    ))
