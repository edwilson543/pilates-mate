from pilates.domain import lesson_plans
from testing.helpers import exercises as exercise_helpers
from testing.helpers import lesson_plans as lesson_plan_helpers
from testing.helpers import vendors as vendor_helpers


def test_generates_lesson_plan(authenticated_api_client, unit_of_work):
    exercise = exercise_helpers.Exercise.insert(unit_of_work)

    fake_completion = lesson_plans.GeneratedLessonPlan(
        name="30 minute blast",
        description="An energising session",
        warm_up=[
            lesson_plan_helpers.GeneratedExerciseSequence(
                n_sets=1,
                sets=[
                    lesson_plan_helpers.GeneratedExerciseSet(
                        exercise=lesson_plan_helpers.GeneratedExercise(
                            id=exercise.id, name=exercise.name
                        )
                    )
                ],
            )
        ],
        main_session=[],
        cool_down=[],
    )
    fake_client = vendor_helpers.FakeCompletionClient(completion=fake_completion)

    with fake_client.inject():
        response = authenticated_api_client.post(
            "/lesson-plans/",
            json={
                "requirements": {
                    "duration_minutes": 30,
                    "target_difficulty": "INTERMEDIATE",
                    "target_muscle_groups": ["CORE"],
                    "available_equipment": [],
                    "user_prompt": "An energising morning session",
                }
            },
        )

    assert response.status_code == 201
    lesson_plan_id = response.json()["id"]

    lesson_plan = unit_of_work.lesson_plans.get_lesson_plan(lesson_plan_id)

    assert lesson_plan.name == fake_completion.name
    assert lesson_plan.status == lesson_plans.LessonPlanStatus.GENERATED
    assert lesson_plan.description == "An energising session"
    assert len(lesson_plan.warm_up) == 1
    assert lesson_plan.main_session == []
    assert lesson_plan.cool_down == []
