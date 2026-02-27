import pathlib
import typing

import pytest
from fastapi import testclient

from pilates.data import json_backend
from pilates.interfaces.api import app
from testing.helpers import unit_of_work as unit_of_work_helpers


@pytest.fixture()
def api_client(unit_of_work) -> testclient.TestClient:
    return testclient.TestClient(app.app)


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
