"""Google configuration settings."""

__all__ = ("GoogleConfig",)

from functools import cached_property
from pathlib import Path

from google.auth import load_credentials_from_file
from google.auth.credentials import Credentials
from pydantic import BaseModel, Field


class GoogleConfig(BaseModel):
    """Google configuration model.

    This model stores the Google configuration settings including the project ID and credentials path.
    Without a credentials path, the client falls back to Application Default Credentials, or to
    anonymous credentials when ``FIRESTORE_EMULATOR_HOST`` is set.

    """

    project_id: str = Field(..., description="The project ID")
    credentials_path: Path | None = Field(None, description="The path to the credentials file")

    @cached_property
    def credentials(self) -> Credentials | None:
        """Get the credentials for the Google API.

        Returns:
            Credentials | None: Credentials loaded from ``credentials_path``,
                or None when no path is configured.

        """
        if self.credentials_path is None:
            return None
        creds, _ = load_credentials_from_file(str(self.credentials_path))
        return creds
