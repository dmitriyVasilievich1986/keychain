from dataclasses import asdict, dataclass
from os import getenv

from keychain.config import APP_HOST, APP_PORT


@dataclass
class CallerProps:
    username: str | None
    password: str | None
    host: str | None
    port: str | None

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        host: str | None = None,
        port: str | None = None,
    ) -> None:
        """
        Initialize the CallerProps object.

        Args:
            username (str, optional): The username. Defaults to None.
            password (str, optional): The password. Defaults to None.
            host (str, optional): The host. Defaults to None.
            port (str, optional): The port. Defaults to None.
        """

        self.username = username or getenv("API_USERNAME")
        self.password = password or getenv("API_PASSWORD")
        self.host = host or APP_HOST
        self.port = port or APP_PORT

    @property
    def url(self) -> str:
        """
        Returns the URL formed by combining the host and port.

        Returns:
            str: The URL formed by combining the host and port.

        Examples:
            >>> caller_props = CallerProps("user", "pass", "localhost", 80)
            >>> caller_props.url
            'http://localhost:80'
        """

        return f"http://{self.host}:{self.port}"

    @property
    def login_url(self) -> str:
        """
        Returns the login URL formed by combining the URL and the login route.

        Returns:
            str: The login URL formed by combining the URL and the login route.

        Examples:
            >>> caller_props = CallerProps("user", "pass", "localhost", 80)
            >>> caller_props.login_url
            'http://localhost:80/login'
        """

        return getenv("LOGIN_URL", f"{self.url}/login")

    @property
    def passwords_api_url(self) -> str:
        """
        Returns the passwords URL formed by combining the URL and the passwords route.

        Returns:
            str: The passwords URL formed by combining the URL and the passwords route.

        Examples:
            >>> caller_props = CallerProps("user", "pass", "localhost", 80)
            >>> caller_props.passwords_api_url
            'http://localhost:80/api/v1/password'
        """

        return getenv("PASSWORDS_API_URL", f"{self.url}/api/v1/password")


@dataclass
class PostData:
    username: str | None
    password: str | None
    csrf_token: str

    def json(self) -> dict[str, str]:
        """
        Returns the JSON representation of the caller_props object.

        Returns:
            dict: A dictionary representing the JSON data.
        """

        return asdict(self)
