"""API v1 router."""

__all__ = ("router",)

from fastapi import APIRouter

from .field import router as field_router
from .password import router as password_router
from .user import router as user_router

router = APIRouter(prefix="/v1")

router.include_router(user_router)
router.include_router(password_router)
router.include_router(field_router)
