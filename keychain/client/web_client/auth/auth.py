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
        """Initializes the authentication client with provided credentials.

        Args:
            creds (WebClientCreds): The credentials required for authentication, including base URL and timeout.

        Attributes:
            _token (AuthResponse | None): Stores the authentication token after successful login.
            creds (AuthBody): Validated credentials for authentication.
            client (httpx.Client): HTTP client configured with base URL and timeout from credentials.

        """
        import httpx

        self._token: AuthResponse | None = None
        self.creds = AuthBody.model_validate(creds.model_dump())
        self.client = httpx.Client(base_url=creds.base_url, timeout=creds.timeout)

    def _get_token(self) -> AuthResponse:
        """Authenticates the client by sending credentials to the login URL and retrieves an authentication token.

        Sends a POST request with the client's credentials to the configured login endpoint.
        Raises an exception if the response status indicates an error.
        Validates and stores the authentication token from the response.

        Returns:
            AuthResponse: The validated authentication token.

        """
        response = self.client.post(web_client_config.LOGIN_URL, json=self.creds.model_dump())
        response.raise_for_status()
        self._token = AuthResponse.model_validate(response.json())
        return self.token

    def __call__(self, func: Callable[P, "Response"]) -> Callable[P, "Response"]:
        """Decorator that injects an authentication token into the decorated function call.

        If the response status code indicates unauthorized (401) or forbidden (403),
        the token is reset and the function is retried with a refreshed token.

        Args:
            func (Callable[P, "Response"]): The function to be decorated, which should accept a 'token' keyword argument.

        Returns:
            Callable[P, "Response"]: The wrapped function that handles token injection and automatic retry on authentication failure.

        """

        def wrapper(*args: P.args, **kwargs: P.kwargs) -> "Response":
            response = func(*args, **kwargs, token=self.token)  # type: ignore[arg-type]
            if response.status_code in (401, 403):
                self._token = None
                response = func(*args, **kwargs, token=self.token)  # type: ignore[arg-type]
            response.raise_for_status()
            return response

        return wrapper
