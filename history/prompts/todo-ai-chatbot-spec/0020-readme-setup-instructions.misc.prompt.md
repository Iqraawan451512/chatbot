---
id: 0020
title: README with setup instructions
stage: misc
date: 2026-10-23
surface: agent
model: claude-opus-5-5
feature: todo-ai-chatbot-spec
branch: main
user: Iqra
command: none
labels: ["docs", "readme", "dependencies"]
links:
  spec: specs/001-todo-ai-chatbot-spec/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - README.md
 - backend/requirements.txt
tests:
 - Manual: fresh venv `pip install -r requirements.txt` (old file FAILED on nonexistent better-auth==0.0.1; new file PASS)
 - Manual: app started from the fresh venv on port 8003 with temp DB; health, signup, chat (list + sub-item), GET lists PASS
---

## Prompt

add a README with setup instructions

## Response snapshot

Existing README described components the code doesn't use (OpenAI ChatKit, Agents SDK, Neon, Better Auth) and its setup failed: a clean `pip install -r requirements.txt` errors on `better-auth==0.0.1` (not on PyPI). Replaced requirements.txt with the four packages the code imports plus pydantic/SQLAlchemy, pinned to the tested versions (fastapi 0.115.6, uvicorn 0.34.0, sqlmodel 0.0.22, pydantic 2.10.4, SQLAlchemy 2.0.45, PyJWT 2.10.1); verified install and a full smoke test from a fresh venv. Rewrote README: features, stack, prerequisites, per-OS setup, two-terminal run, alternate port via BACKEND_URL, env-var configuration table (notes .env is not loaded), chat command table, API reference with curl example, troubleshooting, project structure, SpecKit SPECIFY_FEATURE note. Not committed.

## Outcome

- ✅ Impact: Accurate README; a new clone can install and run the app.
- 🧪 Tests: Fresh install + smoke test PASS.
- 📁 Files: README.md, backend/requirements.txt.
- 🔁 Next prompts: Commit and push; optionally align setup.py/pyproject.toml pins.
- 🧠 Reflection: Testing the documented steps exposed a broken requirements file that docs alone would have hidden.

## Evaluation notes (flywheel)

- Failure modes observed: placeholder dependency in requirements.txt broke clean installs.
- Graders run and results (PASS/FAIL): Manual PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): none
