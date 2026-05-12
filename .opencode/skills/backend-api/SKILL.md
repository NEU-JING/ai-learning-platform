---
name: backend-api
description: Develop and maintain the FastAPI Python backend for the AI Learning Platform
license: MIT
compatibility: opencode
metadata:
  audience: backend
  workflow: api
---

## What I do
- Build and maintain FastAPI endpoints in `backend/app/api/v1/`
- Manage SQLAlchemy models in `backend/app/models/`
- Implement business logic in `backend/app/services/`
- Define Pydantic schemas in `backend/app/schemas/`
- Handle configuration in `backend/app/core/config.py`

## Key conventions
- **SQLAlchemy 2.0 style**: uses `db.query()` style (older SQLAlchemy), not `select()` statements
- **Login endpoint**: `/api/auth/login` expects `application/x-www-form-urlencoded`, uses `OAuth2PasswordRequestForm`
- **Auth**: JWT tokens expire after 15 minutes; passwords hashed with bcrypt
- **CORS**: `allow_origins=["*"]` in dev
- **Course data**: auto-initializes from `backend/app/data/courses_extended.py` on startup if DB empty
- **Code execution**: sandboxed via Docker (`backend/app/services/code_executor.py`), falls back to subprocess
- **Run server**: `cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

## When to use me
Use this when creating new API endpoints, modifying database models, adding services, or fixing backend bugs.
