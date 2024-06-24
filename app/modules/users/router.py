from typing import Any

from fastapi import APIRouter

from .data_mapper import fromDb
from .model import Builder, User
from .repository import getAll

router = APIRouter(prefix="/users")


@router.get("/", tags=["users"])
async def read_users() -> list[User]:
    db_users = getAll()

    return list(map(fromDb, db_users))


@router.get("/me", tags=["users"])
async def read_user_me() -> User:
    return Builder().setUsername("Me").build()


@router.get("/{username}", tags=["users"])
async def read_user(username: str) -> Any:
    return Builder().setUsername(username).build()
