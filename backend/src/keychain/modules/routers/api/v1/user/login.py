"""User related endpoints.

This module provides REST API endpoints for user login operations.
"""

__all__ = ["router"]

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from keychain.config import AppConfig
from keychain.modules.middlewares.dependencies import get_config, get_db
from keychain.modules.routers.models.request.user import (
    LoginRequestModel,
)
from keychain.modules.routers.models.response.user import AccessTokenResponseModel
from keychain.services.auth.client import AuthClient
from keychain.services.daos.user import UserDAO
from keychain.services.db_client.client import DBClient

router = APIRouter(prefix="/user")


@router.post("/login", response_model=AccessTokenResponseModel, description="Login a user")
async def login_user(
    login_model: LoginRequestModel,
    db: Annotated[DBClient, Depends(get_db)],
    config: Annotated[AppConfig, Depends(get_config)],
) -> AccessTokenResponseModel:
    """Login a user.

    Args:
        login_model: LoginRequestModel containing the user's username and password.
        db: Database client dependency for database operations.
        config: Application configuration dependency for authentication settings.

    Returns:
        An AccessTokenResponseModel object containing the access token.

    Raises:
        HTTPException: If the user is not found or validation fails.

        HTTPException: If the password is invalid.

        HTTPException: If the access token cannot be encoded.

        HTTPException: If an unexpected error occurs.

    """
    user_dao = UserDAO(db)
    try:
        user = await user_dao.get_by_username(login_model.username)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error logging in user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e

    if not user.verify_password(login_model.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    auth_service = AuthClient(config=config)
    try:
        access_token = auth_service.encode_token(str(user.id))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error encoding access token: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e

    return AccessTokenResponseModel(access_token=access_token.access_token)
