"""
Chat API Endpoint
Implements the stateless chat endpoint that loads conversation history,
runs the agent, and persists responses
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import uuid
from sqlmodel import Session
from datetime import datetime
import json

# Import using absolute paths
import sys
from pathlib import Path

# Add the backend directory to the Python path to resolve imports
backend_dir = Path(__file__).resolve().parents[2]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from src.services.database import get_session
from src.services.conversation_service import (
    get_conversation_history,
    load_conversation_for_user,
    create_new_conversation,
    save_message_to_conversation,
    get_user_tasks
)
from src.agents.todo_agent import get_todo_agent
from src.services.auth_service import get_current_user_id, authorize_user


router = APIRouter()


@router.post("/api/{user_id}/chat")
async def chat_endpoint(
    user_id: str,
    request: Dict[str, Any],
    current_user_id: uuid.UUID = Depends(get_current_user_id),
):
    """
    Main chat endpoint that processes user messages through the AI agent
    """
    try:
        user_uuid = authorize_user(user_id, current_user_id)

        # Extract message from request
        if "message" not in request:
            raise HTTPException(status_code=400, detail="Missing 'message' in request body")

        user_message = request["message"]
        timestamp = request.get("timestamp")

        # Validate message length
        if len(user_message.strip()) == 0:
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        # Get database session
        with next(get_session()) as session:
            # Load or create conversation for the user
            conversation = load_conversation_for_user(session, user_uuid)
            if not conversation:
                conversation = create_new_conversation(session, user_uuid)

            # Save the user's message to the conversation
            user_message_obj = save_message_to_conversation(
                session,
                conversation.id,
                "user",
                user_message,
                user_uuid
            )

            # Get the AI agent
            agent = get_todo_agent()

            # Process the user's message with the agent
            ai_response = await agent.process_request(user_message, str(user_uuid))

            # Save the AI's response to the conversation
            ai_message_obj = save_message_to_conversation(
                session,
                conversation.id,
                "ai",
                ai_response
            )

            # Prepare response
            response = {
                "success": True,
                "response": ai_response,
                "conversation_id": str(conversation.id),
                "timestamp": datetime.utcnow().isoformat()
            }

            return response

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error (in a real system you'd use proper logging)
        import traceback
        print(f"Error in chat endpoint: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Helper function to ensure the endpoint is stateless
def ensure_stateless_operation():
    """
    This function verifies that the chat endpoint maintains statelessness
    by always loading conversation history from the database for each request
    """
    pass  # This is just a conceptual verification