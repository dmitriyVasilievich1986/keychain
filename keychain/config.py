from base64 import urlsafe_b64encode
from os import getenv
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from flask_appbuilder.security.manager import AUTH_DB

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "passwords.sqlite"
MIGRATIONS_DIR = BASE_DIR / "alembic"
ENV_FILE = BASE_DIR / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)

SQLALCHEMY_TRACK_MODIFICATIONS = False

PASSWORD = getenv("PASSWORD", "secret")
SECRET_KEY = getenv("SECRET_KEY", "secret")
SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
DEBUG = getenv("DEBUG", "False").lower() == "true"

TOKEN = urlsafe_b64encode(str(uuid4()).encode()).decode()

STATIC_URL_PATH = "/static"
TEMPLATE_FOLDER = BASE_DIR / "templates"
STATIC_FOLDER = BASE_DIR.parent / "static"
AUTH_TYPE = AUTH_DB

APP_HOST = getenv("APP_HOST", "0.0.0.0")
APP_PORT = getenv("APP_PORT", "3000")
