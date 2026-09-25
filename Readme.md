[![build-backend](https://github.com/dmitriyVasilievich1986/keychain/actions/workflows/build_backend.yml/badge.svg)](https://github.com/dmitriyVasilievich1986/keychain/actions/workflows/build_backend.yml)
[![build-frontend](https://github.com/dmitriyVasilievich1986/keychain/actions/workflows/build_frontend.yml/badge.svg)](https://github.com/dmitriyVasilievich1986/keychain/actions/workflows/build_frontend.yml)
[![test-backend](https://github.com/dmitriyVasilievich1986/keychain/actions/workflows/test_backend.yml/badge.svg)](https://github.com/dmitriyVasilievich1986/keychain/actions/workflows/test_backend.yml)

# Keychain

A modern, secure, self-hosted password manager with encrypted storage.

## Overview

Keychain is a full-stack password manager for storing and managing secrets. It ships a React frontend, a FastAPI backend with Fernet-encrypted fields, and Docker Compose setups for local development and production-style deployment.

### Key Features

- **Encrypted fields** — sensitive values encrypted at rest with Fernet
- **JWT authentication** — token-based auth with configurable expiration
- **Self-hosted** — Docker Compose for local and production-like runs
- **Modern UI** — React + Material UI
- **RESTful API** — OpenAPI docs via FastAPI
- **CLI** — admin tooling for DB, users, passwords, and crypto keys
- **Migrations** — Alembic-managed schema
- **Type-safe** — TypeScript frontend and typed Python backend

## Architecture

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTPS (80/443)
       ↓
┌─────────────────────────────────────────┐
│         Nginx (reverse proxy)           │
│  • Serves static frontend assets        │
│  • Proxies /api/* to backend            │
└────────┬────────────────────┬───────────┘
         │                    │
         ↓                    ↓
┌──────────────┐      ┌──────────────────┐
│   Frontend   │      │     Backend      │
│  React 19    │      │  FastAPI         │
│  TypeScript  │      │  Python 3.13     │
│  Vite+       │      │  SQLAlchemy      │
│  MUI/Zustand │      │  Cryptography    │
└──────────────┘      └────────┬─────────┘
                               ↓
                        ┌──────────────┐
                        │ PostgreSQL   │
                        └──────────────┘
```

## Project Structure

```
keychain/
├── backend/                         # FastAPI app (uv + pyproject.toml)
│   ├── src/keychain/                # Application source
│   ├── configurations/              # YAML configs (local/production/test)
│   ├── Dockerfile
│   └── README.md
├── frontend/                        # React app (Vite+)
│   ├── src/
│   ├── vite.config.ts               # Vite+, lint, fmt, aliases
│   ├── package.json
│   └── README.md
├── nginx/                           # Reverse proxy image + config
├── static/                          # Frontend build output + images
├── db/                              # Postgres data volume (local)
├── docker-compose.yaml              # Production-style stack
├── docker-compose-development.yaml  # Local/dev stack
├── .pre-commit-config.yaml          # Repo-wide git hooks
└── .github/workflows/               # CI
```

## Tech Stack

| Area | Technologies |
| --- | --- |
| Backend | Python 3.13, FastAPI, SQLAlchemy (async), Alembic, Pydantic, PyJWT, Cryptography, Uvicorn |
| Frontend | React 19, TypeScript, Vite+, Oxlint, Oxfmt, MUI, Zustand, React Router, Axios, Sass |
| Infra | Docker Compose, Nginx, PostgreSQL 18 |

## Quick Start (Docker Compose)

### Prerequisites

- Docker and Docker Compose
- Git
- For local frontend builds: Node.js 24 and npm 12.0.1 (see `frontend/package.json` `devEngines`)

### 1. Clone

```bash
git clone https://github.com/dmitriyVasilievich1986/keychain.git
cd keychain
```

### 2. Configure backend secrets

Create `backend/.env` and `backend/db.env` (see examples and details in [backend/README.md](./backend/README.md)).

Minimum `.env` keys:

```bash
CONFIG_FILE_PATH=/opt/backend/configurations/local.yaml
CRYPTOGRAPHY__SECRET_KEY=<fernet-key>
AUTH__JWT_SECRET_KEY=<jwt-secret>
```

Generate keys (Python 3.13):

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install cryptography

# Fernet key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Or use the CLI after installing the package:

```bash
keychain cryptography generate-key
keychain access-token generate-key
```

### 3. Start the stack

**Development** (hot-reload backend; optional frontend profile):

```bash
# Backend + Postgres + Nginx
docker compose -f docker-compose-development.yaml up -d --build

# Also start the Vite+ frontend container
docker compose -f docker-compose-development.yaml --profile frontend up -d --build
```

**Production-style** (pre-built images; no source mounts):

```bash
docker compose -f docker-compose.yaml up -d
```

### 4. Initialize the database

```bash
docker exec -it keychain-backend bash
keychain db upgrade
keychain db-client user create --username admin --email admin@example.com --password yourpassword
exit
```

### 5. Build frontend for Nginx (if not using the frontend profile)

```bash
cd frontend
npm install   # requires npm 12.0.1 (or install it: npm install -g npm@12.0.1)
npm run build # writes into ../static/
```

### 6. Open the app

- App: `http://localhost` (or `https://localhost` when TLS is configured)
- API via Nginx: `http://localhost/api/`
- Backend direct (dev compose): `http://localhost:8000`

## Docker Compose Services

Both compose files run **nginx**, **backend**, and **PostgreSQL**. The development file additionally offers an optional **frontend** service behind the `frontend` profile.

| Service | Role |
| --- | --- |
| `nginx` | Serves `static/` and proxies `/api/*` to the backend |
| `backend` | FastAPI app (`keychain run`, with `--reload` in development) |
| `db` | PostgreSQL 18 |
| `frontend` (dev profile) | Node 24 container running the Vite+ dev workflow via `scripts/start.sh` |

Rebuild examples:

```bash
docker compose -f docker-compose-development.yaml build backend nginx
docker compose -f docker-compose-development.yaml up -d
```

## Local Development (without full Compose frontend)

### Backend

See [backend/README.md](./backend/README.md).

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
keychain db upgrade
keychain run --reload
```

### Frontend

See [frontend/README.md](./frontend/README.md) and [frontend/AGENTS.md](./frontend/AGENTS.md).

The frontend uses **Vite+** (`vp`) for dev, build, lint, and format:

```bash
cd frontend
npm install
npm run dev      # vp dev
npm run lint:all # fmt + lint --fix + typecheck
npm run build    # tsc -b && vp build → ../static/
```

## CLI

```bash
keychain version
keychain run
keychain show-config

keychain db upgrade
keychain db current
keychain db revision -m "message"

keychain db-client user create --username admin --email admin@example.com --password secret
keychain db-client user list
keychain db-client password create --name "Gmail" --user-id 1
keychain db-client field create --name "username" --value "user@example.com" --password-id 1

keychain cryptography generate-key
keychain access-token generate-key
keychain access-token generate 1
```

## API

With the backend running:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

Useful endpoints:

- `POST /api/v1/login`
- `GET /api/v1/user`
- `GET|POST /api/v1/password`
- `GET /api/v1/password/{id}`
- `POST /api/v1/field`
- `GET /health`
- `GET /version`

## Environment Variables

### Backend

```bash
CONFIG_FILE_PATH                     # Path to YAML config
CRYPTOGRAPHY__SECRET_KEY             # Fernet key
AUTH__JWT_SECRET_KEY                 # JWT signing secret
DB__DB_URI                           # Database URL (Postgres in Compose)
AUTH__ACCESS_TOKEN_EXPIRE_MINUTES    # Token TTL (default: 30)
INFO__DEBUG                          # Debug flag
```

Postgres container variables live in `backend/db.env`.

### Frontend

```bash
VITE_API_HOST      # API base URL (empty = relative URLs through Nginx)
VITE_IMAGES_HOST   # Image path prefix (e.g. /static/i)
VITE_SOURCEMAP     # Enable source maps when building/serving
```

## Security

- Field values encrypted at rest (Fernet / AES-128)
- JWT auth with configurable expiration
- User passwords hashed with Werkzeug
- Prefer TLS termination at Nginx (or another reverse proxy) in production
- Do not commit `.env` / `db.env` secrets
- Back up the Postgres volume regularly

## CI

GitHub Actions workflows:

- `build_backend.yml` — backend image/build checks
- `build_frontend.yml` — frontend install + build (uses npm 12.0.1)
- `test_backend.yml` — backend tests
- `auto_bump_version.yml` — version bump automation

Local quality gates use [pre-commit](https://pre-commit.com) (`.pre-commit-config.yaml`): Ruff, Pyright, and frontend `vp fmt` / `vp lint`.

## Contributing

1. Fork and create a feature branch
2. Make changes with tests where appropriate
3. Run pre-commit hooks (or at least backend Ruff/Pyright and frontend `npm run lint:all`)
4. Open a pull request

## License

MIT License — see [LICENSE](./LICENSE).

Copyright (c) 2024–2026 dmitriyvasil@gmail.com

## Author

Dmitriy Vasilievich

- Email: dmitriyvasil@gmail.com
- GitHub: [dmitriyVasilievich1986](https://github.com/dmitriyVasilievich1986)

---

**Note:** Intended for personal or small-team self-hosting. For larger deployments, add hardening, audit logging, and operational controls as needed.
