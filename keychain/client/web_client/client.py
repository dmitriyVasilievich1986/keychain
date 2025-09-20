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
        """Initializes the web client.

        Args:
            creds (WebClientCreds): Credentials and configuration for the web client.
            transform_cls (type[DC]): The data class type used for response transformation.
            auth (WebAuth | None, optional): Optional authentication object. If not provided, a new WebAuth is created using creds.

        Attributes:
            cls (type[DC]): The data class type for response transformation.
            auth (WebAuth): The authentication object.
            client (httpx.Client): The HTTP client instance configured with base URL and timeout from creds.

        """
        import httpx

        self.cls: type[DC] = transform_cls
        self.auth = auth or WebAuth(creds)
        self.client = httpx.Client(base_url=creds.base_url, timeout=creds.timeout)

    def _get_password_raw(self, token: AuthResponse, pk: str | int | None = None) -> "Response":
        """Retrieves the raw password data from the API using the provided authentication token and optional primary key.

        Args:
            token (AuthResponse): The authentication token to be used in the request headers.
            pk (str | int | None, optional): The primary key of the password entry to retrieve. If None, retrieves all passwords.

        Returns:
            Response: The response object containing the password data from the API.

        """
        postfix = "" if pk is None else pk
        return self.client.get(f"{web_client_config.PASSWORDS_API_URL}{postfix}", headers=token.token)

    def get_password(self, pk: str | int) -> PasswordResponse[DC]:
        """Retrieves a password entry by its primary key.

        Args:
            pk (str | int): The primary key of the password entry to retrieve.

        Returns:
            PasswordResponse[DC]: A validated response object containing the password data.

        Raises:
            ValidationError: If the response data cannot be validated against the expected model.
            AuthenticationError: If authentication fails during the request.
            RequestException: If there is an error during the HTTP request.

        """
        response: "Response" = self.auth(self._get_password_raw)(pk=pk)  # type: ignore[call-arg]
        return PasswordResponse[self.cls].model_validate(response.json())  # type: ignore[name-defined]

    def get_passwords_list(self) -> PasswordsListResponse[DC]:
        """Retrieves a list of passwords from the server.

        Returns:
            PasswordsListResponse[DC]: A validated response object containing the list of passwords.

        Raises:
            ValidationError: If the response data cannot be validated against the PasswordsListResponse model.

        """
        response: "Response" = self.auth(self._get_password_raw)()  # type: ignore[call-arg]
        return PasswordsListResponse[self.cls].model_validate(response.json())  # type: ignore[name-defined]
