import pathlib

import pytest
from fastapi import testclient

from pilates import config
from pilates.data.json_repositories import _lesson_planning
from pilates.interfaces.api import app


@pytest.fixture()
def api_client(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> testclient.TestClient:
    database_file = tmp_path / "test_database.json"

    def get_test_repository():
        return _lesson_planning.JSONRepository(database_file=database_file)

    monkeypatch.setattr(config, "get_lesson_planning_repository", get_test_repository)

    return testclient.TestClient(app.app)
