"""Authentication token models.

This module defines data models for handling decoded JWT tokens,
including their claims and expiration information.
"""

__all__ = ["DecodedToken"]

from datetime import datetime

from pydantic import BaseModel, Field


class DecodedToken(BaseModel):
    """Model representing a decoded JWT token.

    This model contains the standard JWT claims that are extracted when
    decoding a token, including the subject (typically a user identifier)
    and expiration timestamp.

    Attributes:
        sub: The subject of the token (typically a user ID or username).
        exp: The expiration time of the token as a Unix timestamp.

    """

    user_id: str = Field(..., description="The subject of the token", alias="sub")
    expires_at: int = Field(..., description="The expiration time of the token", alias="exp")

    @property
    def exp_datetime(self) -> datetime:
        """Convert the expiration timestamp to a datetime object.

        Returns:
            datetime: The expiration time as a datetime object.

        """
        return datetime.fromtimestamp(self.expires_at)
