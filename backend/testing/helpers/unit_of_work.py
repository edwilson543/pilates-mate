import contextlib
import typing
from unittest import mock

import attrs

from pilates.domain import unit_of_work
from testing.helpers import exercises as exercise_helpers
from testing.helpers import lesson_plans as lesson_plan_helpers
from testing.helpers import users as user_helpers


@attrs.frozen
class FakeUnitOfWork(unit_of_work.UnitOfWork):
    lesson_plans = attrs.field(factory=lesson_plan_helpers.FakeRepository)
    exercises = attrs.field(factory=exercise_helpers.FakeRepository)
    users = attrs.field(factory=user_helpers.FakeRepository)


@contextlib.contextmanager
def inject_uow(
    uow: unit_of_work.UnitOfWork,
) -> typing.Generator[None, None, None]:
    """
    Override the configuration hook to inject a particular unit of work.
    """
    with mock.patch("pilates.config.get_unit_of_work", return_value=uow):
        yield
