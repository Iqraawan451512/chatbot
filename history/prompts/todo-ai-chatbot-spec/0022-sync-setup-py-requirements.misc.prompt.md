---
id: 0022
title: Sync setup.py with requirements
stage: misc
date: 2026-10-23
surface: agent
model: claude-opus-5-5
feature: todo-ai-chatbot-spec
branch: main
user: Iqra
command: none
labels: ["dependencies", "packaging"]
links:
  spec: specs/001-todo-ai-chatbot-spec/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - backend/setup.py
tests:
 - Manual: AST comparison of setup.py install_requires vs requirements.txt -> MATCH
 - Manual: `setup.py egg_info` (output to scratchpad) generates requires.txt with the same 6 pins
---

## Prompt

update setup.py to match requirements.txt

## Response snapshot

Replaced setup.py install_requires (old fastapi 0.104.1, openai, asyncpg, python-multipart, python-dotenv pins) with the same six pins as requirements.txt: fastapi==0.115.6, uvicorn[standard]==0.34.0, sqlmodel==0.0.22, pydantic==2.10.4, SQLAlchemy==2.0.45, PyJWT==2.10.1, plus a "keep in sync" comment. pyproject.toml declares only the build system, so no change there. Verified exact match and setuptools metadata. Not committed.

## Outcome

- ✅ Impact: Packaging metadata consistent with requirements.txt.
- 🧪 Tests: Comparison + egg_info PASS.
- 📁 Files: backend/setup.py.
- 🔁 Next prompts: Commit and push.
- 🧠 Reflection: Generated egg-info outside the repo to avoid stray build files.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): Manual PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): none
