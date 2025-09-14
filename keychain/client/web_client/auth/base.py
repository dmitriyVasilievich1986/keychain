from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import (
    Generic,
    ParamSpec,
    TYPE_CHECKING,
    TypeVar,
)

if TYPE_CHECKING:
    from httpx import Response

P = ParamSpec("P")
T = TypeVar("T")


class AuthBase(ABC, Generic[T]):
    _token: T | None

    @abstractmethod
    def _get_token(self) -> T:
        raise NotImplementedError

    @abstractmethod
    def __call__(self, func: Callable[P, "Response"]) -> Callable[P, "Response"]:
        raise NotImplementedError

    @property
    def token(self) -> T:
        if self._token is None:
            return self._get_token()
        return self._token
