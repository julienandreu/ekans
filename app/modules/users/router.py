from typing import Any

from fastapi import APIRouter

router = APIRouter()


@router.get("/users/", tags=["users"])
async def read_users() -> Any:
    return [{"username": "Rick"}, {"username": "Morty"}]


@router.get("/users/me", tags=["users"])
async def read_user_me() -> Any:
    return {"username": "fakecurrentuser"}


@router.get("/users/{username}", tags=["users"])
async def read_user(username: str) -> Any:
    return {"username": username}
