# Keychain Backend

A secure RESTful API service for password management built with FastAPI and Python.

## Description

Keychain Backend is a robust password management service that provides encrypted storage and retrieval of passwords. It features JWT-based authentication, encrypted field storage using Fernet symmetric encryption, and a clean RESTful API architecture. The service stores its data in Google Cloud Firestore and includes CLI tooling for user and password administration.

## Tech Stack

- **Python 3.13** - Programming language
- **FastAPI** - Modern web framework for building APIs
- **Google Cloud Firestore** - Document database, accessed through the async client
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
│   │   │       ├── get_firestore.py  # Firestore client dependency
│   │   │       └── authorize_user.py # Authorization dependency
│   │   └── routers/                  # API route handlers
│   │       ├── api/v1/               # API v1 endpoints
│   │       │   ├── user/             # User + login endpoints
│   │       │   └── password/         # Password endpoints (fields are embedded)
│   │       ├── system/               # System endpoints (health, version)
│   │       └── models/               # Request/response models
│   ├── services/                     # Business logic services
│   │   ├── auth/                     # Authentication service
│   │   │   ├── client.py             # JWT token handling
│   │   │   └── models/               # Token models
│   │   ├── cryptography/             # Encryption service
│   │   │   └── client.py             # Fernet encryption client
│   │   ├── db_client/                # Database clients
│   │   │   └── firestore/            # Async Firestore client
│   │   └── daos/                     # Data Access Objects
│   │       └── firestore/            # Firestore DAOs
│   │           ├── base.py           # Base Firestore DAO
│   │           ├── user.py           # User DAO
│   │           ├── password.py       # Password DAO
│   │           └── models/           # Pydantic document models
│   └── utils/                        # Utility modules
│       ├── cli/                      # CLI commands
│       │   ├── main.py               # Main CLI entry point
│       │   ├── db/                   # Data management commands
│       │   │   ├── db.py             # `db` command group
│       │   │   ├── user.py           # User management commands
│       │   │   └── password.py       # Password management commands
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
└── .env                              # Environment variables (secrets)
```

## Data Model

Data is stored as Firestore documents. Document IDs are random UUID4 strings.

### User (`db.users.collection_name`, default `users`)

- `name`: Username (used for login)
- `password_hash`: Hashed password
- `created_at` / `updated_at`: Timestamps

### Password (`db.firestore.collection_name`)

- `name`: Password name/title
- `description`: Optional description
- `image_url`: Optional image URL
- `user_id`: ID of the owning user
- `fields`: Embedded list of fields (see below)
- `created_at` / `updated_at` / `deleted_at`: Timestamps

### Field (embedded in a password)

- `name`: Field name (e.g., "username", "password")
- `position`: Position within the password
- `values`: History of values, each with `value` and `created_at`
- `created_at` / `updated_at` / `deleted_at`: Timestamps

## Getting Started

### Prerequisites

- Python 3.13 or higher
- uv (Python package manager) or pip
- A Google Cloud project with Firestore, or the local Firestore emulator (`gcloud emulators firestore start`)

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
GOOGLE__PROJECT_ID=your_gcp_project_id
GOOGLE__CREDENTIALS_PATH=/path/to/service-account.json  # optional; Application Default Credentials otherwise
```

2. Generate the required keys:

```bash
# Generate a Fernet key for field encryption
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Generate a JWT secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

3. Configure `configurations/local.yaml` as needed. The database section names the
   Firestore database and collections:

```yaml
db:
  firestore:
    db_name: "(default)"
    collection_name: "password"
  users:
    db_name: "(default)"
    collection_name: "users"
```

Firestore needs no migrations: collections are created on first write.

### Using the Firestore emulator

To develop without a GCP project, start the emulator and point the client at it:

```bash
gcloud emulators firestore start --host-port=localhost:8081
export FIRESTORE_EMULATOR_HOST=localhost:8081  # or add it to .env
```

When `FIRESTORE_EMULATOR_HOST` is set, no credentials are needed and nothing reaches GCP.

## Running the Application

### Using the CLI

```bash
# Development mode with auto-reload
keychain run --reload

# Custom host and port
keychain run --host 0.0.0.0 --port 8080
```

Defaults are `--host 0.0.0.0` and `--port 8080`.

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
docker run -p 8080:8080 keychain-backend
```

### Using Docker Compose

From the repository root, a full stack (backend, nginx, optional frontend)
is defined in `docker-compose.yaml`:

```bash
docker compose up --build
```

The API will be available at `http://localhost:8080`

## Available CLI Commands

### Application Commands

```bash
keychain version                 # Show version information
keychain show-config             # Display current configuration
keychain run                     # Start the server
```

### User Management Commands

```bash
keychain db user create-user --username admin           # Prompts for a password
keychain db user get-user --user-id <uuid>              # Or --username admin
keychain db user update-user --user-id <uuid> --username newname
keychain db user delete-user --user-id <uuid>
keychain db user verify-password --user-id <uuid>       # Prompts for a password
keychain db user reset-password --user-id <uuid>        # Prompts for a new password
```

### Password Management Commands

```bash
keychain db password create-password --name "Gmail" --user-id <uuid> --image-url "/static/i/gmail.png"
keychain db password list-passwords --user-id <uuid>
keychain db password get-password --password-id <uuid>
keychain db password update-password --password-id <uuid> --name "Gmail Work"
keychain db password delete-password --password-id <uuid>
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

- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

## API Endpoints

### System Endpoints

```
GET  /health                # Health check (verifies Firestore connectivity)
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

## Usage Examples

### Authentication

```python
import requests

# Login and get access token
response = requests.post("http://localhost:8080/api/v1/user/login", json={"username": "admin", "password": "secret"})
token = response.json()["access_token"]

# Use token for authenticated requests
headers = {"Authorization": f"Bearer {token}"}
```

### Creating a Password with Fields

Fields are embedded in the password; their order defines their position.

```python
response = requests.post(
    "http://localhost:8080/api/v1/password",
    headers=headers,
    json={
        "name": "GitHub",
        "image_url": "/static/i/github.png",
        "fields": [
            {"name": "username", "values": [{"value": "myusername"}]},
            {"name": "password", "values": [{"value": "mypassword123"}]},
        ],
    },
)
password = response.json()
```

### Retrieving Passwords

```python
# Get all passwords for authenticated user
response = requests.get("http://localhost:8080/api/v1/password", headers=headers)
passwords = response.json()

# Get specific password with fields
response = requests.get(f"http://localhost:8080/api/v1/password/{password_id}", headers=headers)
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

Tests run against the Firestore emulator (`FIRESTORE_EMULATOR_HOST`, default `localhost:8081`):

```bash
gcloud emulators firestore start --host-port=localhost:8081
uv run --env-file=.env pytest
```

## Environment Variables

- `CONFIG_FILE_PATH`: Path to YAML configuration file (defaults to `configurations/production.yaml`)
- `CRYPTOGRAPHY__SECRET_KEY`: Fernet encryption key (base64 encoded)
- `AUTH__JWT_SECRET_KEY`: JWT signing secret

Nested configuration values can be set via environment variables using the double
underscore (`__`) delimiter. For example:

- `DB__FIRESTORE__DB_NAME`: Firestore database for passwords
- `DB__FIRESTORE__COLLECTION_NAME`: Firestore collection for passwords
- `DB__USERS__DB_NAME` / `DB__USERS__COLLECTION_NAME`: Firestore database and collection for users
- `GOOGLE__PROJECT_ID`: GCP project that hosts Firestore
- `GOOGLE__CREDENTIALS_PATH`: Service-account JSON (optional)
- `FIRESTORE_EMULATOR_HOST`: `host:port` of a local Firestore emulator (optional)
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
