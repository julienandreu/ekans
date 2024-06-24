from __future__ import annotations

from pydantic import BaseModel


class User(BaseModel):
    username: str

    def __init__(self, username: str) -> None:
        super().__init__(username=username)


class Builder:
    def setUsername(self, username: str) -> Builder:
        self.__username = username
        return self

    def reset(self) -> Builder:
        return Builder()

    def build(self) -> User:
        return User(self.__username)
