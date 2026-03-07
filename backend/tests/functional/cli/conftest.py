import pathlib
import typing

import pytest
from click.testing import CliRunner

from pilates.data import json_backend
from testing.helpers import unit_of_work as unit_of_work_helpers


@pytest.fixture
def cli_runner() -> CliRunner:
    """Provide a Click CLI runner for testing commands."""
    return CliRunner()


@pytest.fixture
def unit_of_work(
    tmp_path: pathlib.Path,
) -> typing.Generator[json_backend.JSONUnitOfWork, None, None]:
    """Use the real repository implementation with a fresh test database."""
    database_file = tmp_path / "test_database.json"
    uow = json_backend.JSONUnitOfWork(database_file=database_file)

    with unit_of_work_helpers.inject_uow(uow):
        yield uow
