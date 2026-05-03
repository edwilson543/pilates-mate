from importlib import resources

from pilates.data.json_backend import _unit_of_work


def test_database_can_be_deserialized():
    database_file_ref = resources.files(_unit_of_work) / "database.json"
    with resources.as_file(database_file_ref) as database_file:
        json_uow = _unit_of_work.JSONUnitOfWork(database_file)

    assert json_uow.exercises.get_exercises() is not None
    assert json_uow.lesson_plans.get_lesson_plans() is not None
