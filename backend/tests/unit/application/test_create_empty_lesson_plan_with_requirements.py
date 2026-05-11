import datetime as dt

import pytest

from pilates.application import create_empty_lesson_plan_with_requirements
from pilates.domain import lesson_plans
from testing.helpers import lesson_plans as lesson_plan_helpers
from testing.helpers import unit_of_work as unit_of_work_helpers


@pytest.mark.asyncio
class TestCreateEmptyLessonPlanWithRequirements:
    async def test_creates_lesson_plan_and_returns_id(self):
        uow = unit_of_work_helpers.FakeUnitOfWork()
        requirements = lesson_plan_helpers.LessonPlanRequirements()

        lesson_plan_id = await create_empty_lesson_plan_with_requirements.create_empty_lesson_plan_with_requirements(
            created_at=dt.date(2026, 1, 1),
            requirements=requirements,
            uow=uow,
        )

        result = uow.lesson_plans.get_lesson_plan(lesson_plan_id)

        assert lesson_plan_id == 1
        assert result.name == "30 minute blast - 1 January 2026"
        assert result.date == dt.date(2026, 1, 1)
        assert result.requirements == requirements
        assert result.status == lesson_plans.LessonPlanStatus.PENDING_GENERATION
        assert result.description == ""
        assert result.warm_up == []
        assert result.main_session == []
        assert result.cool_down == []
