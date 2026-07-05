"""User related endpoints."""

__all__ = ("router",)

from fastapi import APIRouter

from .login import router as login_router
from .user import router as user_router

router = APIRouter(tags=["User Management"])

router.include_router(user_router)
router.include_router(login_router)
