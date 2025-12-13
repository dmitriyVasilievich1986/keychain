"""Base models for the web API."""

from .query import BaseQueryModel
from .request import BaseRequestModel
from .response import BaseResponseModel

__all__ = ("BaseQueryModel", "BaseRequestModel", "BaseResponseModel")
