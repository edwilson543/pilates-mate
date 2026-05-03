import pathlib
import typing

import pytest
import pytest_asyncio
from fastapi import testclient

from pilates import config
from pilates.data import json_backend
from pilates.interfaces.api import app
from testing.helpers import unit_of_work as unit_of_work_helpers


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


@pytest.fixture()
def unit_of_work(
    tmp_path: pathlib.Path,
) -> typing.Generator[json_backend.JSONUnitOfWork, None, None]:
    """
    Use the real repository implementation, but with a fresh database per test.
    """
    # Create a fresh JSON database in a temp directory.
    database_file = tmp_path / "test_database.json"
    uow = json_backend.JSONUnitOfWork(database_file=database_file)

    with unit_of_work_helpers.inject_uow(uow):
        yield uow
