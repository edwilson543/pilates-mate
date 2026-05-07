import abc

import attrs

from . import _models


@attrs.frozen
class UserAlreadyExists(Exception):
    email: str


@attrs.frozen
class UserDoesNotExist(Exception):
    email: str


class Repository(abc.ABC):
    @abc.abstractmethod
    def create_user(self, *, email: str, hashed_password: str, full_name: str) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def get_user(self, *, email: str) -> _models.User:
        raise NotImplementedError
