import pathlib

from pilates.domain import unit_of_work

from . import _exercises, _lesson_plans, _users


class JSONUnitOfWork(unit_of_work.UnitOfWork):
    def __init__(self, database_file: pathlib.Path | None = None) -> None:
        database_file = database_file or pathlib.Path(__file__).parent / "database.json"

        self.exercises = _exercises.JSONRepository(database_file=database_file)
        self.lesson_plans = _lesson_plans.JSONRepository(database_file=database_file)
        self.users = _users.JSONRepository(database_file=database_file)
