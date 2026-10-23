# Conversation Flow for Todo AI Chatbot

## Purpose
Defines the expected conversation patterns and flows between users and the AI chatbot for effective todo management.

## Basic Conversation Flow

### 1. Initial Interaction
**User**: "Hi" or "Hello"
**AI**: "Hello! I'm your AI assistant for managing todos. You can ask me to add, list, update, complete, or delete tasks. For example, try saying 'Add buy groceries to my list'."

### 2. Task Addition
**User**: "Add [task description] to my list"
**AI**: "I've added '[task description]' to your list. You now have X tasks in your list."

### 3. Task Listing
**User**: "Show me my tasks" or "What do I have to do?"
**AI**: Lists all incomplete tasks with their IDs, descriptions, and due dates if applicable.

### 4. Task Completion
**User**: "Complete task [ID]" or "Mark [task description] as done"
**AI**: "I've marked '[task description]' as completed. You now have X tasks remaining."

### 5. Task Update
**User**: "Update task [ID] to [new description]" or "Change [old description] to [new description]"
**AI**: "I've updated your task from '[old description]' to '[new description]'."

### 6. Task Deletion
**User**: "Delete task [ID]" or "Remove [task description] from my list"
**AI**: "I've removed '[task description]' from your list."

## Advanced Conversation Flows

### 1. Natural Language Variations
The AI should understand various ways to express the same intent:
- Add: "Add", "Create", "Put on my list", "Remind me to"
- List: "Show", "Display", "List", "Tell me", "What do I have"
- Complete: "Complete", "Done", "Finish", "Mark as finished"
- Update: "Change", "Update", "Modify", "Edit"
- Delete: "Delete", "Remove", "Get rid of", "Cancel"

### 2. Contextual Understanding
**User**: "Add buy milk to my list for tomorrow"
**AI**: "I've added 'buy milk' to your list with due date tomorrow. You now have X tasks in your list."

**User**: "Add meeting with John to my list for Friday at 3pm"
**AI**: "I've added 'meeting with John' to your list with due date Friday at 3pm. You now have X tasks in your list."

### 3. Multi-step Conversations
**User**: "Add buy groceries to my list"
**AI**: "I've added 'buy groceries' to your list. You now have 3 tasks in your list."
**User**: "What are my tasks?"
**AI**: "1. Buy groceries (incomplete)\n2. Call mom (incomplete)\n3. Finish report (incomplete)"
**User**: "Complete task 1"
**AI**: "I've marked 'buy groceries' as completed. You now have 2 tasks remaining."
**User**: "Show my completed tasks"
**AI**: "1. Buy groceries (completed)"

### 4. Error Handling Flows

#### Unknown Command
**User**: "What's the weather like?"
**AI**: "I'm focused on helping you manage your todo list. You can ask me to add, list, update, complete, or delete tasks. For example, try saying 'Add water plants to my list'."

#### Invalid Task Reference
**User**: "Complete task 10"
**AI**: "I couldn't find task 10 in your list. Your current tasks are numbered 1 to 3. Would you like me to show you your tasks?"

#### Ambiguous Requests
**User**: "Update buy groceries"
**AI**: "Could you clarify what you'd like to update about 'buy groceries'? Would you like to change the description, mark it as complete, or remove it?"

## Language Support

### English Flow
**User**: "Add buy milk to my list"
**AI**: "I've added 'buy milk' to your list."

### Urdu Flow (Bonus Feature)
**User**: "میری فہرست میں دودھ خریدنے کا کام شامل کریں"
**AI**: "میں نے آپ کی فہرست میں 'دودھ خریدنا' کا کام شامل کر دیا ہے۔"

## Session Independence
Each conversation is independent and the AI does not rely on memory of previous sessions:
- Upon each interaction, the AI loads the current state from the database
- The AI responds based only on the current request and stored data
- No persistent context is maintained on the server

## State Transitions
The conversation flow supports these state transitions:

1. **Idle State**: Awaiting user input
2. **Processing State**: Analyzing user intent and calling MCP tools
3. **Response State**: Generating and returning AI response
4. **Error State**: Handling invalid requests or tool failures

## Error Recovery
- If an MCP tool fails, the AI informs the user and suggests retrying
- If the AI misunderstands a request, it asks for clarification
- If there's a database issue, the AI informs the user of a temporary issue

## Special Cases

### Empty Task List
**User**: "Show me my tasks"
**AI**: "You currently have no tasks in your list. You can add a task by saying something like 'Add [task description] to my list'."

### Large Task Lists
**User**: "Show me my tasks"
**AI**: If the list is very long (>10 tasks), the AI may respond:
"I have [X] tasks in your list. Would you like to see all tasks or filter by priority/status?"

### Duplicate Tasks
**User**: "Add buy milk to my list" (when already exists)
**AI**: "You already have 'buy milk' in your list. Would you like me to update it instead?"

## Conversation Continuity
Even though the server is stateless, conversation continuity is maintained by:
- Loading full conversation history from database for each request
- Using context from the conversation history to inform responses
- Storing each new interaction in the database immediately
- Ensuring users can resume conversations after server restarts