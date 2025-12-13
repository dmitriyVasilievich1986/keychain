# Keychain Backend

A secure RESTful API service for password management built with FastAPI and Python.

## Description

Keychain Backend is a robust password management service that provides encrypted storage and retrieval of passwords. It features JWT-based authentication, encrypted field storage using Fernet symmetric encryption, and a clean RESTful API architecture. The service uses SQLite for data persistence and includes comprehensive CLI tooling for database management and administrative tasks.

## Tech Stack

- **Python 3.13** - Programming language
- **FastAPI** - Modern web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **Alembic** - Database migration tool
- **Pydantic** - Data validation using Python type annotations
- **PyJWT** - JSON Web Token authentication
- **Cryptography** - Fernet encryption for sensitive data
- **Uvicorn** - ASGI server
- **Click** - CLI framework
- **Loguru** - Logging library
- **Aiosqlite** - Async SQLite support
- **Ruff** - Fast Python linter and formatter

## Project Structure

```
backend/
├──  src/keychain/
│   ├──  config/                    # Configuration management
│   │   ├──  app_config.py          # Main application configuration
│   │   ├──  auth/                  # Authentication configuration
│   │   ├──  base/                  # Base settings and storage
│   │   ├──  cryptography/          # Encryption configuration
│   │   ├──  db/                    # Database configuration
│   │   └── info/                  # Application info
│   ├──  modules/                   # Application modules
│   │   ├──  app.py                 # FastAPI application factory
│   │   ├──  middlewares/           # Middleware and dependencies
│   │   │   ├──  app_lifespan.py   # Application lifecycle management
│   │   │   └── dependencies/     # Dependency injection
│   │   │       ├──  get_config.py # Configuration dependency
│   │   │       ├──  get_db.py     # Database dependency
│   │   │       └── authorize_user.py # Authorization dependency
│   │   └── routers/              # API route handlers
│   │       ├──  api/v1/           # API v1 endpoints
│   │       │   ├──  user/         # User endpoints
│   │       │   ├──  password/     # Password endpoints
│   │       │   └── field/        # Field endpoints
│   │       ├──  system/           # System endpoints (health, version)
│   │       └── models/           # Request/response models
│   ├──  services/                 # Business logic services
│   │   ├──  alembic/              # Database migrations
│   │   │   ├──  env.py            # Alembic environment
│   │   │   └── versions/         # Migration scripts
│   │   ├──  auth/                 # Authentication service
│   │   │   ├──  client.py         # JWT token handling
│   │   │   └── models/           # Token models
│   │   ├──  cryptography/         # Encryption service
│   │   │   └── client.py         # Fernet encryption client
│   │   ├──  db_client/            # Database client
│   │   │   ├──  client.py         # SQLAlchemy session management
│   │   │   └── models/           # SQLAlchemy models
│   │   │       ├──  user.py       # User model
│   │   │       ├──  password.py   # Password model
│   │   │       └── field.py      # Field model
│   │   └── daos/                 # Data Access Objects
│   │       ├──  user.py           # User DAO
│   │       ├──  password.py       # Password DAO
│   │       └── field.py          # Field DAO
│   └── utils/                    # Utility modules
│       ├──  cli/                  # CLI commands
│       │   ├──  main.py           # Main CLI entry point
│       │   ├──  db.py             # Database commands
│       │   ├──  db_client/        # Database client commands
│       │   ├──  cryptography.py   # Encryption commands
│       │   └── access_token.py   # Token generation commands
│       └── singleton.py          # Singleton pattern utility
├──  configurations/               # Configuration files
│   ├──  local.yaml                # Local development config
│   └── production.yaml           # Production config
├──  Dockerfile                    # Multi-stage Docker build
├──  pyproject.toml                # Project metadata and dependencies
├──  uv.lock                       # Dependency lock file
└── .env                          # Environment variables
```

## Database Schema

### User

- `id`: Primary key
- `username`: Unique username
- `email`: User email
- `password_hash`: Hashed password
- `created_at`: Timestamp
- `passwords`: Relationship to Password model

### Password

- `id`: Primary key
- `name`: Password name/title
- `created_at`: Timestamp
- `image_url`: Optional image URL
- `user_id`: Foreign key to User
- `fields`: Relationship to Field model

### Field

- `id`: Primary key
- `name`: Field name (e.g., "username", "password")
- `value`: Encrypted field value
- `password_id`: Foreign key to Password

## Getting Started

### Prerequisites

- Python 3.13 or higher
- uv (Python package manager) or pip

### Installation with uv (recommended)

1. Install uv if you haven't:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Sync dependencies:

```bash
uv sync
```

3. Activate the virtual environment:

```bash
source .venv/bin/activate
```

### Installation with pip

1. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -e .
```

### Configuration

1. Create a `.env` file in the backend directory:

```bash
CONFIG_FILE_PATH=/path/to/backend/configurations/local.yaml
CRYPTOGRAPHY__SECRET_KEY=your_fernet_key_here
AUTH__JWT_SECRET_KEY=your_jwt_secret_here
```

2. Generate encryption keys:

```bash
# Generate Fernet key for encryption
keychain cryptography generate-key

# Generate JWT secret key
keychain access-token generate-key
```

3. Configure `configurations/local.yaml` as needed (see example in project)

### Database Setup

Initialize the database and run migrations:

```bash
# Create database tables
keychain db upgrade

# Check migration status
keychain db current

# Create a new migration (after model changes)
keychain db revision --autogenerate -m "description"
```

## Running the Application

### Using the CLI

```bash
# Development mode with auto-reload
keychain run --reload

# Production mode
keychain run --host 0.0.0.0 --port 8000

# Custom host and port
keychain run --host 127.0.0.1 --port 8080
```

### Using uvicorn directly

```bash
uvicorn keychain.modules.app:get_app --factory --reload
```

### Using Docker

```bash
# Build the image
docker build -t keychain-backend .

# Run the container
docker run -p 8000:8000 keychain-backend
```

The API will be available at `http://localhost:8000`

## Available CLI Commands

### Application Commands

```bash
keychain version                 # Show version information
keychain show-config             # Display current configuration
keychain run                     # Start the server
```

### Database Commands

```bash
keychain db upgrade              # Run migrations
keychain db downgrade            # Rollback migrations
keychain db current              # Show current revision
keychain db history              # Show migration history
keychain db revision             # Create new migration
```

### Database Client Commands

```bash
# User management
keychain db-client user create --username admin --email admin@example.com --password secret
keychain db-client user list
keychain db-client user get --user-id 1
keychain db-client user delete --user-id 1

# Password management
keychain db-client password create --name "Gmail" --user-id 1
keychain db-client password list --user-id 1
keychain db-client password get --password-id 1
keychain db-client password delete --password-id 1

# Field management
keychain db-client field create --name "username" --value "user@example.com" --password-id 1
keychain db-client field list --password-id 1
keychain db-client field get --field-id 1
keychain db-client field update --field-id 1 --value "newvalue"
keychain db-client field delete --field-id 1
```

### Cryptography Commands

```bash
keychain cryptography generate-key    # Generate a new Fernet encryption key
keychain cryptography encrypt TEXT    # Encrypt text
keychain cryptography decrypt TOKEN   # Decrypt token
```

### Access Token Commands

```bash
keychain access-token generate-key        # Generate JWT secret key
keychain access-token generate USER_ID   # Generate access token for user
keychain access-token decode TOKEN       # Decode and verify token
```

## API Documentation

Once the server is running, interactive API documentation is available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### System Endpoints

```
GET  /health                # Health check
GET  /version               # Version information
```

### Authentication

```
POST /api/v1/login          # User login (returns JWT token)
```

### User Management

```
POST   /api/v1/user         # Create user
GET    /api/v1/user         # Get current user (requires auth)
PATCH  /api/v1/user         # Update user (requires auth)
DELETE /api/v1/user         # Delete user (requires auth)
```

### Password Management

```
POST   /api/v1/password                # Create password (requires auth)
GET    /api/v1/password                # List passwords (requires auth)
GET    /api/v1/password/{password_id}  # Get password details (requires auth)
PATCH  /api/v1/password/{password_id}  # Update password (requires auth)
DELETE /api/v1/password/{password_id}  # Delete password (requires auth)
```

### Field Management

```
POST   /api/v1/field                   # Create field (requires auth)
PATCH  /api/v1/field/{field_id}        # Update field (requires auth)
DELETE /api/v1/field/{field_id}        # Delete field (requires auth)
```

## Usage Examples

### Authentication

```python
import requests

# Login and get access token
response = requests.post(
    "http://localhost:8000/api/v1/login",
    json={"username": "admin", "password": "secret"}
)
token = response.json()["access_token"]

# Use token for authenticated requests
headers = {"Authorization": f"Bearer {token}"}
```

### Creating a Password

```python
# Create a new password entry
response = requests.post(
    "http://localhost:8000/api/v1/password",
    headers=headers,
    json={"name": "GitHub", "image_url": "/static/i/github.png"}
)
password = response.json()
```

### Adding Fields to Password

```python
# Add username field
requests.post(
    "http://localhost:8000/api/v1/field",
    headers=headers,
    json={
        "name": "username",
        "value": "myusername",
        "password_id": password["id"]
    }
)

# Add password field (will be encrypted)
requests.post(
    "http://localhost:8000/api/v1/field",
    headers=headers,
    json={
        "name": "password",
        "value": "mypassword123",
        "password_id": password["id"]
    }
)
```

### Retrieving Passwords

```python
# Get all passwords for authenticated user
response = requests.get(
    "http://localhost:8000/api/v1/password",
    headers=headers
)
passwords = response.json()

# Get specific password with fields
response = requests.get(
    f"http://localhost:8000/api/v1/password/{password_id}",
    headers=headers
)
password_details = response.json()  # Fields are automatically decrypted
```

## Security Features

- **JWT Authentication**: Secure token-based authentication with configurable expiration
- **Password Hashing**: User passwords are hashed using Werkzeug security utilities
- **Field Encryption**: Sensitive field values are encrypted using Fernet symmetric encryption
- **CORS Configuration**: Configurable CORS middleware for cross-origin requests
- **Protected Routes**: Authorization dependency ensures only authenticated users can access protected endpoints

## Development

### Code Quality

```bash
# Run linter
ruff check .

# Run formatter
ruff format .

# Run linter and fix issues
ruff check --fix .
```

### Creating Migrations

After modifying database models:

```bash
# Generate migration
keychain db revision --autogenerate -m "description of changes"

# Review the generated migration in src/keychain/services/alembic/versions/

# Apply migration
keychain db upgrade
```

## Environment Variables

- `CONFIG_FILE_PATH`: Path to YAML configuration file
- `CRYPTOGRAPHY__SECRET_KEY`: Fernet encryption key (base64 encoded)
- `AUTH__JWT_SECRET_KEY`: JWT signing secret

Configuration can also be set via environment variables using double underscore notation:

- `DB__DB_URI`: Database connection string
- `AUTH__ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `INFO__DEBUG`: Enable debug mode

## Docker Support

Multi-stage Dockerfile included for optimized builds:

- **Build stage**: Installs dependencies using uv
- **Development stage**: Includes source code and configurations
- **Production stage**: Optimized runtime image

## License

MIT License - See LICENSE file for details.

## Author

Dmitriy Vasilievich (dmitriyvasil@gmail.com)
