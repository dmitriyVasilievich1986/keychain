[![pre-commit](https://github.com/dmitriyVasilievich1986/keychain/actions/workflows/pre_commit.yml/badge.svg)](https://github.com/dmitriyVasilievich1986/keychain/actions/workflows/pre_commit.yml)
[![build-project](https://github.com/dmitriyVasilievich1986/keychain/actions/workflows/build_project.yml/badge.svg)](https://github.com/dmitriyVasilievich1986/keychain/actions/workflows/build_project.yml)

# Keychain

A modern, secure, and self-hosted password management solution with end-to-end encryption.

## Overview

Keychain is a full-stack password manager that provides a secure way to store, manage, and access your passwords. Built with modern web technologies, it features a React-based frontend, a FastAPI backend with encrypted storage, and is designed for easy self-hosting with Docker.

### Key Features

- **Secure Storage**: All sensitive field values are encrypted using Fernet symmetric encryption
- **JWT Authentication**: Token-based authentication with configurable expiration
- **Self-Hosted**: Complete control over your data with Docker deployment
- **Modern UI**: Clean and responsive Material-UI interface
- **RESTful API**: Well-documented API for all operations
- **CLI Tools**: Comprehensive command-line interface for administration
- **Database Migrations**: Version-controlled schema management with Alembic
- **Type-Safe**: TypeScript frontend and Python type hints throughout

## Architecture

The application consists of three main components orchestrated by Docker Compose:

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTP (Port 80)
       ↓
┌─────────────────────────────────────────┐
│            Nginx (Reverse Proxy)         │
│  • Serves static frontend assets        │
│  • Proxies /api/* to backend            │
│  • Handles gzip compression             │
│  • Manages cache headers                │
└────────┬────────────────────┬───────────┘
         │                    │
         │ Static Files       │ API Calls
         ↓                    ↓
┌──────────────┐      ┌──────────────────┐
│   Frontend   │      │     Backend      │
│              │      │                  │
│  React 19    │      │  FastAPI         │
│  TypeScript  │      │  Python 3.13     │
│  MUI         │      │  SQLAlchemy      │
│  Zustand     │      │  Cryptography    │
└──────────────┘      └────────┬─────────┘
                               │
                               ↓
                        ┌──────────────┐
                        │   SQLite DB  │
                        │  (Encrypted) │
                        └──────────────┘
```

## Project Structure

```
keychain/
├── backend/                    # Python FastAPI backend
│   ├── src/keychain/          # Source code
│   │   ├── config/            # Configuration management
│   │   ├── modules/           # FastAPI app and routes
│   │   ├── services/          # Business logic services
│   │   └── utils/             # CLI and utilities
│   ├── configurations/        # YAML config files
│   ├── Dockerfile             # Multi-stage Docker build
│   ├── pyproject.toml         # Python dependencies
│   └── README.md              # Backend documentation
├── frontend/                  # React TypeScript frontend
│   ├── src/                   # Source code
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Page components
│   │   ├── store/             # Zustand state management
│   │   └── utils/             # Utilities and API client
│   ├── package.json           # Node dependencies
│   ├── vite.config.ts         # Vite configuration
│   └── README.md              # Frontend documentation
├── nginx/                     # Nginx configuration
│   └── nginx.conf             # Reverse proxy config
├── static/                    # Static assets and build output
│   ├── assets/                # Frontend build artifacts
│   └── i/                     # Images
├── docker-compose.local.yaml  # Docker Compose configuration
├── .github/workflows/         # CI/CD pipelines
└── README.md                  # This file
```

## Tech Stack

### Backend
- Python 3.13
- FastAPI - Web framework
- SQLAlchemy - ORM
- Alembic - Database migrations
- Pydantic - Data validation
- PyJWT - Authentication
- Cryptography (Fernet) - Encryption
- Uvicorn - ASGI server

### Frontend
- React 19
- TypeScript
- Vite - Build tool
- Material-UI (MUI) - Component library
- Zustand - State management
- React Router - Routing
- Axios - HTTP client
- Sass - Styling

### Infrastructure
- Docker & Docker Compose
- Nginx - Reverse proxy
- SQLite - Database

## Quick Start with Docker Compose

### Prerequisites
- Docker and Docker Compose installed
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/dmitriyVasilievich1986/keychain.git
cd keychain
```

### 2. Configure Backend

Create `.env` file in the `backend/` directory:

```bash
cd backend
```

Create `backend/.env`:
```bash
CONFIG_FILE_PATH=/opt/backend/configurations/local.yaml
CRYPTOGRAPHY__SECRET_KEY=<generate-with-keychain-cryptography-generate-key>
AUTH__JWT_SECRET_KEY=<generate-with-keychain-access-token-generate-key>
```

Generate encryption keys (requires Python 3.13):
```bash
# Install dependencies locally to generate keys
python -m venv .venv
source .venv/bin/activate
pip install cryptography pyjwt

# Generate Fernet key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Generate JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Start the Application

From the root directory:

```bash
# Start backend and nginx only (recommended for production)
docker-compose -f docker-compose.local.yaml up -d

# Or include frontend in development mode
docker-compose -f docker-compose.local.yaml --profile frontend up -d
```

### 4. Initialize Database

```bash
# Access backend container
docker exec -it keychain-backend bash

# Run migrations
keychain db upgrade

# Create first user
keychain db-client user create --username admin --email admin@example.com --password yourpassword

# Exit container
exit
```

### 5. Build Frontend (if not using frontend profile)

```bash
cd frontend
npm install
npm run build  # Outputs to ../static/
```

### 6. Access the Application

Open your browser and navigate to:
```
http://localhost
```

The application is now running with:
- Frontend: Served by Nginx on port 80
- Backend API: `http://localhost/api/`
- Backend direct access: `http://localhost:8000` (if needed)

## Docker Compose Configuration

The `docker-compose.local.yaml` file orchestrates three services:

### Services

#### 1. Nginx (keychain-nginx)
```yaml
ports: 80:80
```
- **Purpose**: Acts as a reverse proxy and static file server
- **Configuration**: `nginx/nginx.conf`
- **Responsibilities**:
  - Serves the React frontend from `/static/`
  - Proxies API requests (`/api/*`) to the backend service
  - Handles gzip compression for better performance
  - Sets cache headers for static assets (1 year for images and JS bundles)
  - Implements SPA routing with `try_files` fallback to `index.html`
- **Volumes**:
  - `./nginx/nginx.conf` → Configuration
  - `./static/` → Frontend build output and static assets

#### 2. Backend (keychain-backend)
```yaml
ports: 8000:8000
```
- **Purpose**: FastAPI application server
- **Build**: Uses multi-stage Dockerfile from `./backend`
- **Environment**:
  - Loads `.env` file for secrets
  - `CONFIG_FILE_PATH`: Points to YAML configuration
- **Volumes** (for development):
  - `./backend/configurations/` → Config files
  - `./backend/src/` → Source code (hot reload)
  - `./backend/keychain.sqlite` → Database persistence
- **Health Check**: Polls `/health` endpoint every 60s
- **Dependencies**: None (starts first)

#### 3. Frontend (keychain-frontend)
```yaml
profile: frontend
```
- **Purpose**: Development build server (optional)
- **Profile**: Only starts when explicitly requested with `--profile frontend`
- **Image**: Node.js 24
- **Environment**:
  - `VITE_API_HOST`: API endpoint (empty = relative URLs)
  - `VITE_IMAGES_HOST`: Image path prefix
- **Command**: Runs `scripts/start.sh` which installs dependencies and starts Vite dev server
- **Volumes**: Mounts source files and configuration for hot reload
- **Note**: In production, build frontend locally and serve via Nginx

### Usage Patterns

**Development** (with hot reload):
```bash
docker-compose -f docker-compose.local.yaml --profile frontend up
```

**Production** (pre-built frontend):
```bash
# Build frontend first
cd frontend && npm run build && cd ..

# Start backend and nginx
docker-compose -f docker-compose.local.yaml up -d
```

**Rebuilding backend**:
```bash
docker-compose -f docker-compose.local.yaml build backend
docker-compose -f docker-compose.local.yaml up -d
```

## Development Setup

### Backend Development

See [backend/README.md](./backend/README.md) for detailed backend setup instructions.

Quick start:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
keychain db upgrade
keychain run --reload
```

### Frontend Development

See [frontend/README.md](./frontend/README.md) for detailed frontend setup instructions.

Quick start:
```bash
cd frontend
npm install
npm run dev
```

## CLI Commands

The backend includes a comprehensive CLI for administration:

```bash
# Application
keychain version                    # Show version
keychain run                        # Start server
keychain show-config                # Display configuration

# Database Management
keychain db upgrade                 # Run migrations
keychain db current                 # Show current version
keychain db revision -m "message"   # Create migration

# User Management
keychain db-client user create --username admin --email admin@example.com --password secret
keychain db-client user list
keychain db-client user get --user-id 1

# Password Management
keychain db-client password create --name "Gmail" --user-id 1
keychain db-client password list --user-id 1

# Field Management
keychain db-client field create --name "username" --value "user@example.com" --password-id 1
keychain db-client field list --password-id 1

# Security
keychain cryptography generate-key  # Generate encryption key
keychain cryptography encrypt TEXT  # Encrypt data
keychain cryptography decrypt TOKEN # Decrypt data
keychain access-token generate-key  # Generate JWT secret
keychain access-token generate 1    # Generate token for user ID
```

## API Documentation

Once the backend is running, interactive API documentation is available at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints

- `POST /api/v1/login` - Authenticate user
- `GET /api/v1/user` - Get current user
- `GET /api/v1/password` - List passwords
- `POST /api/v1/password` - Create password
- `GET /api/v1/password/{id}` - Get password with decrypted fields
- `POST /api/v1/field` - Create encrypted field
- `GET /health` - Health check
- `GET /version` - Version information

## Environment Variables

### Backend
```bash
CONFIG_FILE_PATH            # Path to YAML config
CRYPTOGRAPHY__SECRET_KEY    # Fernet encryption key
AUTH__JWT_SECRET_KEY        # JWT signing secret
DB__DB_URI                  # Database connection string
AUTH__ACCESS_TOKEN_EXPIRE_MINUTES  # Token expiration (default: 30)
INFO__DEBUG                 # Debug mode (true/false)
```

### Frontend
```bash
VITE_API_HOST              # API base URL (empty for relative)
VITE_IMAGES_HOST           # Image path prefix
```

## Security Considerations

- **Encryption**: All sensitive field values are encrypted at rest using Fernet (AES-128)
- **Authentication**: JWT tokens with configurable expiration
- **Password Hashing**: User passwords are hashed using Werkzeug's secure methods
- **HTTPS**: Use a reverse proxy (like Nginx with Let's Encrypt) for production
- **Secrets Management**: Never commit `.env` files or secrets to version control
- **Database**: Keep regular backups of the SQLite database
- **Updates**: Keep dependencies updated for security patches

## Production Deployment

### Recommendations

1. **Use HTTPS**: Configure SSL/TLS certificates (Let's Encrypt)
2. **External Database**: Consider PostgreSQL for production instead of SQLite
3. **Secret Management**: Use secure secret management solutions
4. **Monitoring**: Implement health checks and monitoring
5. **Backups**: Regular automated database backups
6. **Resource Limits**: Set container resource limits in production
7. **Logging**: Configure centralized logging

### Example Production nginx Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Include the rest of nginx.conf...
}
```

## Troubleshooting

### Backend won't start
- Check if `.env` file exists with valid keys
- Verify database migrations are up to date: `docker exec keychain-backend keychain db current`
- Check logs: `docker logs keychain-backend`

### Frontend build fails
- Ensure Node.js 18+ is installed
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check for TypeScript errors: `npm run build`

### API calls fail
- Verify backend is running: `curl http://localhost:8000/health`
- Check nginx configuration is correctly proxying `/api/` requests
- Inspect browser network tab for CORS or 404 errors

### Database errors
- Ensure migrations are applied: `keychain db upgrade`
- Check database file permissions
- Verify `CONFIG_FILE_PATH` points to correct YAML file

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run linters (backend: `ruff`, frontend: `eslint`)
5. Submit a pull request

## CI/CD

The project includes GitHub Actions workflows:

- **pre_commit.yml**: Runs linting and code quality checks
- **build_project.yml**: Builds and tests the application

## License

MIT License - See [LICENSE](./LICENSE) file for details.

Copyright (c) 2024 dmitriyvasil@gmail.com

## Author

Dmitriy Vasilievich
- Email: dmitriyvasil@gmail.com
- GitHub: [dmitriyVasilievich1986](https://github.com/dmitriyVasilievich1986)

## Acknowledgments

Built with modern open-source technologies:
- FastAPI for the elegant Python API framework
- React for the powerful UI library
- Material-UI for the beautiful component library
- Cryptography library for secure encryption

---

**Note**: This is a self-hosted solution intended for personal or small team use. For enterprise deployments, consider additional security hardening, audit logging, and compliance requirements.
