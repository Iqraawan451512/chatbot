# Data Model for Todo AI Chatbot

## Entity: User
**Fields**:
- id: UUID (Primary Key)
- email: String (255 char, Unique, Not Null)
- username: String (100 char, Optional)
- created_at: DateTime (Not Null)
- updated_at: DateTime (Not Null)
- is_active: Boolean (Default: true)

**Relationships**:
- One-to-many with Conversation
- One-to-many with TodoTask

## Entity: Conversation
**Fields**:
- id: UUID (Primary Key)
- user_id: UUID (Foreign Key to User)
- title: String (255 char, Optional)
- created_at: DateTime (Not Null)
- updated_at: DateTime (Not Null)
- is_active: Boolean (Default: true)

**Relationships**:
- Many-to-one with User
- One-to-many with Message

## Entity: Message
**Fields**:
- id: UUID (Primary Key)
- conversation_id: UUID (Foreign Key to Conversation)
- sender_type: Enum ('user' | 'ai') (Not Null)
- sender_id: UUID (Foreign Key to User, Optional)
- content: Text (Not Null)
- timestamp: DateTime (Not Null)
- message_type: Enum ('text' | 'command_result' | 'error') (Default: 'text')

**Relationships**:
- Many-to-one with Conversation
- Many-to-one with User (Optional, only for user messages)

## Entity: TodoTask
**Fields**:
- id: UUID (Primary Key)
- user_id: UUID (Foreign Key to User)
- description: Text (Not Null)
- status: Enum ('incomplete' | 'completed') (Default: 'incomplete')
- due_date: Date (Optional)
- created_at: DateTime (Not Null)
- updated_at: DateTime (Not Null)
- completed_at: DateTime (Optional)
- priority: Integer (Default: 0, Range: -1 to 1)

**Relationships**:
- Many-to-one with User

## Entity: TaskAttachment (Optional)
**Fields**:
- id: UUID (Primary Key)
- task_id: UUID (Foreign Key to TodoTask)
- attachment_type: String (50 char, Not Null)
- content: Text (Optional)
- created_at: DateTime (Not Null)

**Relationships**:
- Many-to-one with TodoTask

## Validation Rules
- All timestamps stored in UTC
- User emails must be unique
- Task status can only be 'incomplete' or 'completed'
- Priority values must be -1 (low), 0 (normal), or 1 (high)
- Due dates must be in the future for incomplete tasks

## State Transitions
- TodoTask: 'incomplete' → 'completed' (via complete_task MCP tool)
- Conversation: active → inactive (via deletion or archival)
- User: active → inactive (via account deactivation)