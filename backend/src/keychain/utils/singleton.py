"""Thread-safe implementation of Singleton."""

__all__ = ["Singleton"]

from threading import Lock
from typing import ClassVar


class Singleton(type):
    """Thread-safe Singleton metaclass.

    This metaclass ensures that only one instance of a class is created,
    even when accessed from multiple threads. The implementation uses
    a lock to prevent race conditions during instance creation.

    Usage:
        class MyClass(metaclass=Singleton):
            pass

        instance1 = MyClass()
        instance2 = MyClass()
        assert instance1 is instance2  # True

    Attributes:
        _instances: A dictionary mapping classes to their singleton instances.
        _lock: A threading lock used to ensure thread-safe instance creation.

    """

    _instances: ClassVar[dict] = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        """Create or return the existing singleton instance of the class.

        This method is called when the class is instantiated. It checks
        if an instance already exists, and if not, creates one. The check
        and creation are protected by a lock to ensure thread safety.

        Args:
            *args: Positional arguments passed to the class constructor.
            **kwargs: Keyword arguments passed to the class constructor.

        Returns:
            The singleton instance of the class. If an instance already
            exists, it returns that instance; otherwise, it creates
            a new one and stores it for future use.

        """
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance

        return cls._instances[cls]
