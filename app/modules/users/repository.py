from collections.abc import Sequence
from typing import Literal
from uuid import UUID, uuid4

from sqlmodel import Field, Session, SQLModel, select

from app.core.db import engine


class UserBase(SQLModel):
    username: str = Field(index=True)
    __tablename__ = "EkansUser"


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    public_id: str = Field(default=uuid4, index=True)


class UserRepository:
    @staticmethod
    def create(db_user: User) -> User:
        with Session(engine) as session:
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            return db_user

    @staticmethod
    def get_all(offset: int = 0, limit: int = 10) -> Sequence[User]:
        with Session(engine) as session:
            db_users = session.exec(select(User).offset(offset).limit(limit)).all()
            return db_users

    @staticmethod
    def get_one(id: int) -> User:
        with Session(engine) as session:
            db_user = session.get(User, id)
            if not db_user:
                raise Exception("User not found with id '{id}'")
            return db_user

    @staticmethod
    def get_by_public_id(public_id: UUID) -> User:
        with Session(engine) as session:
            db_user = session.exec(
                select(User).where(User.public_id == public_id).limit(1)
            ).first()
            if not db_user:
                raise Exception("User not found with public id '{id}'")
            return db_user

    @staticmethod
    def get_by_username(username: str) -> User:
        with Session(engine) as session:
            db_user = session.exec(
                select(User).where(User.username == username).limit(1)
            ).first()
            if not db_user:
                raise Exception("User not found with username '{username}'")
            return db_user

    @staticmethod
    def update(id: int, user: User) -> User:
        with Session(engine) as session:
            db_user = session.get(User, id)
            if not db_user:
                raise Exception("User not found with id '{id}'")
            user_data = user.model_dump(exclude_unset=True)
            for key, value in user_data.items():
                setattr(db_user, key, value)
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            return db_user

    @staticmethod
    def delete(id: int | None = None, user: User | None = None) -> Literal[True]:
        with Session(engine) as session:
            db_user = user or session.get(User, id)
            if not db_user:
                raise Exception("User not found with id '{id}'")
            session.delete(db_user)
            session.commit()
            return True
