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
    def __call__(self, func: Callable[P, "Response"]) -> Callable[P, "Response"]:  # noqa: D102
        raise NotImplementedError

    @property
    def token(self) -> T:
        """Returns the authentication token.

        If the token is not already set, retrieves a new token using the `_get_token` method.
        Otherwise, returns the existing token.

        Returns:
            T: The authentication token.

        """
        if self._token is None:
            return self._get_token()
        return self._token
