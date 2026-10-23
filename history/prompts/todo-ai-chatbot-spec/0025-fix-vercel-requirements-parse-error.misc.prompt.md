---
id: 0025
title: Fix Vercel requirements parse error
stage: misc
date: 2026-10-24
surface: agent
model: claude-opus-5-5
feature: todo-ai-chatbot-spec
branch: main
user: Iqra
command: none
labels: ["deployment", "vercel", "dependencies", "bugfix"]
links:
  spec: specs/001-todo-ai-chatbot-spec/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - requirements.txt
 - backend/requirements.txt
 - backend/setup.py
 - README.md
tests:
 - Manual: every non-comment line of root requirements.txt parses as a plain PEP 508 requirement (no pip options, no inline comments)
 - Manual: pip dry-run from repo root and from backend/ (README path) PASS
 - Manual: setup.py install_requires matches root list
---

## Prompt

00:30:08.114 
Error: [PYTHON_REQUIREMENTS_PARSE_ERROR] could not parse requirements.txt: Error parsing included file in `/vercel/path0/requirements.txt` at position 58

## Response snapshot

Position 58 is the start of line 2 (`-r backend/requirements.txt`): Vercel's requirements parser does not support `-r` includes (pip does, so the earlier local test passed). Inverted the arrangement: the root requirements.txt is now the plain package list (no includes, no inline comments) and backend/requirements.txt contains `-r ../requirements.txt` for local installs; setup.py comment updated; README structure line updated. Committed and pushed to main to trigger a Vercel redeploy.

## Outcome

- ✅ Impact: Vercel can parse the Python requirements.
- 🧪 Tests: Format + install-path checks PASS.
- 📁 Files: 4 files.
- 🔁 Next prompts: Check the new Vercel build log / live URL.
- 🧠 Reflection: Local pip success didn't prove Vercel compatibility; the root file should stay plain.

## Evaluation notes (flywheel)

- Failure modes observed: Vercel's parser rejects `-r` includes.
- Graders run and results (PASS/FAIL): Manual PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): none
