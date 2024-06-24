from uuid import UUID

from .model import Builder, User
from .repository import User as DbUser


class UserDataMapper:
    @staticmethod
    def from_db(db_user: DbUser) -> User:
        return (
            Builder()
            .set_username(db_user.username)
            .set_id(UUID(db_user.public_id))
            .build()
        )

    @staticmethod
    def from_model(user: User) -> DbUser:
        db_user = DbUser.model_validate(
            {
                "id": None,
                "public_id": str(user.id),
                "username": user.username,
            }
        )
        return db_user
