import logging
from datetime import timedelta
from pathlib import Path

from cryptography.fernet import Fernet
from flask_appbuilder.security.manager import AUTH_DB
from pydantic import computed_field, Field, field_validator
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Config(BaseSettings):
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = Field(
        False,
        init=False,
        description="Disable SQLAlchemy event system to save resources",
    )
    static_url_path: str = Field(
        "/static", description="URL path for serving static files", init=False
    )

    DEBUG: bool = Field(False, description="Enable or disable debug mode")
    LOG_LEVEL: str | int = Field(logging.INFO, description="Logging level")
    AUTH_TYPE: int = Field(
        AUTH_DB, description="Authentication type for Flask AppBuilder"
    )
    APP_HOST: str = Field("0.0.0.0", description="Host for the Flask application")
    APP_PORT: int = Field(3000, description="Port for the Flask application")

    PERMANENT_SESSION_LIFETIME: timedelta = Field(
        timedelta(minutes=30), description="Duration of permanent session lifetime"
    )

    BASE_DIR: Path = Field(Path(__file__).parent.parent, init=False)

    @property
    def db_path(self) -> Path:
        return self.BASE_DIR.parent / "passwords.sqlite"

    @computed_field  # type: ignore[prop-decorator]
    @property  # decorators order is matter. do not change it
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """
        Constructs the SQLAlchemy database URI for a SQLite database.

        Returns:
            str: The database URI in the format 'sqlite:///{db_path}', where
            'db_path' is the path to the SQLite database file.
        """

        return f"sqlite:///{self.db_path}"

    @property
    def migrations_dir(self) -> Path:
        """
        Returns the path to the Alembic migrations directory.
        The directory is constructed by joining the BASE_DIR attribute with the "alembic" subdirectory.

        Returns:
            Path: The full path to the Alembic migrations directory.
        """

        return self.BASE_DIR / "alembic"

    @property
    def template_folder(self) -> Path:
        """
        Returns the path to the 'templates' directory within the base directory.

        Returns:
            Path: The full path to the 'templates' folder.
        """

        return self.BASE_DIR / "templates"

    @property
    def static_folder(self) -> Path:
        """
        Returns the path to the 'static' folder located one level above the base directory.

        Returns:
            Path: The path object pointing to the 'static' directory.
        """

        return self.BASE_DIR.parent / "static"

    SECRET_KEY: str = Field(
        ...,
        description="Secret key for session management and other security-related needs",
    )

    @field_validator("SECRET_KEY")
    @classmethod
    def is_correct_secret_key(cls, value: str) -> str:
        """
        Validates whether the provided string is a correct Fernet secret key.
        Attempts to initialize a Fernet instance with the given key. If the key is invalid,
        a ValueError will be raised.

        Args:
            value (str): The secret key to validate.

        Returns:
            str: The validated secret key.

        Raises:
            ValueError: If the provided key is not a valid Fernet key.
        """

        Fernet(value)  # will raise ValueError if the key is invalid
        return value


class WebClientConfig(BaseSettings):
    timeout: int = Field(
        30, description="Timeout for web client requests in seconds", init=False
    )

    PASSWORDS_API_URL: str | None = Field(
        "/api/v1/password/", description="URL for the passwords API"
    )
    LOGIN_URL: str | None = Field(
        "/api/v1/security/login", description="URL for the login page"
    )

    API_USERNAME: str | None = Field(
        None, description="Username for API authentication"
    )
    API_PASSWORD: str | None = Field(
        None, description="Password for API authentication"
    )
