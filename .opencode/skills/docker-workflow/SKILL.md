---
name: docker-workflow
description: Manage Docker Compose services and sandbox container for the AI Learning Platform
license: MIT
compatibility: opencode
metadata:
  audience: devops
  workflow: docker
---

## What I do
- Start/stop all services via `docker-compose up -d` / `docker-compose down`
- Start sandbox container: `docker-compose --profile sandbox up -d sandbox`
- Build sandbox image: handled by backend's `ensure_sandbox_image()` in `code_executor.py`
- Manage infrastructure containers: PostgreSQL 15 (`ai-learning-postgres`), Redis 7 (`ai-learning-redis`)

## Key services
| Service | Access |
|---------|--------|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

## Key conventions
- **Production**: uses `docker-compose.prod.yml`
- **Sandbox**: requires explicit `--profile sandbox` flag (not started by default)
- **Container names**: follow `ai-learning-*` prefix convention

## When to use me
Use this when setting up the development environment, troubleshooting Docker issues, or managing deployments.
