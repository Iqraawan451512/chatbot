---
id: 0006
title: Fix network error and redesign landing
stage: green
date: 2026-10-23
surface: agent
model: claude-opus-5-5
feature: todo-ai-chatbot-spec
branch: 001-todo-ai-chatbot-spec
user: Iqra
command: none
labels: ["bugfix", "network-error", "landing-page", "ui", "frontend", "backend"]
links:
  spec: specs/001-todo-ai-chatbot-spec/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - backend/main.py
 - backend/src/api/chat.py
 - backend/src/api/tasks.py
 - backend/src/agents/todo_agent.py
 - backend/src/models/message.py
 - backend/src/models/user.py
 - frontend/index.html
 - frontend/vite.config.js
 - frontend/src/App.css
 - frontend/src/services/apiClient.js
 - frontend/src/pages/ChatPage.jsx
 - frontend/src/pages/LandingPage.jsx
 - frontend/src/components/ChatInterface.jsx
 - frontend/src/components/TodoList.jsx
tests:
 - Manual: FastAPI TestClient end-to-end (chat add/list/complete, tasks GET/POST/DELETE, CORS preflight) against temp SQLite DB
 - Manual: intent parsing for 10 phrasings
 - Manual: live Vite proxy -> backend round trip; vite build; headless-Edge screenshots (desktop, 390px mobile, app view)
---

## Prompt

that is my chatbot project i want its landing page professional and stylish and also its chatbot showing same error like network error when i am adding or creating new todo fit the error

## Response snapshot

Root causes of the "Network Error":
1. backend/main.py passed `allow_credentials=True` twice to CORSMiddleware -> SyntaxError, backend never started.
2. Port 8000 is occupied by a different app (`src.main:app`, "Todo Web Application API"), so frontend requests hit the wrong server.
3. Once running: chat endpoint rejected non-UUID usernames (400); SQLAlchemy mapper failed because Message.sender_id lacked a FK and User.messages back_populates mismatched (500).
4. Add-task parsing used str.strip("to my list") (character set strip) -> "buy grocerie".

Fixes: removed duplicate kwarg; usernames mapped to deterministic uuid5; FK + back_populates fixed; regex-based add-task extraction; new REST tasks API (GET/POST/complete/DELETE via MCP tools); frontend uses same-origin Vite proxy (BACKEND_URL configurable), real task list synced after each chat, friendly error messages. New professional dark landing page (hero with chat mockup, features, how-it-works, CTA, footer) and redesigned app shell (progress ring, filters, suggestion chips, typing indicator), responsive to 390px.

## Outcome

- ✅ Impact: Chat add/create todo works end-to-end; task panel reflects DB; new landing page.
- 🧪 Tests: TestClient E2E pass; live proxy round trip pass; vite build pass; visual checks pass.
- 📁 Files: 6 backend, 8 frontend (2 new: tasks.py, LandingPage.jsx).
- 🔁 Next prompts: Free port 8000 or run with BACKEND_URL; add automated pytest/vitest tests; real auth (Better Auth).
- 🧠 Reflection: "Network Error" masked several stacked bugs; reproducing via compile + TestClient surfaced each layer.

## Evaluation notes (flywheel)

- Failure modes observed: Silent startup crash surfaced only as generic client network error; port collision with another local project.
- Graders run and results (PASS/FAIL): Manual E2E PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Add pytest for chat + tasks endpoints.
