from collections.abc import Sequence
from typing import Literal
from uuid import UUID, uuid4

from sqlmodel import Field, Session, SQLModel, select

from app.core.db import engine

from .model import User as UserModel


class UserBase(SQLModel):
    username: str = Field(index=True)
    __tablename__ = "EkansUser"


class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True)
    public_id: str = Field(default=uuid4, index=True)


def create(user: UserModel) -> User:
    with Session(engine) as session:
        db_user = User.model_validate(user)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user


def getAll(offset: int = 0, limit: int = 10) -> Sequence[User]:
    with Session(engine) as session:
        db_users = session.exec(select(User).offset(offset).limit(limit)).all()
        return db_users


def getByPublicId(public_id: UUID) -> User:
    with Session(engine) as session:
        db_user = session.exec(
            select(User).where(User.public_id == public_id).limit(1)
        ).first()
        if not db_user:
            raise Exception("User not found with id '{id}'")
        return db_user


def getByUsername(username: str) -> User:
    with Session(engine) as session:
        db_user = session.get(User, username)
        if not db_user:
            raise Exception("User not found with username '{username}'")
        return db_user


def update(username: str, user: User) -> User:
    with Session(engine) as session:
        db_user = session.get(User, username)
        if not db_user:
            raise Exception("User not found with username '{username}'")
        user_data = user.model_dump(exclude_unset=True)
        for key, value in user_data.items():
            setattr(db_user, key, value)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user


def delete(username: str) -> Literal[True]:
    with Session(engine) as session:
        db_user = session.get(User, username)
        if not db_user:
            raise Exception("User not found with username '{username}'")
        session.delete(db_user)
        session.commit()
        return True
