---
id: 0007
title: Sign in, edit/delete, landing visual
stage: green
date: 2026-10-23
surface: agent
model: claude-opus-5-5
feature: todo-ai-chatbot-spec
branch: 001-todo-ai-chatbot-spec
user: Iqra
command: none
labels: ["auth", "sign-in", "edit-task", "delete-task", "landing-page", "ui"]
links:
  spec: specs/001-todo-ai-chatbot-spec/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - .gitignore
 - backend/main.py
 - backend/requirements.txt
 - backend/src/api/auth.py
 - backend/src/api/chat.py
 - backend/src/api/tasks.py
 - backend/src/services/auth_service.py
 - backend/src/services/database.py
 - backend/src/models/user.py
 - backend/src/agents/todo_agent.py
 - backend/mcp_server/tools/list_tasks.py
 - frontend/src/services/apiClient.js
 - frontend/src/pages/AuthPage.jsx
 - frontend/src/pages/ChatPage.jsx
 - frontend/src/pages/LandingPage.jsx
 - frontend/src/components/TodoList.jsx
 - frontend/src/components/ChatInterface.jsx
 - frontend/src/App.css
tests:
 - Manual: FastAPI TestClient E2E (signup/dup/short pw/bad signin/signin/me, 401 no/bad token, 403 other user, 21 chat commands incl. edit/rename/delete/clear/reopen, PATCH desc/status/empty)
 - Manual: password_hash migration on a copy of the real DB (idempotent)
 - Manual: live Vite proxy round trip with auth; vite build; screenshots (landing desktop + true 390px mobile, sign-up page, signed-in app)
---

## Prompt

make a sign in feature also remove or change the chatbot picture you showed in landing page also edit delete features in chat bot and list of todos

## Response snapshot

Sign in: email+password accounts (name, email, password ≥8). PBKDF2-SHA256 (310k iterations, stdlib) password hashing, PyJWT HS256 7-day tokens; secret from AUTH_SECRET env or a generated git-ignored backend/.auth_secret. New /api/auth/signup|signin|me; chat and tasks routes require Bearer token and reject other users' ids (403). password_hash column added with idempotent ALTER TABLE migration. Frontend AuthPage with Sign in / Sign up tabs, session in localStorage, 401 → sign out with notice, /#signin /#signup deep links.

Landing: chat mockup replaced with a "Today's plan" task board (numbered tasks, edit/delete icons, progress ring, toasts); username form replaced by Get started / Sign in CTAs.

Edit/delete: TodoList numbered rows matching chat numbers, ✎ and double-click inline edit (Enter/Esc), delete with inline Delete/Keep confirm, checkbox toggles done/not done via new PATCH endpoint. Chat agent rewritten: earliest-verb intent detection, edit/rename ("edit task 1 to X", "rename A to B"), delete by number/name/ordinal, "clear completed tasks", reopen, help; ambiguous or unknown references ask instead of silently acting on the first task (previous behavior). Chat UI adds Edit/Delete/Help chips and Clear chat. Added .gitignore protecting .env, .auth_secret, *.db.

## Outcome

- ✅ Impact: Real accounts, per-user data isolation, edit/delete in both chat and list, new landing visual.
- 🧪 Tests: All manual E2E checks passed.
- 📁 Files: 11 backend (2 new), 6 frontend (1 new), .gitignore new.
- 🔁 Next prompts: Restart user's backend on 8001; add pytest/vitest suites; rate-limit auth endpoints; password reset.
- 🧠 Reflection: Old agent fell back to deleting the first task on unmatched references, which was a data-loss bug fixed as part of the delete feature.

## Evaluation notes (flywheel)

- Failure modes observed: User's own servers occupied test ports; PowerShell case-insensitive variables broke a test script; headless browser min width distorted mobile screenshots.
- Graders run and results (PASS/FAIL): Manual E2E PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Add pytest coverage for auth and agent intent parsing.
