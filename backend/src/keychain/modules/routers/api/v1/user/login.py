"""User login router for issuing access tokens."""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from jwt.exceptions import PyJWTError
from loguru import logger
from sqlalchemy.exc import NoResultFound, SQLAlchemyError

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
    body: Annotated[LoginRequestModel, Body(description="Login request body")],
    db: Annotated[DBClient, Depends(get_db)],
    config: Annotated[AppConfig, Depends(get_config)],
) -> AccessTokenResponseModel:
    """Authenticate a user and issue an access token.

    Args:
        body (LoginRequestModel): The login request containing username and
            password.
        db (DBClient): The database client used to look up the user.
        config (AppConfig): The application config used to build the auth
            client.

    Returns:
        AccessTokenResponseModel: The response containing the access token.

    Raises:
        HTTPException: 404 if the username does not exist, 401 if the password
            is incorrect, or 500 on a database or token encoding error.

    """
    user_dao = UserDAO(db)
    try:
        user = await user_dao.get_by_username(body.username)
    except NoResultFound as e:
        logger.warning(f"User not found: {body.username}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Username or password is incorrect") from e
    except SQLAlchemyError as e:
        logger.exception("Error logging in user", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
        ) from e

    if not user.verify_password(body.password):
        logger.warning(f"Invalid password for user: {body.username}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username or password is incorrect")

    auth_service = AuthClient(config=config)
    try:
        access_token = auth_service.encode_token(str(user.id))
    except (ValueError, PyJWTError) as e:
        logger.exception("Error encoding access token", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred"
        ) from e

    return AccessTokenResponseModel(access_token=access_token.access_token)
