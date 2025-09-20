from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from keychain.config.config import web_client_config

T = TypeVar("T")


class WebClientCreds(BaseModel):
    username: str = Field(..., description="The username for the web client")
    password: str = Field(..., description="The password for the web client")
    host: str = Field(..., description="The host for the web client")
    port: int = Field(..., description="The port for the web client")

    timeout: int = Field(
        web_client_config.timeout,
        description="Timeout for web client requests in seconds",
    )

    @property
    def base_url(self) -> str:
        """Constructs the base URL from the host and port.

        Returns:
            str: The base URL in the format 'http://{host}:{port}'.

        """
        return f"http://{self.host}:{self.port}"


class AuthBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

    username: str = Field(..., description="The username for authentication")
    password: str = Field(..., description="The password for authentication")
    provider: Literal["db"] = Field("db", description="The authentication provider, default is 'db'", init=False)


class AuthResponse(BaseModel):
    access_token: str = Field(..., description="The access token received after authentication")
    token_type: str = Field("bearer", description="The type of the token", init=False)

    @property
    def token(self) -> dict[str, str]:
        """Returns the token as a dictionary suitable for use in authorization headers.

        Returns:
            dict: A dictionary with the authorization header.

        """
        return {"Authorization": f"{self.token_type.capitalize()} {self.access_token}"}


class PasswordResponse(BaseModel, Generic[T]):
    description_columns: dict[Any, Any] = Field(..., description="Mapping of description columns")
    id: int = Field(..., description="ID of the password entry")
    label_columns: dict[str, str] = Field(..., description="Mapping of label columns")
    result: T = Field(..., description="Password entry data")
    show_columns: list[str] = Field(..., description="List of columns")
    show_title: str = Field(..., description="Title of the password list")


class PasswordsListResponse(BaseModel, Generic[T]):
    count: int = Field(..., description="Total number of passwords")
    description_columns: dict[Any, Any] = Field(..., description="Mapping of description columns")
    ids: list[int] = Field(..., description="List of password IDs")
    label_columns: dict[str, str] = Field(..., description="Mapping of label columns")
    list_columns: list[str] = Field(..., description="List of columns")
    list_title: str = Field(..., description="Title of the password list")
    order_columns: list[str] = Field(..., description="Columns used for ordering")
    result: list[T] = Field(..., description="List of password entries")
