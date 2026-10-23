# Todo AI Chatbot - System Overview

## Purpose
The Todo AI Chatbot is an AI-powered todo management system that allows users to manage their tasks through natural language conversation. The system adheres to the Agentic Dev Stack workflow and follows strict constitutional principles regarding statelessness, MCP tool usage, and database access restrictions.

## Architecture Overview
The system consists of multiple interconnected components that work together to provide a seamless AI-powered todo management experience:

- **Frontend**: Built with OpenAI ChatKit for user interaction
- **Backend**: Python FastAPI server operating in a stateless manner
- **AI Agent**: Powered by OpenAI Agents SDK that processes user requests
- **MCP Server**: Official MCP SDK providing controlled access to todo operations
- **Database**: Neon Serverless PostgreSQL for persistent storage
- **Authentication**: Better Auth for secure user access

## Key Design Principles
1. **Statelessness**: The backend server maintains no conversation state in memory
2. **MCP Authority**: All todo operations must go through MCP tools
3. **No Direct Database Access**: AI agent cannot access database directly
4. **Natural Language Processing**: AI understands and responds to natural language commands
5. **Conversation Persistence**: All conversations are stored in the database

## Data Flow
1. User sends natural language command via frontend
2. Frontend communicates with backend via POST /api/{user_id}/chat
3. Backend loads conversation history from database
4. Backend passes user message to AI agent
5. AI agent selects appropriate MCP tool based on user intent
6. AI agent executes MCP tool to perform todo operation
7. Backend stores conversation (user message + AI response) in database
8. Backend returns AI response to frontend for display

## Technology Stack
- Frontend: OpenAI ChatKit
- Backend: Python FastAPI
- AI Framework: OpenAI Agents SDK
- MCP Server: Official MCP SDK
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth