# Keychain Backend

A secure RESTful API service for password management built with FastAPI and Python.

## Description

Keychain Backend is a robust password management service that provides encrypted storage and retrieval of passwords. It features JWT-based authentication, encrypted field storage using Fernet symmetric encryption, and a clean RESTful API architecture. The service uses PostgreSQL for data persistence and includes comprehensive CLI tooling for database management and administrative tasks.

## Tech Stack

- **Python 3.13** - Programming language
- **FastAPI** - Modern web framework for building APIs
- **SQLAlchemy** (async) - SQL toolkit and ORM
- **Alembic** - Database migration tool
- **PostgreSQL** - Primary database, accessed asynchronously via **asyncpg**
- **Pydantic / pydantic-settings** - Data validation and settings management
- **PyJWT** - JSON Web Token authentication
- **Cryptography** - Fernet encryption for sensitive data
- **Werkzeug** - Password hashing utilities
- **Uvicorn** - ASGI server
- **AsyncClick** - Async CLI framework
- **Loguru** - Logging library
- **Ruff** - Fast Python linter and formatter

## Project Structure

```
backend/
├── src/keychain/
│   ├── config/                       # Configuration management
│   │   ├── app_config.py             # Main application configuration
│   │   ├── auth/                     # Authentication configuration
│   │   ├── base/                     # Base settings and settings storage
│   │   ├── cryptography/             # Encryption configuration
│   │   ├── db/                       # Database configuration
│   │   └── info/                     # Application info (name, version, API/CORS)
│   ├── modules/                      # Application modules
│   │   ├── app.py                    # FastAPI application factory
│   │   ├── middlewares/              # Middleware and dependencies
│   │   │   ├── app_lifespan.py       # Application lifecycle management
│   │   │   └── dependencies/         # Dependency injection
│   │   │       ├── get_config.py     # Configuration dependency
│   │   │       ├── get_db.py         # Database dependency
│   │   │       └── authorize_user.py # Authorization dependency
│   │   └── routers/                  # API route handlers
│   │       ├── api/v1/               # API v1 endpoints
│   │       │   ├── user/             # User + login endpoints
│   │       │   ├── password/         # Password endpoints
│   │       │   └── field/            # Field endpoints
│   │       ├── system/               # System endpoints (health, version)
│   │       └── models/               # Request/response models
│   ├── services/                     # Business logic services
│   │   ├── alembic/                  # Database migrations
│   │   │   ├── env.py                # Alembic environment
│   │   │   └── versions/             # Migration scripts
│   │   ├── auth/                     # Authentication service
│   │   │   ├── client.py             # JWT token handling
│   │   │   └── models/               # Token models
│   │   ├── cryptography/             # Encryption service
│   │   │   └── client.py             # Fernet encryption client
│   │   ├── db_client/                # Database client
│   │   │   ├── client.py             # SQLAlchemy async session management
│   │   │   └── models/               # SQLAlchemy models
│   │   │       ├── base.py           # Declarative base
│   │   │       ├── user.py           # User model
│   │   │       ├── password.py       # Password model
│   │   │       └── field.py          # Field model
│   │   └── daos/                     # Data Access Objects
│   │       ├── base/                 # Base DAO and shared types
│   │       ├── user.py               # User DAO
│   │       ├── password.py           # Password DAO
│   │       └── field.py              # Field DAO
│   └── utils/                        # Utility modules
│       ├── cli/                      # CLI commands
│       │   ├── main.py               # Main CLI entry point
│       │   ├── db/                   # Database + data management commands
│       │   │   ├── db.py             # Migration commands (upgrade/downgrade/current)
│       │   │   ├── user.py           # User management commands
│       │   │   ├── password.py       # Password management commands
│       │   │   └── field.py          # Field management commands
│       │   ├── cryptography.py       # Encryption commands
│       │   └── access_token.py       # Token generation commands
│       ├── singleton.py              # Singleton pattern utility
│       └── filter.py                 # Query filter parsing utility
├── configurations/                   # Configuration files
│   ├── local.yaml                    # Local development config
│   ├── production.yaml               # Production config
│   └── test.yaml                     # Test config
├── Dockerfile                        # Multi-stage Docker build
├── pyproject.toml                    # Project metadata and dependencies
├── uv.lock                           # Dependency lock file
├── .env                              # Environment variables (secrets)
└── db.env                            # PostgreSQL container environment variables
```

## Database Schema

### User

- `id`: Primary key
- `name`: Username (used for login)
- `password_hash`: Hashed password
- `created_at`: Timestamp
- `passwords`: Relationship to Password model

### Password

- `id`: Primary key
- `name`: Password name/title
- `created_at`: Timestamp
- `image_url`: Optional image URL (defaults to `/static/i/no-photo.png`)
- `user_id`: Foreign key to User
- `fields`: Relationship to Field model

### Field

- `id`: Primary key
- `name`: Field name (e.g., "username", "password")
- `value`: Encrypted field value
- `created_at`: Timestamp
- `is_deleted`: Soft-delete flag
- `password_id`: Foreign key to Password

## Getting Started

### Prerequisites

- Python 3.13 or higher
- uv (Python package manager) or pip
- A running PostgreSQL instance (or use the provided Docker Compose setup)

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
DB__USER=your_db_user
DB__PASSWORD=your_db_password
```

2. Generate the required keys:

```bash
# Generate a Fernet key for field encryption
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Generate a JWT secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

3. Configure `configurations/local.yaml` as needed. The database section selects the
   PostgreSQL provider and connection details:

```yaml
db:
  alembic_ini_path: src/keychain/services/alembic/alembic.ini
  provider: postgresql
  host: db
  port: 5432
  name: keychain_local
```

Credentials (`DB__USER` / `DB__PASSWORD`) are supplied via environment variables.

### Database Setup

Apply migrations to create the schema:

```bash
# Upgrade to the latest revision
keychain db upgrade

# Check the current revision
keychain db current

# Roll back one revision
keychain db downgrade --revision -1
```

> Note: Creating new migrations is done with Alembic directly (see [Creating Migrations](#creating-migrations)).

## Running the Application

### Using the CLI

```bash
# Development mode with auto-reload
keychain run --reload

# Custom host and port
keychain run --host 0.0.0.0 --port 8000
```

Defaults are `--host 0.0.0.0` and `--port 8000`.

### Using uvicorn directly

```bash
uvicorn keychain.modules.app:get_app --factory --reload
```

### Using Docker

The provided multi-stage `Dockerfile` can be built directly:

```bash
# Build the image
docker build -t keychain-backend .

# Run the container
docker run -p 8000:8000 keychain-backend
```

### Using Docker Compose

From the repository root, a full stack (PostgreSQL, backend, nginx, optional frontend)
is defined in `docker-compose.yaml`:

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`

## Available CLI Commands

### Application Commands

```bash
keychain version                 # Show version information
keychain show-config             # Display current configuration
keychain run                     # Start the server
```

### Database Migration Commands

```bash
keychain db upgrade                       # Upgrade to the latest revision (default: head)
keychain db upgrade --revision <rev>      # Upgrade to a specific revision
keychain db downgrade --revision -1       # Roll back one revision
keychain db current                       # Show the current revision
```

### User Management Commands

```bash
keychain db user create-user --username admin           # Prompts for a password
keychain db user get-user --user-id 1                   # Or --username admin
keychain db user update-user --user-id 1 --username newname
keychain db user delete-user --user-id 1
keychain db user verify-password --user-id 1            # Prompts for a password
keychain db user reset-password --user-id 1            # Prompts for a new password
```

### Password Management Commands

```bash
keychain db password create-password --name "Gmail" --user-id 1 --image-url "/static/i/gmail.png"
keychain db password list-passwords --user-id 1
keychain db password get-password --password-id 1
keychain db password update-password --password-id 1 --name "Gmail Work"
keychain db password delete-password --password-id 1
```

### Field Management Commands

```bash
keychain db field create-field --name "username" --password-id 1   # Prompts for the value
keychain db field list-fields --user-id 1
keychain db field get-field --field-id 1
keychain db field update-field --field-id 1                        # Prompts for the new value
keychain db field delete-field --field-id 1
```

### Cryptography Commands

```bash
keychain cryptography encrypt --string TEXT    # Encrypt a string
keychain cryptography decrypt --string TOKEN   # Decrypt a token
```

### Access Token Commands

```bash
keychain access-token generate-access-token --user-id 1   # Generate an access token for a user
keychain access-token decode-access-token --token TOKEN   # Decode and verify a token
```

## API Documentation

Once the server is running, interactive API documentation is available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### System Endpoints

```
GET  /health                # Health check (verifies database connectivity)
GET  /version               # Version information
```

### Authentication

```
POST /api/v1/user/login     # User login (returns JWT token)
```

### User Management

```
GET    /api/v1/user/me      # Get current user (requires auth)
PUT    /api/v1/user         # Update current user (requires auth)
```

### Password Management

```
GET    /api/v1/password                # List passwords (requires auth)
GET    /api/v1/password/{password_id}  # Get password details (requires auth)
POST   /api/v1/password                # Create password (requires auth)
PUT    /api/v1/password/{password_id}  # Replace password (requires auth)
PATCH  /api/v1/password/{password_id}  # Partially update password (requires auth)
DELETE /api/v1/password/{password_id}  # Delete password (requires auth)
```

### Field Management

```
GET    /api/v1/field                   # List fields (requires auth)
GET    /api/v1/field/{field_id}        # Get field details (requires auth)
POST   /api/v1/field                   # Create field (requires auth)
PUT    /api/v1/field/{field_id}        # Update field (requires auth)
DELETE /api/v1/field/{field_id}        # Delete field (requires auth)
```

## Usage Examples

### Authentication

```python
import requests

# Login and get access token
response = requests.post(
    "http://localhost:8000/api/v1/user/login",
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
password_details = response.json()  # Field values are returned decrypted
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

### Testing

```bash
# Run the test suite (pytest is configured in pyproject.toml)
pytest
```

### Creating Migrations

After modifying database models, generate a new migration with Alembic directly:

```bash
# Generate migration
alembic -c src/keychain/services/alembic/alembic.ini revision --autogenerate -m "description of changes"

# Review the generated migration in src/keychain/services/alembic/versions/

# Apply migration
keychain db upgrade
```

## Environment Variables

- `CONFIG_FILE_PATH`: Path to YAML configuration file (defaults to `configurations/production.yaml`)
- `CRYPTOGRAPHY__SECRET_KEY`: Fernet encryption key (base64 encoded)
- `AUTH__JWT_SECRET_KEY`: JWT signing secret

Nested configuration values can be set via environment variables using the double
underscore (`__`) delimiter. For example:

- `DB__PROVIDER`: Database provider (`postgresql`)
- `DB__HOST`: Database host
- `DB__PORT`: Database port
- `DB__NAME`: Database name
- `DB__USER`: Database user
- `DB__PASSWORD`: Database password
- `AUTH__ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (minutes)
- `INFO__DEBUG`: Enable debug mode

## Docker Support

A multi-stage `Dockerfile` is included for optimized builds:

- **Build stage**: Installs dependencies using uv
- **Development stage**: Includes source code and configurations
- **Production stage**: Optimized runtime image

## License

MIT License - See LICENSE file for details.

## Author

Dmitriy Vasilievich (dmitriyvasil@gmail.com)
