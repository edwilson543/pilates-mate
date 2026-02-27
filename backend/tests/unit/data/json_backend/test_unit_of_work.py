from pilates import config


def test_database_can_be_deserialized():
    real_unit_of_work = config.get_unit_of_work()

    assert real_unit_of_work.exercises.get_exercises() is not None
    assert real_unit_of_work.lesson_plans.get_lesson_plans() is not None
