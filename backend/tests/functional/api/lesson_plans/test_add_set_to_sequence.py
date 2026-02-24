from testing.helpers import lesson_planning as lesson_planning_helpers


def test_adds_exercise_set_to_existing_sequence(api_client, repository):
    sequence = lesson_planning_helpers.ExerciseSequence(sets=[])
    lesson_plan = lesson_planning_helpers.LessonPlan.create_in_repo(
        repository, warm_up=[sequence]
    )
    exercise = lesson_planning_helpers.Exercise.create_in_repo(repository)

    response = api_client.post(
        f"/lesson-plans/sequences/{sequence.id}/sets",
        json={
            "exercise_id": exercise.id,
            "reps": 10,
            "duration_seconds": 60,
            "movement_variant": "STANDARD",
            "equipment_variant": [],
        },
    )

    assert response.status_code == 201
    lesson_plan = repository.get_lesson_plan(lesson_plan.id)
    new_set = lesson_plan.warm_up[0].sets[0]
    assert response.json()["id"] == new_set.id

    assert new_set.exercise.id == exercise.id
    assert new_set.reps == 10
    assert new_set.duration_seconds == 60
    assert new_set.movement_variant == "STANDARD"
