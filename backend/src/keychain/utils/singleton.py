"""Thread-safe, re-entrant implementation of Singleton."""

__all__ = ["Singleton"]

from threading import RLock
from typing import Any, ClassVar


class Singleton(type):
    """Thread-safe, re-entrant Singleton metaclass.

    This metaclass ensures that only one instance of a class is created,
    even when accessed from multiple threads. Once the instance exists it is
    returned without taking the lock.

    The lock is re-entrant, so the ``__init__`` of one singleton may create
    another singleton (e.g. a client that loads ``AppConfig`` through
    ``SettingsStorage``) without deadlocking.

    It is also safe to use from asyncio code: construction is synchronous, so
    there is no await point between the existence check and the store.

    Usage:
        class MyClass(metaclass=Singleton):
            pass

        instance1 = MyClass()
        instance2 = MyClass()
        assert instance1 is instance2  # True

    Attributes:
        _instances: A dictionary mapping classes to their singleton instances.
        _lock: A re-entrant lock that serialises first-time instance creation.

    """

    _instances: ClassVar[dict[type, Any]] = {}
    _lock: ClassVar[RLock] = RLock()

    def __call__(cls, *args, **kwargs):
        """Create or return the existing singleton instance of the class.

        This method is called when the class is instantiated. If an instance
        already exists it is returned immediately. Otherwise, the instance is
        created under the lock, re-checking first so that concurrent callers
        never create a second one.

        Args:
            *args: Positional arguments passed to the class constructor.
            **kwargs: Keyword arguments passed to the class constructor.
                Both are ignored once the instance exists.

        Returns:
            The singleton instance of the class.

        """
        # Fast path: no locking once the instance exists.
        if (instance := Singleton._instances.get(cls)) is not None:
            return instance

        with Singleton._lock:
            if cls not in Singleton._instances:
                Singleton._instances[cls] = super().__call__(*args, **kwargs)

        return Singleton._instances[cls]
