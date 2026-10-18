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

    """

    project_id: str = Field(..., description="The project ID")
    credentials_path: Path = Field(..., description="The path to the credentials file")

    @cached_property
    def credentials(self) -> Credentials:
        """Get the credentials for the Google API."""
        creds, _ = load_credentials_from_file(str(self.credentials_path))
        return creds
