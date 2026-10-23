---
id: 0010
title: Sub-items under tasks
stage: green
date: 2026-10-23
surface: agent
model: claude-opus-5-5
feature: todo-ai-chatbot-spec
branch: 001-todo-ai-chatbot-spec
user: Iqra
command: none
labels: ["sub-items", "data-model", "agent", "ui"]
links:
  spec: specs/001-todo-ai-chatbot-spec/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - backend/src/models/todo_task.py
 - backend/src/services/database.py
 - backend/mcp_server/tools/add_task.py
 - backend/mcp_server/tools/delete_task.py
 - backend/mcp_server/tools/list_tools.py
 - backend/mcp_server/tools/list_tasks.py
 - backend/src/api/tasks.py
 - backend/src/agents/todo_agent.py
 - frontend/src/services/apiClient.js
 - frontend/src/components/TodoList.jsx
 - frontend/src/components/ChatInterface.jsx
 - frontend/src/App.css
tests:
 - Manual: TestClient E2E incl. user's exact phrase "i want to add fruits in tasks 1", multi sub-items "under <name>", 1.1 numbering for edit/complete/delete, parent delete cascades, no sub-of-sub (chat + REST), "add fruits to my tasks" list match, regression of list commands
 - Manual: parent_id migration on real DB after clean backend restart; vite build; screenshot of nested sub-items
---

## Prompt

Here are your lists:
🗂️ My tasks (0/3 done)
   1. ○ milk potatos
   2. ○ vegatable
   3. ○ fruits in tasks 1
03:25 PM
i want to add fruits in tasks 1
08:26 PM
Added "fruits in tasks 1" to My tasks. ✅
03:26 PM
Show my lists
08:26 PM
Here are your lists:
🗂️ My tasks (0/4 done)
   1. ○ milk potatos
   2. ○ vegatable
   3. ○ fruits in tasks 1
   4. ○ fruits in tasks 1
i want a list under the title whwn i want to add any item in the tasks chatbot 
create it an other tasks not a  item of the tasks

## Response snapshot

Clarified via AskUserQuestion: user wants sub-items under a task ("fruits" under item 1). Added TodoTask.parent_id (self FK, one level) with migration; add_task accepts parent_id (inherits parent's list, rejects sub-of-sub); delete_task cascades to sub-items; get_lists nests "subtasks". Agent: items numbered N and sub-items N.k; "add X in/to/under task N", "add a, b under <name>", "edit task 1.1 to …", "mark fruits in task 1 as done", "delete apples from task 2"; whole-name match wins before scoping; fixed "add X to my tasks" not matching the "My tasks" list. Panel: ＋ button per item opens a sub-item field; sub-items render indented with dashed guide and their own check/edit/delete; delete warns about sub-item count; chat chip "↳ Sub-item". Backend restarted cleanly without --reload after reload hung again.

## Outcome

- ✅ Impact: Items can hold their own sub-items in chat and panel.
- 🧪 Tests: All manual E2E checks passed.
- 📁 Files: 8 backend, 4 frontend.
- 🔁 Next prompts: User can delete the two stray "fruits in tasks 1" items; optional drag-to-nest.
- 🧠 Reflection: The earlier lists feature didn't match the user's mental model (items as titles); asking with previews resolved it.

## Evaluation notes (flywheel)

- Failure modes observed: uvicorn --reload hang on Windows (second time).
- Graders run and results (PASS/FAIL): Manual E2E PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): pytest for agent sub-item parsing.
