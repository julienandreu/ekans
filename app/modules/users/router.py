from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from . import User, UserDataMapper, UserRepository

router = APIRouter(prefix="/users", tags=["users"])


class CreateUser(BaseModel):
    username: str


@router.get("/", response_model=list[User])
async def read_users(offset: int = 0, limit: int = 10) -> list[User]:
    """
    Retrieve all users.
    """
    db_users = UserRepository.get_all(offset, limit)

    return list(map(UserDataMapper.from_db, db_users))


@router.get("/{id}", response_model=User)
async def read_user(id: UUID) -> User:
    """
    Get a specific user by id.
    """
    db_user = UserRepository.get_by_public_id(id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserDataMapper.from_db(db_user)


@router.delete("/{id}", status_code=204)
async def delete_user(id: UUID) -> None:
    """
    Delete a specific user by id.
    """
    db_user = UserRepository.get_by_public_id(id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    UserRepository.delete(user=db_user)
    return None


@router.post("/", response_model=User, status_code=201)
async def create_user(user_to_create: CreateUser) -> User:
    """
    Create new user.
    """
    try:
        existing_db_user = UserRepository.get_by_username(user_to_create.username)
        if existing_db_user is not None:
            raise HTTPException(status_code=404, detail="User already exists")
    except Exception:
        model_user = User(uuid4(), user_to_create.username)
        db_user = UserRepository.create(UserDataMapper.from_model(model_user))
        return UserDataMapper.from_db(db_user)
