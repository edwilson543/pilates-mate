import typing

import pytest
import pytest_asyncio
from fastapi import testclient

from pilates import config
from pilates.domain import unit_of_work, users
from pilates.interfaces.api import app
from testing.helpers import users as user_helpers


class _APIClient(testclient.TestClient):
    def __init__(
        self,
        settings: config.Settings,
        uow: unit_of_work.UnitOfWork,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        self._settings = settings
        self._uow = uow

        self._authenticated_user: users.User | None = None

    def create_user_and_login(self) -> None:
        auth_service = config.get_auth_service(settings=self._settings, uow=self._uow)
        password = "qwerty123"
        user = user_helpers.User.insert(uow=self._uow, password=password)
        tokens = auth_service.issue_access_and_refresh_token_from_credentials(
            email=user.email, password=password
        )

        self.set_access_token(token=tokens.access_token)
        self._authenticated_user = user

    def set_access_token(self, token: str) -> None:
        self._headers.update({"Authorization": f"Bearer {token}"})

    @property
    def app_settings(self) -> config.Settings:
        # Mypy doesn't track that the type of the `settings` object set by application lifespan.
        return self.app.state.settings  # type:ignore[attr-defined]

    @property
    def authenticated_user(self) -> users.User:
        if not self._authenticated_user:
            pytest.fail("API Client is not authenticated as any user.")
        return self._authenticated_user


@pytest_asyncio.fixture()
async def api_client(settings, unit_of_work) -> typing.AsyncIterator[_APIClient]:
    async with app.lifespan(app.app, settings=settings):
        yield _APIClient(app=app.app, settings=settings, uow=unit_of_work)


@pytest_asyncio.fixture()
async def authenticated_api_client(api_client) -> typing.AsyncIterator[_APIClient]:
    api_client.create_user_and_login()
    yield api_client
