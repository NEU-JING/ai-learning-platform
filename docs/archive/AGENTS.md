# AGENTS.md - AI Learning Platform

## Quick Start

```bash
# Docker Compose (recommended) - starts all services
docker-compose up -d

# Access points:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000

# Start sandbox (code execution) - requires explicit profile
docker-compose --profile sandbox up -d sandbox

# Local backend development
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
cd backend && pytest ../tests/ -v
```

## Architecture

```
ai-learning-platform/
├── backend/app/           # FastAPI application (main.py, models, services, schemas)
│   ├── data/              # Built-in course data (courses_extended.py loads on startup)
│   ├── services/         # Business logic (user_service, code_executor)
│   └── core/             # Config, database, security
├── frontend/              # Static HTML/JS (no build step required)
├── sandbox/              # Docker-based code execution sandbox
├── tests/                # pytest test suite
├── docker-compose.yml    # Dev environment
└── docker-compose.prod.yml  # Production environment
```

## Key Quirks

- **Sandbox runs on demand**: Use `--profile sandbox` to start code execution service
- **Login is form-data**: Login endpoint `/api/auth/login` expects `application/x-www-form-urlencoded`, not JSON. Use `OAuth2PasswordRequestForm`.
- **CORS open in dev**: `allow_origins=["*"]` in CORS middleware
- **Course data auto-initializes**: Built-in courses load from `courses_extended.py` on backend startup if database is empty
- **SQLAlchemy 2.0 style**: Uses `db.query()` style (older SQLAlchemy), not select() statements

## Database

- PostgreSQL 15 (container: `ai-learning-postgres`)
- Redis 7 (container: `ai-learning-redis`)
- Database auto-creates on first backend startup

## API Endpoints

| Endpoint | Auth | Description |
|----------|------|-------------|
| `POST /api/auth/register` | No | Register (JSON: email, username, password) |
| `POST /api/auth/login` | No | Login (form-data: username=email, password) |
| `GET /api/auth/me` | Yes | Get current user |
| `GET /api/courses` | No | List courses |
| `GET /api/courses/{id}` | No | Course detail |
| `POST /api/code/execute` | Yes | Execute Python code |
| `POST /api/labs/{id}/submit` | Yes | Submit lab solution |

## Dependencies

Backend uses `requirements.txt`. A `venv` exists at `backend/venv/` but is not required - pip install works directly.

## Security Notes

- Code execution sandbox blocks dangerous operations (subprocess, eval, file I/O)
- JWT tokens expire after 15 minutes
- Passwords hashed with bcrypt