import pathlib
import typing

import pytest
from fastapi import testclient

from pilates.data import json_repositories
from pilates.interfaces.api import app
from testing.helpers import lesson_plans as lesson_plan_helpers


@pytest.fixture()
def api_client(repository) -> testclient.TestClient:
    return testclient.TestClient(app.app)


@pytest.fixture()
def repository(
    tmp_path: pathlib.Path,
) -> typing.Generator[json_repositories.JSONRepository, None, None]:
    """
    Use the real repository implementation, but with a fresh database per test.
    """
    # Create a fresh JSON database in a temp directory.
    database_file = tmp_path / "test_database.json"
    repo = json_repositories.JSONRepository(database_file=database_file)

    with lesson_plan_helpers.inject_repository(repo):
        yield repo
