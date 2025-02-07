"""Version 1 of the API."""

from fastapi import APIRouter

from app.routers.v1.actuator import router as actuator_router

router_v1 = APIRouter(prefix="/v1")
router_v1.include_router(actuator_router)
