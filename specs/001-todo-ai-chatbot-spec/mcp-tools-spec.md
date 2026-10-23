# MCP Tools Specification for Todo AI Chatbot

## Purpose
The Model Context Protocol (MCP) tools provide a controlled interface for the AI agent to perform todo operations. These tools ensure that the AI agent never accesses the database directly, maintaining the required separation of concerns.

## Available Tools

### 1. add_task
**Purpose**: Adds a new task to the user's todo list.

**Inputs**:
- `user_id`: String identifier for the user
- `task_description`: String containing the task description
- `due_date`: Optional string with due date in ISO 8601 format (YYYY-MM-DD)

**Output**:
- `success`: Boolean indicating success of operation
- `task_id`: String identifier for the newly created task
- `message`: String confirmation message for the user

**Behavior**:
- Creates a new task associated with the specified user
- Sets initial status to "incomplete"
- Generates a unique task ID
- Persists task to database

### 2. list_tasks
**Purpose**: Retrieves all tasks for a specific user.

**Inputs**:
- `user_id`: String identifier for the user
- `status_filter`: Optional string to filter by status ("all", "completed", "incomplete")

**Output**:
- `success`: Boolean indicating success of operation
- `tasks`: Array of task objects containing id, description, status, and due_date
- `count`: Number of tasks returned

**Behavior**:
- Returns all tasks associated with the specified user
- Optionally filters by completion status
- Does not modify any existing tasks

### 3. update_task
**Purpose**: Updates an existing task's properties.

**Inputs**:
- `user_id`: String identifier for the user
- `task_id`: String identifier for the task to update
- `new_description`: Optional string with updated task description
- `new_due_date`: Optional string with updated due date in ISO 8601 format
- `new_status`: Optional string with updated status ("completed", "incomplete")

**Output**:
- `success`: Boolean indicating success of operation
- `message`: String confirmation message
- `updated_task`: Object containing the updated task details

**Behavior**:
- Validates that the task belongs to the specified user
- Updates only the provided fields
- Maintains unchanged fields as they were

### 4. complete_task
**Purpose**: Marks a specific task as completed.

**Inputs**:
- `user_id`: String identifier for the user
- `task_id`: String identifier for the task to mark as completed

**Output**:
- `success`: Boolean indicating success of operation
- `message`: String confirmation message
- `completed_task`: Object containing the completed task details

**Behavior**:
- Validates that the task exists and belongs to the user
- Updates the task status to "completed"
- Preserves all other task properties

### 5. delete_task
**Purpose**: Removes a task from the user's todo list.

**Inputs**:
- `user_id`: String identifier for the user
- `task_id`: String identifier for the task to delete

**Output**:
- `success`: Boolean indicating success of operation
- `message`: String confirmation message

**Behavior**:
- Validates that the task exists and belongs to the user
- Permanently removes the task from the database
- Returns success confirmation

## MCP Tool Constraints

### Security Requirements
- Each tool must verify that the user owns the requested task(s)
- Tools must not expose internal database structure or implementation details
- Tools must validate all inputs before performing operations

### Statelessness Requirements
- MCP tools must be stateless and not maintain session data
- Each tool call must be self-contained with all necessary parameters
- Tools must persist all changes to the database

### Error Handling
- Tools must return appropriate success/error indicators
- Tools must provide meaningful error messages for debugging
- Tools must not expose sensitive system information to users

### Data Validation
- All inputs must be validated for type and format
- Task IDs must be verified for existence before operations
- User IDs must be validated for authenticity
- Due dates must conform to ISO 8601 format when provided

## Integration Requirements
- MCP tools must integrate seamlessly with the Neon Serverless PostgreSQL database
- Tools must use SQLModel for database operations
- All operations must be atomic where appropriate
- Tools must handle database connection failures gracefully