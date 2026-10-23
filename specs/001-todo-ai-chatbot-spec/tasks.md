---
description: "Task list for Todo AI Chatbot implementation"
---

# Tasks: Todo AI Chatbot

**Input**: Design documents from `/specs/001-todo-ai-chatbot-spec/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure per implementation plan with backend/ and frontend/ directories
- [x] T002 [P] Initialize Python requirements.txt with FastAPI, OpenAI Agents SDK, Official MCP SDK, SQLModel, Neon PostgreSQL driver dependencies
- [x] T003 [P] Initialize Node.js package.json with OpenAI ChatKit and related dependencies
- [x] T004 Create initial .env file structure with Neon PostgreSQL connection settings and Better Auth placeholders

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

- [x] T005 Create SQLModel database models for User in backend/src/models/user.py
- [x] T006 [P] Create SQLModel database models for Conversation in backend/src/models/conversation.py
- [x] T007 [P] Create SQLModel database models for Message in backend/src/models/message.py
- [x] T008 [P] Create SQLModel database models for TodoTask in backend/src/models/todo_task.py
- [x] T009 Create database service in backend/src/services/database.py
- [x] T010 Setup database migration framework in backend/
- [x] T011 Initialize MCP server framework in backend/mcp_server/server.py
- [x] T012 Setup conversation service in backend/src/services/conversation_service.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Natural Language Todo Management (Priority: P1) 🎯 MVP

**Goal**: User interacts with the AI chatbot using natural language to manage their todo list (add, update, complete, delete tasks).

**Independent Test**: User can add a new task by saying "Add buy groceries to my list" and the system responds with confirmation and stores the task.

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T013 [P] [US1] Contract test for POST /api/{user_id}/chat endpoint in backend/tests/contract/test_chat_api.py
- [ ] T014 [P] [US1] Integration test for natural language task addition in backend/tests/integration/test_todo_management.py

### Implementation for User Story 1

- [x] T015 [P] [US1] Create add_task MCP tool in backend/mcp_server/tools/add_task.py
- [x] T016 [P] [US1] Create list_tasks MCP tool in backend/mcp_server/tools/list_tasks.py
- [x] T017 [P] [US1] Create update_task MCP tool in backend/mcp_server/tools/update_task.py
- [x] T018 [P] [US1] Create complete_task MCP tool in backend/mcp_server/tools/complete_task.py
- [x] T019 [P] [US1] Create delete_task MCP tool in backend/mcp_server/tools/delete_task.py
- [x] T020 [US1] Implement todo agent configuration in backend/src/agents/todo_agent.py
- [x] T021 [US1] Implement chat API endpoint in backend/src/api/chat.py
- [x] T022 [US1] Create frontend ChatInterface component in frontend/src/components/ChatInterface.jsx
- [x] T023 [US1] Create frontend ChatPage in frontend/src/pages/ChatPage.jsx
- [x] T024 [US1] Connect frontend to chat endpoint in frontend/src/services/apiClient.js

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - MCP Tool Integration (Priority: P2)

**Goal**: AI agent performs todo operations only through MCP tools without direct database access.

**Independent Test**: AI agent can successfully add, list, update, complete, and delete tasks by calling the appropriate MCP tools.

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [ ] T025 [P] [US2] Contract test for MCP tool integration in backend/tests/contract/test_mcp_integration.py
- [ ] T026 [P] [US2] Integration test for AI agent tool usage in backend/tests/integration/test_agent_tools.py

### Implementation for User Story 2

- [x] T027 [US2] Enhance AI agent to ensure it only uses MCP tools in backend/src/agents/todo_agent.py
- [x] T028 [US2] Implement database access restriction validation in backend/src/services/database.py
- [x] T029 [US2] Add validation to ensure no direct database queries from agent in backend/src/agents/todo_agent.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Stateless Backend Operation (Priority: P3)

**Goal**: Backend server operates in a stateless manner, loading conversation history from database for each request.

**Independent Test**: Server can handle multiple requests without maintaining session state in memory, loading conversation history from database each time.

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [ ] T030 [P] [US3] Contract test for stateless operation in backend/tests/contract/test_stateless_operation.py
- [ ] T031 [P] [US3] Integration test for conversation persistence in backend/tests/integration/test_conversation_persistence.py

### Implementation for User Story 3

- [x] T032 [P] [US3] Implement conversation history loading in backend/src/services/conversation_service.py
- [x] T033 [US3] Enhance chat API to load conversation history from DB in backend/src/api/chat.py
- [x] T034 [US3] Implement conversation state persistence in backend/src/services/conversation_service.py

**Checkpoint**: All user stories should now be independently functional

---

[Add more user story phases as needed, following the same pattern]

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T035 [P] Documentation updates in README.md
- [x] T036 Error handling and validation improvements across all services
- [x] T037 [P] Additional unit tests in backend/tests/unit/ and frontend/tests/unit/
- [x] T038 Security enhancements and input validation
- [x] T039 Run quickstart validation from specs/001-todo-ai-chatbot-spec/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Contract test for POST /api/{user_id}/chat endpoint in backend/tests/contract/test_chat_api.py"
Task: "Integration test for natural language task addition in backend/tests/integration/test_todo_management.py"

# Launch all MCP tools for User Story 1 together:
Task: "Create add_task MCP tool in backend/mcp_server/tools/add_task.py"
Task: "Create list_tasks MCP tool in backend/mcp_server/tools/list_tasks.py"
Task: "Create update_task MCP tool in backend/mcp_server/tools/update_task.py"
Task: "Create complete_task MCP tool in backend/mcp_server/tools/complete_task.py"
Task: "Create delete_task MCP tool in backend/mcp_server/tools/delete_task.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence