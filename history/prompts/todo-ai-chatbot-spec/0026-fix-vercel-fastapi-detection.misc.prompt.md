---
id: 0026
title: Fix Vercel FastAPI auto-detection
stage: misc
date: 2026-10-24
surface: agent
model: claude-opus-5-5
feature: todo-ai-chatbot-spec
branch: main
user: Iqra
command: none
labels: ["deployment", "vercel", "bugfix"]
links:
  spec: specs/001-todo-ai-chatbot-spec/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - vercel.json
 - api/requirements.txt (moved from requirements.txt)
 - backend/requirements.txt
 - backend/setup.py
 - README.md
tests:
 - Manual: vercel.json valid JSON with framework null; no root requirements.txt/pyproject/Pipfile/app entry files remain
 - Manual: api/requirements.txt is plain PEP 508 (7 packages) and matches setup.py; pip dry-run from backend/ PASS
---

## Prompt

This page is unavailable
A function needed by this page temporarily failed.
please push my code on versal

(follow-up) Vercel runtime logs: every request, including `/` and `/favicon.ico`, hit api/index.py and failed with `ModuleNotFoundError: No module named 'fastapi'`.

## Response snapshot

Tried the Vercel connector (requires the user to authenticate via /mcp); user pasted logs instead. Diagnosis: the root requirements.txt containing fastapi made Vercel auto-detect the project as a FastAPI app, which routed the whole site to Python and replaced the pip install with the custom installCommand (npm). Fix: `"framework": null` in vercel.json so the frontend is built as static files and api/index.py is a separate Python function; moved the package list to api/requirements.txt (next to the function) so nothing at the root triggers FastAPI detection; backend/requirements.txt now includes ../api/requirements.txt; comments and README updated. Committed and pushed to main. Not verifiable locally without Vercel account access.

## Outcome

- ✅ Impact: Expected: static frontend at /, Python function only for /api/* and /health with packages installed.
- 🧪 Tests: Layout/format checks PASS; live verification pending the new deployment.
- 📁 Files: 5 files.
- 🔁 Next prompts: Check new deployment; ensure DATABASE_URL and AUTH_SECRET are set.
- 🧠 Reflection: Vercel's zero-config Python detection changes routing and install behaviour; pin the framework explicitly.

## Evaluation notes (flywheel)

- Failure modes observed: Vercel framework auto-detection from a root requirements.txt.
- Graders run and results (PASS/FAIL): Manual PASS (local checks)
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): If packages are still missing, check the build log for the Python install step.
