import pytest

from pilates.data.json_backend import _unit_of_work
from pilates.domain import users


class TestCreateGetUser:
    def test_creates_then_gets_user(self, uow: _unit_of_work.JSONUnitOfWork):
        email = "ed@gmail.com"
        hashed_password = "some-password"

        user_id = uow.users.create_user(email=email, hashed_password=hashed_password)
        user = uow.users.get_user(email=email)

        assert user.id == user_id
        assert user.email == email
        assert user.hashed_password == hashed_password

    def test_raises_when_creating_user_that_already_exists(
        self, uow: _unit_of_work.JSONUnitOfWork
    ):
        email = "ed@gmail.com"

        uow.users.create_user(email=email, hashed_password="some-password")
        with pytest.raises(users.UserAlreadyExists) as exc:
            uow.users.create_user(email=email, hashed_password="some-other-password")

        assert exc.value.email == email

    def test_raises_when_getting_user_that_does_not_exist(
        self, uow: _unit_of_work.JSONUnitOfWork
    ):
        email = "fake@gmail.com"

        with pytest.raises(users.UserDoesNotExist) as exc:
            uow.users.get_user(email=email)

        assert exc.value.email == email
