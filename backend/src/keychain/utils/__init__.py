"""Utility functions and classes."""

from .log_config import configure_logging
from .singleton import Singleton

__all__ = ["Singleton", "configure_logging"]
