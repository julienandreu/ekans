from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


class User(BaseModel):
    id: UUID
    username: str

    def __init__(self, id: UUID, username: str) -> None:
        super().__init__(id=id, username=username)


class Builder:
    def set_id(self, id: UUID) -> Builder:
        self.__id = id
        return self

    def set_username(self, username: str) -> Builder:
        self.__username = username
        return self

    def reset(self) -> Builder:
        return Builder()

    def build(self) -> User:
        return User(self.__id, self.__username)
