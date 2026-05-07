import pathlib

import attrs

from pilates.domain import users

from . import _mixins


@attrs.frozen
class JSONRepository(users.Repository, _mixins.JSONRepositoryMixin):
    database_file: pathlib.Path

    def create_user(self, *, email: str, hashed_password: str, full_name: str) -> int:
        self._raise_if_user_exists(email=email)

        user_id = self._get_next_user_id()
        user = users.User(
            id=user_id,
            full_name=full_name,
            email=email,
            hashed_password=hashed_password,
        )

        data = self._read_database()
        data["users"].append(user.model_dump())
        self._write_database(data)
        return user_id

    def get_user(self, *, email: str) -> users.User:
        for user in self._get_users():
            if user.email == email:
                return user
        raise users.UserDoesNotExist(email=email)

    def _get_users(self) -> list[users.User]:
        data = self._read_database()
        return [users.User.model_validate(user) for user in data["users"]]

    def _get_next_user_id(self) -> int:
        data = self._read_database()
        return max((user["id"] for user in data["users"]), default=0) + 1

    def _raise_if_user_exists(self, *, email: str) -> None:
        try:
            self.get_user(email=email)
        except users.UserDoesNotExist:
            return

        raise users.UserAlreadyExists(email=email)
