from typing import Any
from uuid import UUID

from fastapi import APIRouter

from .data_mapper import fromDb
from .model import Builder, User
from .repository import getAll, getByPublicId

router = APIRouter(prefix="/users")


@router.get("/", tags=["users"])
async def read_users() -> list[User]:
    db_users = getAll()

    return list(map(fromDb, db_users))


@router.get("/me", tags=["users"])
async def read_user_me() -> User:
    return Builder().setUsername("Me").build()


@router.get("/{id}", tags=["users"])
async def read_user(id: UUID) -> Any:
    db_user = getByPublicId(id)
    return fromDb(db_user)
