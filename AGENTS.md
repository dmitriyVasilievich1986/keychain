# Project Agent Instructions

This file describes project-level architecture and workflow rules. Tool-specific and code-style rules live in `backend/AGENTS.md` and `frontend/AGENTS.md`.

## Architecture

- **Backend** (`backend/`): written in Python. It exposes an HTTP API and is the only component that talks to the database.
- **Frontend** (`frontend/`): written in TypeScript + React. It works exclusively through the backend's API and never accesses the database directly.
- **Database**: owned entirely by the backend; nothing outside `backend/` should read from or write to it directly.

## Running the Project

- The project is primarily run via `docker-compose.yaml` (production) and `docker-compose-development.yaml` (development), at the repository root. Use `docker compose -f docker-compose.yaml up` (or the development file) rather than starting backend/frontend services individually, unless working on one service in isolation for local development.
- The compose stack wires together `nginx`, `db`, and `backend`; the frontend is built into static assets served by `nginx` in the production compose file.

## Git Workflow

- Never commit directly to `master` or `development`. All work happens on a feature branch and lands via pull request.
- Branch names must start with one of:
  - `FEATURE/...` — new features or enhancements
  - `BUGFIX/...` — bug fixes
  - `RELEASE/...` — release preparation branches
- Commit messages must follow conventional-commit-style prefixes, e.g. `feat: ...`, `fix: ...`, `chore: ...`, `docs: ...`:
  - First line: short description (`<type>: <short summary>`).
  - If the description alone isn't sufficient, add a blank line followed by a bulleted list of changes, each on its own line.
