# TaskFlow AI — Todo AI Chatbot

Manage your to-dos by chatting. TaskFlow AI turns plain-language messages like
*"Add milk, eggs and bread to Groceries"* into organized lists, items and sub-items,
and keeps a live task board next to the chat.

## Features

- **Chat to manage tasks:** add, list, edit, complete and delete items in plain English.
- **Titled lists:** group items under lists like *Groceries* or *Work*.
- **Sub-items:** put items under other items (*"add fruits in task 1"*), one level deep.
- **Task board:** create, rename, edit, tick off and delete everything with clicks too.
- **Accounts:** sign up and sign in with email and password; each user only sees their own data.
- **MCP tool layer:** the agent changes data only through MCP tools, never directly.
- **Stateless backend:** every request loads what it needs from the database.

## Tech stack

| Part | Technology |
|---|---|
| Frontend | React 18, Vite 4, Axios |
| Backend | Python, FastAPI, Uvicorn |
| Database | SQLite via SQLModel / SQLAlchemy (default) |
| Auth | Email + password (PBKDF2 hashing), JWT sessions via PyJWT |
| Agent | Rule-based intent parser that calls MCP-style tools in `backend/mcp_server` |

## Prerequisites

- **Python 3.11+** (tested with 3.13)
- **Node.js 18+** (tested with 24)
- **Git**

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Iqraawan451512/chatbot.git
cd chatbot
```

### 2. Backend

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment:

| OS / shell | Command |
|---|---|
| Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |
| Windows (Command Prompt) | `.venv\Scripts\activate.bat` |
| macOS / Linux | `source .venv/bin/activate` |

Then install the dependencies:

```bash
pip install -r requirements.txt
```

### 3. Frontend

In a second terminal:

```bash
cd frontend
npm install
```

## Running the app

You need **two terminals**: one for the backend, one for the frontend.

**Terminal 1: backend** (run from the `backend` folder, with the virtual environment active)

```bash
python -m uvicorn main:app --port 8000
```

On first start it creates the SQLite database `backend/todo_chatbot.db` automatically.
Always start it from the `backend` folder, or a new empty database is created wherever you run it.

**Terminal 2: frontend**

```bash
cd frontend
npm run dev
```

Open **http://localhost:3001**, click **Get started free**, create an account, and start chatting.

The frontend dev server forwards every `/api` request to the backend, so the browser never
talks to the backend directly and you don't need any CORS setup.

### If port 8000 is already in use

Run the backend on another port and tell the frontend where it is:

```bash
# Terminal 1 (backend folder)
python -m uvicorn main:app --port 8001
```

```powershell
# Terminal 2 (frontend folder), Windows PowerShell
$env:BACKEND_URL = "http://127.0.0.1:8001"; npm run dev
```

```bash
# Terminal 2 (frontend folder), macOS / Linux
BACKEND_URL=http://127.0.0.1:8001 npm run dev
```

## Configuration

All settings are optional. They are read from **environment variables**; the app does not load a `.env` file.

| Variable | Used by | Default | Purpose |
|---|---|---|---|
| `DATABASE_URL` | backend | `sqlite:///./todo_chatbot.db` | Database connection string (SQLite or PostgreSQL) |
| `AUTH_SECRET` | backend | random, saved to `backend/.auth_secret` | Key that signs sign-in tokens. Required on read-only hosts like Vercel. |
| `SQL_ECHO` | backend | off | Set to `1` to log every SQL statement |
| `PORT` | backend (`python main.py` only) | `8000` | Port when starting with `python main.py` |
| `BACKEND_URL` | frontend dev server | `http://127.0.0.1:8000` | Where `/api` requests are forwarded |
| `VITE_API_URL` | frontend build | same origin | Backend URL for a deployed frontend |

`.env`, `*.db` and `backend/.auth_secret` are git-ignored. Never commit them.

SQLite (local default) and PostgreSQL (tested with Neon) are supported. For PostgreSQL,
set `DATABASE_URL` to a `postgresql://…` connection string; tables are created automatically on start.

## Using the chatbot

Item numbers run across all lists (1, 2, 3, …), sub-items are numbered under their item
(1.1, 1.2, …), and the same numbers appear on the task board.

| You type | What happens |
|---|---|
| `Create a list called Groceries` | Creates an empty list |
| `Create a list called Work with report, call client` | Creates a list with items |
| `Add milk, eggs and bread to Groceries` | Adds several items to a list |
| `Add go to gym` | Adds to your only list, or to **My tasks** |
| `Add fruits in task 1` | Adds a sub-item under item 1 |
| `Show my lists` / `Show Groceries` / `Show completed tasks` | Shows lists and items |
| `Edit task 2 to buy oat milk` / `Edit task 1.1 to apples` | Changes an item or sub-item |
| `Rename Groceries to Shopping` | Renames a list |
| `Mark eggs in Groceries as done` / `Mark task 2 as not done` | Ticks an item off, or reopens it |
| `Delete task 3` / `Delete eggs from Groceries` | Deletes an item (and its sub-items) |
| `Delete the Work list` | Deletes a list and all its items |
| `Clear completed tasks` | Deletes every completed item |
| `Help` | Shows all commands |

If a reference matches nothing or more than one item, the assistant asks which one you mean
instead of guessing.

## API

All `/api/{user_id}/…` routes need an `Authorization: Bearer <token>` header,
and `{user_id}` must be the signed-in user's id.

| Method | Path | Body | Description |
|---|---|---|---|
| `GET` | `/health` | | Health check |
| `POST` | `/api/auth/signup` | `{name, email, password}` | Create an account; returns `{token, user}` |
| `POST` | `/api/auth/signin` | `{email, password}` | Sign in; returns `{token, user}` |
| `GET` | `/api/auth/me` | | Current user |
| `POST` | `/api/{user_id}/chat` | `{message}` | Send a message to the assistant |
| `GET` | `/api/{user_id}/lists` | | Lists with items and sub-items |
| `POST` | `/api/{user_id}/lists` | `{title}` | Create a list |
| `PATCH` | `/api/{user_id}/lists/{list_id}` | `{title}` | Rename a list |
| `DELETE` | `/api/{user_id}/lists/{list_id}` | | Delete a list and its items |
| `GET` | `/api/{user_id}/tasks` | | All items, oldest first |
| `POST` | `/api/{user_id}/tasks` | `{description, list_id?, parent_id?}` | Add an item or sub-item |
| `PATCH` | `/api/{user_id}/tasks/{task_id}` | `{description?, status?}` | Edit, complete (`"completed"`) or reopen (`"incomplete"`) |
| `POST` | `/api/{user_id}/tasks/{task_id}/complete` | | Mark as completed |
| `DELETE` | `/api/{user_id}/tasks/{task_id}` | | Delete an item and its sub-items |

Example:

```bash
# Sign up and keep the token and user id from the response
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name": "Ada", "email": "ada@example.com", "password": "secret123"}'

# Chat (replace USER_ID and TOKEN)
curl -X POST http://localhost:8000/api/USER_ID/chat \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add milk, eggs to Groceries"}'
```

## Deploying to Vercel

The repo deploys as **one Vercel project**: the React frontend is served as static files, and the
FastAPI backend runs as a Python function (`api/index.py`) that handles `/api/*` and `/health`.
`vercel.json` holds the build settings, so nothing needs configuring in the Vercel build settings.

Vercel can't keep files, so the deployed app **must use PostgreSQL** (SQLite data would be lost).

1. Create a PostgreSQL database, for example a free one at [neon.tech](https://neon.tech),
   and copy its connection string (`postgresql://…?sslmode=require`).
2. Generate a sign-in secret:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```
3. On Vercel, click **Add New → Project** and import this GitHub repository.
   Leave **Root Directory** as the repository root and **Framework Preset** as *Other*.
4. Under **Environment Variables**, add:
   | Name | Value |
   |---|---|
   | `DATABASE_URL` | your PostgreSQL connection string |
   | `AUTH_SECRET` | the secret from step 2 |
5. Click **Deploy**. When it finishes, open the URL and create an account.

Every push to `main` redeploys automatically. If you change an environment variable later,
redeploy (**Deployments → ⋯ → Redeploy**) for it to take effect.

## Troubleshooting

| Problem | Fix |
|---|---|
| **"Cannot reach the server"** in the chat | The backend isn't running, or the frontend points at the wrong port. Check Terminal 1 and `BACKEND_URL`. |
| **"Not Found"** when signing in, or for a new feature | The backend is running old code. Stop it (Ctrl+C) and start it again. On Windows, `--reload` can hang mid-reload; a plain restart is more reliable. |
| **`Port 3001 is already in use`** | Another frontend dev server is running. Close it, or run `npx vite --port 3002`. |
| **"Your session has expired"** | Sign in again. Sessions last 7 days, and changing `AUTH_SECRET` signs everyone out. |
| **Tasks disappeared** | The backend was started from a different folder and created a new database. Start it from `backend`. |
| **Vercel: every request fails with a 500 error** | Check that `DATABASE_URL` and `AUTH_SECRET` are set in the Vercel project, then redeploy. The function logs (**Deployments → your deployment → Functions**) show the exact error. |

## Project structure

```
api/index.py                 # Vercel entry point that runs the backend
vercel.json                  # Vercel build settings and /api routing
requirements.txt             # Python packages (backend/requirements.txt points here)

backend/
├── main.py                  # FastAPI app: CORS, routers, startup migration
├── requirements.txt
├── mcp_server/
│   ├── server.py            # Tool registry used by the agent and REST routes
│   └── tools/               # add/list/update/complete/delete tasks, list tools
└── src/
    ├── agents/todo_agent.py # Chat intent parsing and responses
    ├── api/                 # auth, chat, lists, tasks routes
    ├── models/              # User, TodoList, TodoTask, Conversation, Message
    └── services/            # database, auth, conversation helpers

frontend/
├── index.html
├── vite.config.js           # Dev server on 3001, /api proxy to BACKEND_URL
└── src/
    ├── pages/               # LandingPage, AuthPage, ChatPage
    ├── components/          # ChatInterface, TodoList (lists, items, sub-items)
    ├── services/apiClient.js
    └── App.css

specs/001-todo-ai-chatbot-spec/   # Spec, plan and tasks (Spec-Driven Development)
history/prompts/                  # Prompt History Records
```

## Development notes

This project uses Spec-Driven Development with SpecKit Plus (`/sp.*` commands).
Those commands find the current feature from the branch name. On `main`, point them at the
existing feature first:

```powershell
$env:SPECIFY_FEATURE = "001-todo-ai-chatbot-spec"
```

Project principles live in `.specify/memory/constitution.md`.
