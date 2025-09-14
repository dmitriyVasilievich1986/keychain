from typing import Generic, TYPE_CHECKING, TypeVar

from pydantic import BaseModel

from keychain.client.web_client.auth import WebAuth
from keychain.client.web_client.types import (
    AuthResponse,
    PasswordResponse,
    PasswordsListResponse,
    WebClientCreds,
)
from keychain.config.config import web_client_config

if TYPE_CHECKING:
    from httpx import Response


DC = TypeVar("DC", bound=BaseModel)


class WebClient(Generic[DC]):
    def __init__(
        self,
        creds: WebClientCreds,
        transform_cls: type[DC],
        auth: WebAuth | None = None,
    ) -> None:
        import httpx

        self.cls: type[DC] = transform_cls
        self.auth = auth or WebAuth(creds)
        self.client = httpx.Client(base_url=creds.base_url, timeout=creds.timeout)

    def _get_password_raw(
        self, token: AuthResponse, pk: str | int | None = None
    ) -> "Response":
        postfix = "" if pk is None else pk
        return self.client.get(
            f"{web_client_config.PASSWORDS_API_URL}{postfix}", headers=token.token
        )

    def get_password(self, pk: str | int) -> PasswordResponse[DC]:
        response: "Response" = self.auth(self._get_password_raw)(pk=pk)  # type: ignore[call-arg]
        return PasswordResponse[self.cls].model_validate(response.json())  # type: ignore[name-defined]

    def get_passwords_list(self) -> PasswordsListResponse[DC]:
        response: "Response" = self.auth(self._get_password_raw)()  # type: ignore[call-arg]
        return PasswordsListResponse[self.cls].model_validate(response.json())  # type: ignore[name-defined]
