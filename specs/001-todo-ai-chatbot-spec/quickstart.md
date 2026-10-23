# Quickstart Guide for Todo AI Chatbot

## Prerequisites
- Python 3.11+
- Node.js 18+
- Access to Neon Serverless PostgreSQL
- OpenAI API key
- Better Auth configuration

## Setup Instructions

### 1. Clone and Initialize
```bash
# Clone the repository
git clone <repository-url>
cd <repository-name>

# Navigate to backend
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

### 2. Database Setup
```bash
# Set up database connection
# (Database migrations will be handled by the application)
```

### 3. Run the Application
```bash
# Start the backend server
cd backend
uvicorn main:app --reload

# In a separate terminal, start the frontend
cd frontend
npm install
npm run dev
```

### 4. Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Testing the Chat Interface
1. Navigate to the frontend
2. Authenticate using Better Auth
3. Send a message like "Add buy groceries to my list"
4. Verify the AI responds appropriately
5. Check that the task appears in your todo list

## API Usage Example
```javascript
// Send a message to the chat API
const response = await fetch('/api/user123/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: 'Add buy milk to my list'
  })
});

const result = await response.json();
console.log(result.response); // "I've added 'buy milk' to your list..."
```

## Troubleshooting
- Ensure all environment variables are set correctly
- Verify database connectivity
- Check that MCP server is running and accessible
- Confirm OpenAI API key is valid