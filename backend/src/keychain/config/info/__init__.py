"""Application information model."""

__all__ = ["AppInfo"]

from pydantic import BaseModel, Field

from keychain import __version__


class AppInfo(BaseModel):
    """Application information model.

    This model stores basic application metadata including the application name
    and version. Both fields can be configured via environment variable shortcuts
    (APP_NAME and APP_VERSION) or through YAML configuration files.

    Attributes:
        name: The application name. Defaults to "keychain". Can be set via
            the APP_NAME environment variable shortcut.
        version: The application version. Defaults to the package version.
            Can be set via the APP_VERSION environment variable shortcut.

    """

    name: str = Field(default="keychain", description="Application name")
    version: str = Field(default=__version__, description="Application version")
    description: str = Field(default="Keychain Application", description="Application description")
    debug: bool = Field(default=False, description="Debug mode")
