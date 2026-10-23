import sys
from pathlib import Path
import os

# Add the backend directory to the Python path to resolve imports
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import using absolute paths from the backend directory
import src.api.chat as chat_module
from src.api.chat import router as chat_router
from src.api.tasks import router as tasks_router
from src.api.auth import router as auth_router
from src.api.lists import router as lists_router
from src.services.database import create_db_and_tables


# Create the FastAPI app
app = FastAPI(
    title="Todo AI Chatbot API",
    description="API for the Todo AI Chatbot system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the auth, chat and task routers
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(tasks_router)
app.include_router(lists_router)

# Create database tables on startup
@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Todo AI Chatbot API",
        "status": "running",
        "endpoints": {
            "chat": "/api/{user_id}/chat (POST)"
        }
    }


# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Todo AI Chatbot API"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )