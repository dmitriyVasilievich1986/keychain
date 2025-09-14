from collections.abc import Callable
from typing import ParamSpec, TYPE_CHECKING

from keychain.client.web_client.auth.base import AuthBase
from keychain.client.web_client.types import AuthBody, AuthResponse, WebClientCreds
from keychain.config.config import web_client_config

if TYPE_CHECKING:
    from httpx import Response


P = ParamSpec("P")


class WebAuth(AuthBase[AuthResponse]):
    def __init__(self, creds: WebClientCreds) -> None:
        import httpx

        self._token: AuthResponse | None = None
        self.creds = AuthBody.model_validate(creds.model_dump())
        self.client = httpx.Client(base_url=creds.base_url, timeout=creds.timeout)

    def _get_token(self) -> AuthResponse:
        response = self.client.post(
            web_client_config.LOGIN_URL, json=self.creds.model_dump()
        )
        response.raise_for_status()
        self._token = AuthResponse.model_validate(response.json())
        return self.token

    def __call__(self, func: Callable[P, "Response"]) -> Callable[P, "Response"]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> "Response":
            response = func(*args, **kwargs, token=self.token)
            if response.status_code in (401, 403):
                self._token = None
                response = func(*args, **kwargs, token=self.token)
            response.raise_for_status()
            return response

        return wrapper
