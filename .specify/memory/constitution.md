<!-- SYNC IMPACT REPORT:
Version change: N/A (initial version) → 1.0.0
Modified principles: N/A
Added sections: Full constitution based on Todo AI Chatbot requirements
Removed sections: Template placeholders
Templates requiring updates: N/A (this is the initial constitution)
Follow-up TODOs: None
-->
# Todo AI Chatbot Constitution

## Core Principles

### No Manual Coding by User (Non-Negotiable)
Strict workflow: Specification → Plan → Tasks → Implementation. The user must not manually code; all implementation must be done by Claude Code following the Agentic Dev Stack workflow.

### AI Agent Database Access Restriction
The AI agent must never access the database directly; all task operations must go through MCP tools. This ensures proper separation of concerns and maintains system integrity.

### Stateless Backend Architecture
The backend server must be stateless at all times; conversation state must persist only in the database. For every request: load conversation history from database, append new user message, run AI agent with MCP tools, store assistant response in database, clear all server memory.

### MCP Authority Law
The AI agent is allowed to perform actions only through MCP tools (add_task, list_tasks, update_task, complete_task, delete_task); no direct SQL queries or ORM usage by the agent. MCP tools themselves must also be stateless and persist data in the database.

### Agentic Development Law
Follow the Agentic Dev Stack workflow: Specification First → Plan Before Implementation → Task Decomposition → Implementation via Claude Code. All system behavior, agent logic, tools, APIs, and data models must be specified before implementation.

### Conversation Integrity
Every user and assistant message must be stored in the database; conversations must be resumable after server restarts; each request must be reproducible and testable. This ensures conversation persistence and system reliability.

## System Architecture and Technology Stack
Technology Stack: Frontend: OpenAI ChatKit, Backend: Python FastAPI, AI Framework: OpenAI Agents SDK, MCP Server: Official MCP SDK, ORM: SQLModel, Database: Neon Serverless PostgreSQL, Authentication: Better Auth. The system must be designed so that every architectural decision is explainable and specs, diagrams, and implementation are consistent.

## AI Agent Behavior and Frontend Interaction
AI Agent must understand natural language task commands, select correct MCP tool for each intent, confirm every action with friendly response, handle errors gracefully (e.g., task not found), never hallucinate task IDs or task state. Bonus: If user communicates in Urdu, agent should respond in Urdu. Frontend must communicate only via POST /api/{user_id}/chat and must not contain business logic or tool decisions; is responsible only for displaying the conversation.

## Governance
Process discipline is valued more than speed; no shortcuts will be taken; no pre-built logic will be copied; reviewers can clearly trace User Message → Agent → MCP Tool → Database → Response. All architectural decisions must be explainable and system must be ready for real-world use.

**Version**: 1.0.0 | **Ratified**: 2026-01-17 | **Last Amended**: 2026-01-17