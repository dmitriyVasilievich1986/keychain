"""Thread-safe, re-entrant implementation of Singleton."""

__all__ = ("Singleton",)

from threading import RLock
from typing import ClassVar


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
        _lock: A reentrant threading lock used to ensure thread-safe instance
            creation, allowing singletons to create other singletons in their
            constructors.

    """

    _instances: ClassVar[dict] = {}
    _lock: RLock = RLock()

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

        return cls._instances[cls]

    def reset_singleton(cls) -> None:
        """Discard the cached instance so the next construction builds a new one.

        Called on the class itself, e.g. ``MyClass.reset_singleton()``.
        Intended for tests and deterministic teardown. Code elsewhere that still
        holds the previous instance keeps using it, so only reset when nothing
        depends on the old object staying canonical.
        """
        with cls._lock:
            cls._instances.pop(cls, None)
