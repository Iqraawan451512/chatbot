# API Specification for Todo AI Chatbot

## Purpose
Defines the API endpoints for the Todo AI Chatbot backend, enabling communication between the frontend and the AI processing system while maintaining statelessness.

## Base URL
All endpoints are relative to the base URL which will be configured based on deployment environment.

## Endpoint: POST /api/{user_id}/chat

### Purpose
Main endpoint for user interactions with the AI chatbot. Receives user messages and returns AI responses.

### Parameters
- `user_id` (path parameter): Unique identifier for the authenticated user

### Request Body
```json
{
  "message": "string",
  "timestamp": "ISO 8601 datetime string (optional)"
}
```

#### Request Body Fields
- `message`: The natural language message from the user (required)
- `timestamp`: Optional timestamp of when the message was sent (defaults to current time if not provided)

### Response
```json
{
  "success": "boolean",
  "response": "string",
  "conversation_id": "string",
  "timestamp": "ISO 8601 datetime string"
}
```

#### Response Fields
- `success`: Indicates if the request was processed successfully
- `response`: The AI-generated response to the user's message
- `conversation_id`: Identifier for the conversation thread
- `timestamp`: Server time when the response was generated

### Response Codes
- `200`: Success - AI processed the message and returned a response
- `400`: Bad Request - Invalid request format or missing required fields
- `401`: Unauthorized - Invalid or missing user authentication
- `404`: Not Found - User ID does not exist in the system
- `500`: Internal Server Error - Unexpected server error occurred

### Processing Flow
1. Authenticate user based on user_id
2. Load conversation history from database for the user
3. Append the new user message to the conversation history
4. Pass the complete conversation context to the AI agent
5. AI agent processes the message and may call MCP tools
6. AI generates a response based on user intent and tool results
7. Store the new message and AI response in the database
8. Return the AI response to the frontend

### Security Requirements
- User authentication required via Better Auth
- User can only access their own conversation data
- Rate limiting to prevent abuse
- Input validation to prevent injection attacks

### Statelessness Requirements
- No conversation state stored in server memory
- Entire conversation history loaded from database for each request
- All responses stored to database before returning to client
- Server can restart without losing conversation state

### Error Handling
- Invalid user_id returns 404
- Malformed requests return 400 with error details
- MCP tool failures are handled gracefully with appropriate user messaging
- Database connection issues return 500 with error details

## Authentication
All API endpoints require user authentication via Better Auth. The user_id in the path parameter must correspond to an authenticated user session.

## Rate Limiting
- Maximum 100 requests per hour per user
- Maximum 1000 requests per minute per IP address
- Excessive requests result in temporary blocking

## Request Size Limits
- Maximum message length: 10,000 characters
- Maximum request body size: 15KB

## Headers
- `Content-Type`: application/json (for POST requests)
- `Authorization`: Bearer token from Better Auth (if required by implementation)