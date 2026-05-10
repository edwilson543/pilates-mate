import datetime as dt

import pytest

from pilates.application import generate_lesson_plan
from pilates.domain import lesson_plans
from testing.helpers import exercises as exercise_helpers
from testing.helpers import lesson_plans as lesson_plan_helpers
from testing.helpers import unit_of_work as unit_of_work_helpers
from testing.helpers import vendors as vendor_helpers


@pytest.mark.asyncio
class TestGenerateLessonPlan:
    async def test_generates_and_populates_lesson_plan(self):
        uow = unit_of_work_helpers.FakeUnitOfWork()

        requirements = lesson_plan_helpers.LessonPlanRequirements()
        lesson_plan_id = uow.lesson_plans.create_lesson_plan(
            name="initial-name",
            date=dt.date(2026, 1, 1),
            requirements=requirements,
        )

        generated_plan = lesson_plan_helpers.GeneratedLessonPlan(name="generated-name")
        client = vendor_helpers.FakeCompletionClient(completion=generated_plan)
        for generated_exercise in generated_plan.exercises:
            exercise_helpers.Exercise.insert(
                uow=uow, id=generated_exercise.id, name=generated_exercise.name
            )

        await generate_lesson_plan.generate_lesson_plan(
            lesson_plan_id=lesson_plan_id, client=client, uow=uow
        )

        lesson_plan = uow.lesson_plans.get_lesson_plan(lesson_plan_id)

        assert lesson_plan.name == "generated-name"
        assert lesson_plan.status == lesson_plans.LessonPlanStatus.GENERATED
        assert lesson_plan.description == generated_plan.description
        assert len(lesson_plan.warm_up) == len(generated_plan.warm_up) == 1
        assert len(lesson_plan.main_session) == len(generated_plan.main_session) == 1
        assert len(lesson_plan.cool_down) == len(generated_plan.cool_down) == 1
        assert lesson_plan.warm_up[0].name == generated_plan.warm_up[0].name
        assert lesson_plan.main_session[0].name == generated_plan.main_session[0].name
        assert lesson_plan.cool_down[0].name == generated_plan.cool_down[0].name
