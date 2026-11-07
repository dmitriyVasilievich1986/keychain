"""Abstract base class for async application commands."""

__all__ = ("BaseCommand",)

from abc import ABC, abstractmethod
from typing import Any


class BaseCommand[ResponseType: Any](ABC):
    """Base class for commands that validate input then produce a response."""

    @abstractmethod
    async def initialize(self, *args, **kwargs) -> None:
        """Initialize the command.

        Args:
            *args (Any): Positional arguments to initialize the command.
            **kwargs (Any): Keyword arguments to initialize the command.

        """
        pass

    @abstractmethod
    async def validate(self, *args, **kwargs) -> None:
        """Validate command arguments before execution.

        Args:
            *args (Any): Positional arguments to validate.
            **kwargs (Any): Keyword arguments to validate.

        Returns:
            None

        """
        pass

    @abstractmethod
    async def execute(self, *args, **kwargs) -> ResponseType:
        """Run the command and return its result.

        Args:
            *args (Any): Positional arguments passed to the command.
            **kwargs (Any): Keyword arguments passed to the command.

        Returns:
            ResponseType: The command result.

        """
        pass
