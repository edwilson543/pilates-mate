import typing

import pytest_asyncio
from fastapi import testclient

from pilates import config
from pilates.interfaces.api import app


class _APIClient(testclient.TestClient):
    def set_auth_token(self, token: str) -> None:
        self._headers.update({"Authorization": f"Bearer {token}"})

    @property
    def app_settings(self) -> config.Settings:
        # Mypy doesn't track that the type of the `settings` object set by application lifespan.
        return self.app.state.settings  # type:ignore[attr-defined]


@pytest_asyncio.fixture()
async def api_client(unit_of_work) -> typing.AsyncIterator[_APIClient]:
    async with app.lifespan(app.app):
        yield _APIClient(app.app)
