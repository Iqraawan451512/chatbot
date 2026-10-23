---
id: 0024
title: Prepare Vercel deployment
stage: green
date: 2026-10-23
surface: agent
model: claude-opus-5-5
feature: todo-ai-chatbot-spec
branch: main
user: Iqra
command: none
labels: ["deployment", "vercel", "postgresql", "neon"]
links:
  spec: specs/001-todo-ai-chatbot-spec/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - api/index.py
 - vercel.json
 - requirements.txt
 - backend/requirements.txt
 - backend/setup.py
 - backend/src/services/database.py
 - backend/src/services/auth_service.py
 - README.md
tests:
 - Manual: read-only inspection of Neon DB before any write (empty)
 - Manual: fresh venv install from root requirements.txt (nested -r) PASS
 - Manual: app served via api/index.py against Neon; signup/signin, lists, sub-items, edit, rename, delete item with sub-items, delete list with nested items, 401/403 PASS; test account data then deleted (0 rows left)
 - Manual: local SQLite regression via TestClient PASS; vite build PASS
---

## Prompt

push it on my versal account is https://vercel.com/iqra-awans-projects

## Response snapshot

Asked two decisions: database (user chose Neon from .env) and connection method (user chose Vercel "Import from GitHub"). Verified the Neon DB was empty (read-only) before writing. Added PostgreSQL support (psycopg2-binary pinned in backend/requirements.txt and setup.py; postgres:// normalisation; pool_pre_ping; SQL echo now opt-in via SQL_ECHO), made AUTH_SECRET mandatory with a clear error on read-only hosts, and added Vercel config: api/index.py (imports backend app, ensures tables on cold start), root requirements.txt (-r backend/requirements.txt), vercel.json (frontend build to frontend/dist, function includeFiles backend/**, rewrites /api/* and /health). Tested end to end against Neon via the Vercel entry point, cleaned up the test account, re-verified local SQLite. README gained a "Deploying to Vercel" section. User must import the repo on Vercel and set DATABASE_URL and AUTH_SECRET.

## Outcome

- ✅ Impact: Repo is deployable to Vercel with persistent Neon storage.
- 🧪 Tests: All manual checks PASS.
- 📁 Files: 3 new, 5 modified.
- 🔁 Next prompts: Import on Vercel, add env vars, deploy; verify live URL.
- 🧠 Reflection: Checking the shared Neon DB first ruled out clobbering Phase 2 tables.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): Manual PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Verify live deployment logs after first deploy.
