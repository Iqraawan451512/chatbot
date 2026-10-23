"""
MCP Server for Todo AI Chatbot
Implements the Model Context Protocol server to handle todo operations
"""

from typing import Dict, Any, Callable
import asyncio
import json
from .tools.add_task import add_task
from .tools.list_tasks import list_tasks
from .tools.update_task import update_task
from .tools.complete_task import complete_task
from .tools.delete_task import delete_task
from .tools.list_tools import get_lists, create_list, rename_list, delete_list


class MCPServer:
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        """Register the default todo management tools"""
        self.register_tool("add_task", add_task)
        self.register_tool("list_tasks", list_tasks)
        self.register_tool("update_task", update_task)
        self.register_tool("complete_task", complete_task)
        self.register_tool("delete_task", delete_task)
        self.register_tool("get_lists", get_lists)
        self.register_tool("create_list", create_list)
        self.register_tool("rename_list", rename_list)
        self.register_tool("delete_list", delete_list)

    def register_tool(self, name: str, func: Callable):
        """Register a new tool with the MCP server"""
        self.tools[name] = func

    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a registered tool with the provided parameters"""
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found",
                "message": f"Tool '{tool_name}' is not available"
            }

        try:
            # Call the tool function
            result = await self.tools[tool_name](params)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error executing tool '{tool_name}': {str(e)}"
            }

    def get_available_tools(self) -> list:
        """Get list of available tools"""
        return list(self.tools.keys())


# Global MCP server instance
mcp_server = MCPServer()


def get_mcp_server():
    """Get the global MCP server instance"""
    return mcp_server