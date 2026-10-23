# Todo AI Chatbot

An AI-powered todo management system that allows users to manage their tasks through natural language conversation.

## Architecture

The system follows a stateless architecture with the following components:

- **Frontend**: Built with React and OpenAI ChatKit for user interaction
- **Backend**: Python FastAPI server operating in a stateless manner
- **AI Agent**: Powered by OpenAI Agents SDK that processes user requests
- **MCP Server**: Official MCP SDK providing controlled access to todo operations
- **Database**: Neon Serverless PostgreSQL for persistent storage
- **Authentication**: Better Auth for secure user access

## Key Features

- Natural language task management (add, update, complete, delete tasks)
- MCP tool-based operations ensuring no direct database access by AI agent
- Stateless backend that loads conversation history from database for each request
- Support for multilingual input (including Urdu)

## Setup

1. Clone the repository
2. Install backend dependencies: `cd backend && pip install -r requirements.txt`
3. Install frontend dependencies: `cd frontend && npm install`
4. Configure environment variables in `.env`
5. Start the backend: `cd backend && uvicorn main:app --reload`
6. Start the frontend: `cd frontend && npm run dev`

## Project Structure

```
backend/
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
├── src/
│   ├── models/          # SQLModel database models
│   ├── services/        # Business logic services
│   ├── api/             # API endpoints
│   └── agents/          # AI agent configuration
├── mcp_server/          # MCP server implementation
│   ├── server.py
│   └── tools/
└── tests/

frontend/
├── package.json         # Node.js dependencies
├── src/
│   ├── components/      # React components
│   ├── pages/           # Page components
│   └── services/        # API service clients
└── public/
```

## Constitution Compliance

This system strictly follows the Project Constitution:
- No manual coding by the user
- AI agent never accesses database directly
- Backend remains stateless at all times
- All operations routed through MCP tools
- Conversation state persists only in the database

## Quick Start

1. Clone the repository
2. Install backend dependencies: `cd backend && pip install -r requirements.txt`
3. Install frontend dependencies: `cd frontend && npm install`
4. Configure environment variables in `.env`
5. Start the backend: `cd backend && uvicorn main:app --reload`
6. Start the frontend: `cd frontend && npm run dev`

## Running the Application

The backend API will be available at `http://localhost:8000`. The main endpoints are:
- Root: `GET /` - Welcome message
- Health check: `GET /health` - Service status
- Chat endpoint: `POST /api/{user_id}/chat` - Main chat interface

## API Usage

To interact with the chatbot via API:
```
curl -X POST "http://localhost:8000/api/user123/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add buy groceries to my list"}'
```