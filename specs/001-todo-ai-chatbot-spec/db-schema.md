# Database Schema for Todo AI Chatbot

## Purpose
Defines the database schema for the Todo AI Chatbot system using Neon Serverless PostgreSQL and SQLModel. The schema supports the constitutional requirement of storing conversation history while maintaining statelessness of the server.

## Database System
- **Database**: Neon Serverless PostgreSQL
- **ORM**: SQLModel
- **Connection**: Stateless connections managed per request

## Tables

### 1. users
**Purpose**: Stores user account information.

**Fields**:
- `id` (UUID, Primary Key): Unique identifier for the user
- `email` (VARCHAR(255), Unique, Not Null): User's email address
- `username` (VARCHAR(100)): User's chosen username (optional)
- `created_at` (TIMESTAMP, Not Null): Timestamp when user account was created
- `updated_at` (TIMESTAMP, Not Null): Timestamp when user account was last updated
- `is_active` (BOOLEAN, Default: true): Whether the user account is active

**Indexes**:
- Primary key index on `id`
- Unique index on `email`

### 2. conversations
**Purpose**: Represents individual conversation threads for each user.

**Fields**:
- `id` (UUID, Primary Key): Unique identifier for the conversation
- `user_id` (UUID, Foreign Key): Reference to the user who owns this conversation
- `title` (VARCHAR(255)): Auto-generated title based on first message or user-defined
- `created_at` (TIMESTAMP, Not Null): Timestamp when conversation was started
- `updated_at` (TIMESTAMP, Not Null): Timestamp when conversation was last updated
- `is_active` (BOOLEAN, Default: true): Whether the conversation is active

**Foreign Keys**:
- `user_id` references `users.id`

**Indexes**:
- Primary key index on `id`
- Index on `user_id` for efficient user-based queries
- Index on `user_id` and `is_active` for active conversation queries

### 3. messages
**Purpose**: Stores individual messages within conversations (both user and AI messages).

**Fields**:
- `id` (UUID, Primary Key): Unique identifier for the message
- `conversation_id` (UUID, Foreign Key): Reference to the conversation this message belongs to
- `sender_type` (ENUM: 'user' | 'ai', Not Null): Identifies if message is from user or AI
- `sender_id` (UUID): Reference to sender (user_id for user messages, NULL for AI messages)
- `content` (TEXT, Not Null): The actual message content
- `timestamp` (TIMESTAMP, Not Null): When the message was created
- `message_type` (ENUM: 'text' | 'command_result' | 'error', Default: 'text'): Type of message

**Foreign Keys**:
- `conversation_id` references `conversations.id`
- `sender_id` references `users.id` (only applicable for user messages)

**Indexes**:
- Primary key index on `id`
- Index on `conversation_id` and `timestamp` for chronological ordering
- Index on `sender_type` for filtering message types

### 4. todo_tasks
**Purpose**: Stores individual todo tasks for users.

**Fields**:
- `id` (UUID, Primary Key): Unique identifier for the task
- `user_id` (UUID, Foreign Key): Reference to the user who owns this task
- `description` (TEXT, Not Null): Description of the task
- `status` (ENUM: 'incomplete' | 'completed', Default: 'incomplete'): Current status of the task
- `due_date` (DATE, Nullable): Optional due date for the task
- `created_at` (TIMESTAMP, Not Null): Timestamp when task was created
- `updated_at` (TIMESTAMP, Not Null): Timestamp when task was last updated
- `completed_at` (TIMESTAMP, Nullable): Timestamp when task was completed
- `priority` (INTEGER, Default: 0): Priority level (-1 low, 0 normal, 1 high)

**Foreign Keys**:
- `user_id` references `users.id`

**Indexes**:
- Primary key index on `id`
- Index on `user_id` and `status` for efficient task queries
- Index on `due_date` for deadline-based queries
- Index on `user_id` and `priority` for priority-based queries

### 5. task_attachments
**Purpose**: Stores attachments or additional data related to tasks (optional).

**Fields**:
- `id` (UUID, Primary Key): Unique identifier for the attachment
- `task_id` (UUID, Foreign Key): Reference to the task this attachment belongs to
- `attachment_type` (VARCHAR(50), Not Null): Type of attachment (e.g., 'note', 'file_reference')
- `content` (TEXT): Content of the attachment
- `created_at` (TIMESTAMP, Not Null): Timestamp when attachment was created

**Foreign Keys**:
- `task_id` references `todo_tasks.id`

**Indexes**:
- Primary key index on `id`
- Index on `task_id` for task-related queries

## Relationships
- One user has many conversations
- One conversation has many messages
- One user has many todo tasks
- One task can have many attachments

## Constraints
- All timestamps are stored in UTC
- UUIDs are used for all primary keys to ensure global uniqueness
- Foreign key constraints enforce referential integrity
- Cascade delete on user deletion removes associated conversations and tasks
- Check constraints ensure valid enum values

## Indexing Strategy
- Primary indexes on all primary keys
- Foreign key indexes for relationship queries
- Composite indexes for common query patterns (user_id + status, conversation_id + timestamp)
- Time-based indexes for chronological queries

## Data Retention
- User data is retained according to privacy policy
- Messages and conversations are retained as long as user account exists
- Soft delete approach for conversations (using is_active flag) to maintain data integrity
- Hard delete for tasks upon explicit user request

## Performance Considerations
- Partitioning by user_id for large-scale deployments
- Connection pooling managed by the application layer
- Query optimization for common access patterns (recent conversations, active tasks)
- Efficient indexing for natural language search capabilities