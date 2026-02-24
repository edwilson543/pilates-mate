from testing.helpers import lesson_planning as lesson_planning_helpers


def test_deletes_existing_exercise_sets(repository, api_client):
    first_set = lesson_planning_helpers.ExerciseSet()
    second_set = lesson_planning_helpers.ExerciseSet()
    sequence = lesson_planning_helpers.ExerciseSequence(sets=[first_set, second_set])
    lesson_plan = lesson_planning_helpers.LessonPlan.create_in_repo(
        repository, cool_down=[sequence]
    )

    response = api_client.delete(
        f"/lesson-plans/sequences/{sequence.id}/sets/{first_set.id}"
    )

    assert response.status_code == 204
    lesson_plan = repository.get_lesson_plan(lesson_plan.id)
    assert lesson_plan.cool_down[0].sets == [second_set]

    response = api_client.delete(
        f"/lesson-plans/sequences/{sequence.id}/sets/{second_set.id}"
    )

    assert response.status_code == 204
    lesson_plan = repository.get_lesson_plan(lesson_plan.id)
    assert lesson_plan.cool_down[0].sets == []


def test_response_not_found_when_deleting_nonexistent_set(api_client):
    response = api_client.delete("/lesson-plans/sequences/999/sets/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Set not found."}
