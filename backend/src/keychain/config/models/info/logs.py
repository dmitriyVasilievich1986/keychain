"""Logs configuration model."""

__all__ = ("LogLevel", "Logs")

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Logs(BaseModel):
    """Logs configuration model.

    This model stores the configuration for the logs including the log level,
    is simple output, and logs folder path.

    Attributes:
        log_level: Log level.
        is_simple_output: Is simple output.
        logs_folder_path: Logs folder path.

    """

    log_level: LogLevel = Field(default="INFO", description="Log level")
    is_simple_output: bool = Field(default=False, description="Is simple output")
    logs_folder_path: Path | None = Field(None, description="Logs folder path")
