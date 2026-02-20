import datetime as dt

import pytest

from pilates.application import generate_plan
from testing.helpers import lesson_planning as lesson_planning_helpers
from testing.helpers import vendors as vendor_helpers


@pytest.mark.asyncio
class TestGenerateLessonPlan:
    async def test_generates_and_returns_lesson_plan(self):
        repository = lesson_planning_helpers.FakeRepository()

        # Create exercises that will be referenced in the generated plan
        exercise1 = lesson_planning_helpers.Exercise()
        exercise2 = lesson_planning_helpers.Exercise()
        exercise3 = lesson_planning_helpers.Exercise()
        repository._exercises.extend([exercise1, exercise2, exercise3])

        fake_completion = generate_plan._GeneratedLessonPlan(
            name="Morning Flow",
            description="A refreshing morning Pilates session",
            warm_up=[
                lesson_planning_helpers.GeneratedExerciseSequence(
                    n_sets=1,
                    sets=[
                        lesson_planning_helpers.GeneratedExerciseSet(
                            exercise=generate_plan._GeneratedExercise(
                                id=exercise1.id, name=exercise1.name
                            )
                        )
                    ],
                )
            ],
            main_session=[
                lesson_planning_helpers.GeneratedExerciseSequence(
                    n_sets=1,
                    sets=[
                        lesson_planning_helpers.GeneratedExerciseSet(
                            exercise=generate_plan._GeneratedExercise(
                                id=exercise2.id, name=exercise2.name
                            )
                        )
                    ],
                )
            ],
            cool_down=[
                lesson_planning_helpers.GeneratedExerciseSequence(
                    n_sets=1,
                    sets=[
                        lesson_planning_helpers.GeneratedExerciseSet(
                            exercise=generate_plan._GeneratedExercise(
                                id=exercise3.id, name=exercise3.name
                            )
                        )
                    ],
                )
            ],
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
        assert result.date == dt.datetime.now().date()
        assert len(result.warm_up) == 1
        assert len(result.main_session) == 1
        assert len(result.cool_down) == 1
        assert result.warm_up[0].name == fake_completion.warm_up[0].name
        assert result.main_session[0].name == fake_completion.main_session[0].name
        assert result.cool_down[0].name == fake_completion.cool_down[0].name
