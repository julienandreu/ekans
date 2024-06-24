from .model import Builder, User
from .repository import User as DbUser


def fromDb(user: DbUser) -> User:
    return Builder().setUsername(user.username).setId(user.public_id).build()
