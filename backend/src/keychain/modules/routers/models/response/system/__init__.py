"""System response models."""

__all__ = ("HealthResponse", "ServiceHealth", "VersionResponse")

from .health import HealthResponse, ServiceHealth
from .version import VersionResponse
