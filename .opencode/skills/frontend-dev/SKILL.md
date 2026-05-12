---
name: frontend-dev
description: Build and maintain the vanilla HTML/CSS/JS frontend for the AI Learning Platform
license: MIT
compatibility: opencode
metadata:
  audience: frontend
  workflow: web
---

## What I do
- Develop and modify static HTML pages (no build step) in `frontend/`
- Manage JS files in `frontend/js/` (api.js, auth.js, app.js)
- Update CSS styles
- Follow API patterns in `frontend/js/api.js` — all API calls go through `api.js`
- Use `localStorage` for auth token and user data

## Key conventions
- **No framework**: vanilla HTML/CSS/JS only
- **API base**: `http://localhost:8000` in `frontend/js/api.js`
- **Auth**: JWT token stored in `localStorage('token')`, auto-attached via `Authorization: Bearer` header
- **Endpoints** are defined as methods on `api` object (e.g. `api.courses.list()`)
- **Login endpoint** uses `application/x-www-form-urlencoded` (not JSON), via `OAuth2PasswordRequestForm`

## When to use me
Use this when working on frontend features, fixing UI bugs, or modifying page behavior.
