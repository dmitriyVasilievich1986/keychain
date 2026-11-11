"""Tests for the ``Singleton`` metaclass."""

import time
from collections.abc import Generator
from threading import Barrier, Thread

import pytest

from keychain.utils.singleton import Singleton


@pytest.fixture(autouse=True)
def _clear_singletons(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    """Isolate each test from instances, and a lock left held, by other tests."""
    Singleton._instances.clear()  # noqa: SLF001
    monkeypatch.setattr(Singleton, "_lock", type(Singleton._lock)())  # noqa: SLF001
    yield
    Singleton._instances.clear()  # noqa: SLF001


def test_returns_same_instance() -> None:
    """Repeated calls return the instance created by the first call."""

    class Service(metaclass=Singleton):
        def __init__(self, value: int = 0) -> None:
            self.value = value

    first = Service(1)
    second = Service(2)

    assert first is second
    assert second.value == 1


def test_instances_are_per_class() -> None:
    """Each class using the metaclass gets its own instance."""

    class First(metaclass=Singleton):
        pass

    class Second(metaclass=Singleton):
        pass

    assert First() is not Second()


def test_nested_construction_does_not_deadlock() -> None:
    """A singleton's ``__init__`` may create another singleton."""

    class Inner(metaclass=Singleton):
        pass

    class Outer(metaclass=Singleton):
        def __init__(self) -> None:
            self.inner = Inner()

    # Run in a daemon thread so a regression fails the test instead of hanging the suite.
    result: list[Outer] = []
    worker = Thread(target=lambda: result.append(Outer()), daemon=True)
    worker.start()
    worker.join(timeout=5)

    assert not worker.is_alive(), "nested singleton construction deadlocked"
    assert result[0].inner is Inner()


def test_concurrent_first_calls_create_one_instance() -> None:
    """Threads racing on the first call all receive a single instance."""
    workers = 16
    barrier = Barrier(workers)
    init_calls: list[int] = []

    class Slow(metaclass=Singleton):
        def __init__(self) -> None:
            init_calls.append(1)
            # Widen the race window between the check and the store.
            time.sleep(0.05)

    instances: list[Slow] = []

    def create() -> None:
        barrier.wait()
        instances.append(Slow())

    # Daemon threads with a join timeout, so a stuck lock fails the test instead of hanging the suite.
    threads = [Thread(target=create, daemon=True) for _ in range(workers)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=5)

    assert len(instances) == workers
    assert len(init_calls) == 1
    assert all(instance is instances[0] for instance in instances)


def test_failed_init_is_not_cached() -> None:
    """If ``__init__`` raises, the next call retries construction."""
    attempts: list[int] = []

    class Flaky(metaclass=Singleton):
        def __init__(self) -> None:
            attempts.append(1)
            if len(attempts) == 1:
                raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        Flaky()

    assert Flaky() is Flaky()
    assert len(attempts) == 2
