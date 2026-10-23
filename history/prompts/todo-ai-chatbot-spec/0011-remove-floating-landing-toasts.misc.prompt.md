---
id: 0011
title: Remove floating landing toasts
stage: misc
date: 2026-10-23
surface: agent
model: claude-opus-5-5
feature: todo-ai-chatbot-spec
branch: 001-todo-ai-chatbot-spec
user: Iqra
command: none
labels: ["landing-page", "ui", "cleanup"]
links:
  spec: specs/001-todo-ai-chatbot-spec/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - frontend/src/pages/LandingPage.jsx
 - frontend/src/App.css
tests:
 - Manual: vite build; screenshot of landing hero on port 3001
---

## Prompt

perfect now just change one thing that is floating notifiction type animation on landing page

## Response snapshot

Asked whether to remove, freeze, or convert to real toasts; user chose "Remove them". Deleted both floating cards ("Task completed", "Task updated") from the hero in LandingPage.jsx and removed their CSS (.floating-card, .toast-icon, .card-a, .card-b, @keyframes float, mobile hide rule). Build clean; screenshot confirms hero shows only the "Today's plan" board.

## Outcome

- ✅ Impact: Calmer landing hero without floating notifications.
- 🧪 Tests: Build + visual check PASS.
- 📁 Files: 2 frontend files.
- 🔁 Next prompts: none.
- 🧠 Reflection: A one-question check avoided guessing between remove/freeze/restyle.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): Manual PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): none
