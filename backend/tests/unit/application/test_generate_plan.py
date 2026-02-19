import datetime as dt

import pytest

from pilates.application import generate_plan
from testing.helpers import lesson_planning as lesson_planning_helpers
from testing.helpers import vendors as vendor_helpers


@pytest.mark.asyncio
class TestGenerateLessonPlan:
    async def test_generates_and_returns_lesson_plan(self):
        repository = lesson_planning_helpers.FakeRepository()
        fake_completion = generate_plan._GeneratedLessonPlan(
            name="Morning Flow",
            description="A refreshing morning Pilates session",
            date=dt.date(2026, 1, 15),
            warm_up=[lesson_planning_helpers.ExerciseSequence()],
            main_session=[lesson_planning_helpers.ExerciseSequence()],
            cool_down=[lesson_planning_helpers.ExerciseSequence()],
        )
        client = vendor_helpers.FakeCompletionClient(completion=fake_completion)

        requirements = lesson_planning_helpers.LessonPlanRequirements()

        result = await generate_plan.generate_lesson_plan(
            requirements=requirements,
            client=client,
            repository=repository,
        )

        assert result.id == 1
        assert result.name == "Morning Flow"
        assert result.description == "A refreshing morning Pilates session"
        assert result.date == fake_completion.date
        assert result.warm_up == fake_completion.warm_up
        assert result.main_session == fake_completion.main_session
        assert result.cool_down == fake_completion.cool_down
