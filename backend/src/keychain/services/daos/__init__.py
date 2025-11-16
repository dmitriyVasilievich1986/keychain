"""DAOs for all models."""

from .password import PasswordDAO
from .user import UserDAO

__all__ = ["PasswordDAO", "UserDAO"]
