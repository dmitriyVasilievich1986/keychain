"""Authentication token models."""

__all__ = ["EncodedToken"]

from datetime import datetime

from pydantic import BaseModel, Field


class EncodedToken(BaseModel):
    """Model representing an encoded JWT token.

    This model contains the standard JWT claims that are encoded when
    creating a token, including the subject (typically a user identifier)
    and expiration timestamp.
    """

    access_token: str = Field(..., description="The subject of the token")
    expires_at: datetime = Field(..., description="The expiration time of the token")
