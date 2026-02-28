import pathlib

import pytest

from pilates.data.json_backend import _unit_of_work


@pytest.fixture()
def uow(tmp_path: pathlib.Path) -> _unit_of_work.JSONUnitOfWork:
    database_file = tmp_path / "test_database.json"
    uow = _unit_of_work.JSONUnitOfWork(database_file=database_file)
    return uow
