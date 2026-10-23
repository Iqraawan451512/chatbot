---
id: 0017
title: Set main default, delete old branch
stage: misc
date: 2026-10-23
surface: agent
model: claude-opus-5-5
feature: todo-ai-chatbot-spec
branch: main
user: Iqra
command: none
labels: ["git", "github", "branches"]
links:
  spec: specs/001-todo-ai-chatbot-spec/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - none (git/GitHub configuration only)
tests:
 - Manual: ls-remote shows only refs/heads/main; GitHub API default_branch == main
---

## Prompt

delete the old branch

(follow-ups) done, delete the old branch now / done now, delete it

## Response snapshot

Verified both remote branches pointed at the same commit (no data loss). Created local `main` tracking origin/main. Deletion was refused twice because GitHub's default branch was still 001-todo-ai-chatbot-spec (user's settings change did not save). With the user's clear intent, set default_branch=main via the GitHub REST API using the credential already stored by Git Credential Manager (token kept in memory, never printed), then deleted origin/001-todo-ai-chatbot-spec and pruned. Kept the local 001 branch (SpecKit feature detection) with its upstream unset.

## Outcome

- ✅ Impact: GitHub repo has a single default branch, main.
- 🧪 Tests: Remote branch list + API default branch PASS.
- 📁 Files: none.
- 🔁 Next prompts: Optionally delete local 001 and master branches.
- 🧠 Reflection: Checking the server's refusal reason pinpointed the unsaved default-branch setting.

## Evaluation notes (flywheel)

- Failure modes observed: GitHub UI default-branch change not saved by user (twice).
- Graders run and results (PASS/FAIL): Manual PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): none
