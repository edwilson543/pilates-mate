import datetime as dt

import pytest

from pilates.application import generate_lesson_plan
from testing.helpers import exercises as exercise_helpers
from testing.helpers import lesson_plans as lesson_plan_helpers
from testing.helpers import unit_of_work as unit_of_work_helpers
from testing.helpers import vendors as vendor_helpers


@pytest.mark.asyncio
class TestGenerateLessonPlan:
    async def test_generates_and_returns_lesson_plan(self):
        uow = unit_of_work_helpers.FakeUnitOfWork()

        # Create exercises that will be referenced in the generated plan
        exercise1 = exercise_helpers.Exercise.insert(uow)
        exercise2 = exercise_helpers.Exercise.insert(uow)
        exercise3 = exercise_helpers.Exercise.insert(uow)

        fake_completion = generate_lesson_plan._GeneratedLessonPlan(
            name="Morning Flow",
            description="A refreshing morning Pilates session",
            warm_up=[
                lesson_plan_helpers.GeneratedExerciseSequence(
                    n_sets=1,
                    sets=[
                        lesson_plan_helpers.GeneratedExerciseSet(
                            exercise=generate_lesson_plan._GeneratedExercise(
                                id=exercise1.id, name=exercise1.name
                            )
                        )
                    ],
                )
            ],
            main_session=[
                lesson_plan_helpers.GeneratedExerciseSequence(
                    n_sets=1,
                    sets=[
                        lesson_plan_helpers.GeneratedExerciseSet(
                            exercise=generate_lesson_plan._GeneratedExercise(
                                id=exercise2.id, name=exercise2.name
                            )
                        )
                    ],
                )
            ],
            cool_down=[
                lesson_plan_helpers.GeneratedExerciseSequence(
                    n_sets=1,
                    sets=[
                        lesson_plan_helpers.GeneratedExerciseSet(
                            exercise=generate_lesson_plan._GeneratedExercise(
                                id=exercise3.id, name=exercise3.name
                            )
                        )
                    ],
                )
            ],
        )
        client = vendor_helpers.FakeCompletionClient(completion=fake_completion)

        requirements = lesson_plan_helpers.LessonPlanRequirements()

        result = await generate_lesson_plan.generate_lesson_plan(
            requirements=requirements, client=client, uow=uow
        )

        assert result.id == 1
        assert result.name == "Morning Flow"
        assert result.description == "A refreshing morning Pilates session"
        assert result.date == dt.datetime.now().date()
        assert len(result.warm_up) == 1
        assert len(result.main_session) == 1
        assert len(result.cool_down) == 1
        assert result.warm_up[0].name == fake_completion.warm_up[0].name
        assert result.main_session[0].name == fake_completion.main_session[0].name
        assert result.cool_down[0].name == fake_completion.cool_down[0].name
