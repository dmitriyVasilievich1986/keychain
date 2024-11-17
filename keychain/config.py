from base64 import urlsafe_b64encode
from datetime import timedelta
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

DEBUG = getenv("DEBUG", "False").lower() == "true"
SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
SECRET_KEY = getenv("SECRET_KEY", "secret")
LOG_LEVEL = getenv("LOG_LEVEL", "INFO")

TOKEN = urlsafe_b64encode(str(uuid4()).encode()).decode()
PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

STATIC_FOLDER = BASE_DIR.parent / "static"
TEMPLATE_FOLDER = BASE_DIR / "templates"
STATIC_URL_PATH = "/static"
AUTH_TYPE = AUTH_DB

APP_HOST = getenv("APP_HOST", "0.0.0.0")
APP_PORT = getenv("APP_PORT", "3000")
