from pilates.domain import lesson_plans
from testing.helpers import lesson_plans as lesson_plan_helpers


def test_update_exercise_set_to_new_values(api_client, repository):
    exercise_set = lesson_plan_helpers.ExerciseSet(
        reps=31, duration_seconds=30, movement_variant="HOLD"
    )
    sequence = lesson_plan_helpers.ExerciseSequence(sets=[exercise_set])
    lesson_plan_helpers.LessonPlan.create_in_repo(repository, main_session=[sequence])

    response = api_client.put(
        f"/lesson-plans/sequences/{sequence.id}/sets/{exercise_set.id}",
        json={
            "reps": 10,
            "duration_seconds": 60,
            "movement_variant": "PULSE",
            "equipment_variant": [],
        },
    )

    assert response.status_code == 204

    updated_set = repository.get_exercise_set(exercise_set.id)
    assert updated_set.reps == 10
    assert updated_set.duration_seconds == 60
    assert updated_set.movement_variant == lesson_plans.MovementVariant.PULSE


def test_response_not_found_when_updating_nonexistent_set(api_client):
    response = api_client.put(
        "/lesson-plans/sequences/999/sets/999",
        json={
            "reps": 10,
            "duration_seconds": 60,
            "movement_variant": "PULSE",
            "equipment_variant": [],
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Set not found."}
