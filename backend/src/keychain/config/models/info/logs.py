"""Logs configuration model."""

__all__ = ("Logs",)

from pathlib import Path

from pydantic import BaseModel, Field


class Logs(BaseModel):
    """Logs configuration model.

    This model stores the configuration for the logs including the log level,
    is simple output, and logs folder path.

    Attributes:
        log_level: Log level.
        is_simple_output: Is simple output.
        logs_folder_path: Logs folder path.

    """

    log_level: str = Field(default="INFO", description="Log level")
    is_simple_output: bool = Field(default=False, description="Is simple output")
    logs_folder_path: Path | None = Field(None, description="Logs folder path")
