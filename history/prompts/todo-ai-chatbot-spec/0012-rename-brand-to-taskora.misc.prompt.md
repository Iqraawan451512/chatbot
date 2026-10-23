---
id: 0012
title: Rename brand to Taskora
stage: misc
date: 2026-10-23
surface: agent
model: claude-opus-5-5
feature: todo-ai-chatbot-spec
branch: 001-todo-ai-chatbot-spec
user: Iqra
command: none
labels: ["branding", "ui"]
links:
  spec: specs/001-todo-ai-chatbot-spec/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - frontend/index.html
 - frontend/src/pages/LandingPage.jsx
 - frontend/src/pages/AuthPage.jsx
 - frontend/src/pages/ChatPage.jsx
tests:
 - Manual: vite build; screenshot of landing on port 3001
---

## Prompt

change the title TaskFlow AI
 any unique name or professional name

## Response snapshot

User delegated the choice; picked "Taskora". Replaced all 9 visible "TaskFlow AI" mentions (nav/brand on landing, auth, app header, footer, hero copy, page title, meta description); page title now "Taskora · Organize anything, just by asking". Left the internal localStorage key `taskflow-session` unchanged so signed-in users are not logged out. Build clean; screenshot confirms.

## Outcome

- ✅ Impact: App rebranded to Taskora.
- 🧪 Tests: Build + visual check PASS.
- 📁 Files: 4 frontend files.
- 🔁 Next prompts: Optional logo/favicon for the new name.
- 🧠 Reflection: Kept the invisible storage key to avoid an unnecessary sign-out.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): Manual PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): none
