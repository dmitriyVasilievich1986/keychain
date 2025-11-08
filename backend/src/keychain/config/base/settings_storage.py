"""Settings storage with singleton pattern."""

__all__ = ["SettingsStorage"]

from typing import Generic, Optional, TYPE_CHECKING, TypeVar

from keychain.utils.singleton import Singleton

if TYPE_CHECKING:
    from .base import BaseConfig

T = TypeVar("T", bound="BaseConfig")


class SettingsStorage(Generic[T], metaclass=Singleton):
    """A singleton storage for application settings.

    This class provides a thread-safe, singleton-based storage mechanism for
    application configuration settings. It uses the Singleton metaclass to ensure
    only one instance exists throughout the application lifecycle. The stored
    settings can be accessed, set, and deleted through the `settings` property.

    The class is generic and can store any type that extends `BaseConfig`.
    """

    _settings: Optional[T] = None

    @property
    def settings(self) -> Optional[T]:
        """Get the stored settings instance.

        Returns:
            The stored settings instance if set, otherwise None.

        """
        return self._settings

    @settings.setter
    def settings(self, settings: T):
        """Set the settings instance.

        Args:
            settings: The settings instance to store. Must be a subclass of BaseConfig.

        """
        self._settings = settings

    @settings.deleter
    def settings(self):
        """Delete the stored settings instance.

        Clears the stored settings by setting the internal value to None.
        """
        self._settings = None
