"""Abstract base class for async application commands."""

from abc import ABC, abstractmethod
from typing import Any


class BaseCommand[ResponseType: Any](ABC):
    """Base class for commands that validate input then produce a response."""

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
