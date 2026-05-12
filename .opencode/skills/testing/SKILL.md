---
name: testing
description: Run and maintain the pytest test suite for the AI Learning Platform
license: MIT
compatibility: opencode
metadata:
  audience: qa
  workflow: testing
---

## What I do
- Run tests: `cd backend && pytest ../tests/ -v`
- Test files located in `tests/` directory
- Verify backend API, services, and code execution

## Key conventions
- Requires `venv` activated: `source backend/venv/bin/activate`
- Tests are pytest-based, located outside `backend/` at project root `tests/`
- Run `cd backend && pytest ../tests/ -v` (note the `../tests/` path relative to `backend/`)

## When to use me
Use this before submitting changes to ensure nothing is broken, or when debugging failing tests.
