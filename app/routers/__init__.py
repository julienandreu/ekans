"""Global routers."""

from fastapi import APIRouter

from app.routers.v1 import router_v1

router = APIRouter(prefix="/api")
router.include_router(router_v1)
