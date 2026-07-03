"""Base models for the web API."""

__all__ = ("BaseQueryModel", "BaseRequestModel", "BaseResponseFromModelSchema", "BaseResponseModel")

from .query import BaseQueryModel
from .request import BaseRequestModel
from .response import BaseResponseFromModelSchema, BaseResponseModel
