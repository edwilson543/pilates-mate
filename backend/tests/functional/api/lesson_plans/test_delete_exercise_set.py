from testing.helpers import lesson_plans as lesson_plan_helpers


def test_deletes_existing_exercise_sets(unit_of_work, api_client):
    first_set = lesson_plan_helpers.ExerciseSet()
    second_set = lesson_plan_helpers.ExerciseSet()
    sequence = lesson_plan_helpers.ExerciseSequence(sets=[first_set, second_set])
    lesson_plan = lesson_plan_helpers.LessonPlan.insert(
        unit_of_work, cool_down=[sequence]
    )

    response = api_client.delete(
        f"/lesson-plans/sequences/{sequence.id}/sets/{first_set.id}"
    )

    assert response.status_code == 204
    lesson_plan = unit_of_work.lesson_plans.get_lesson_plan(lesson_plan.id)
    assert lesson_plan.cool_down[0].sets == [second_set]

    response = api_client.delete(
        f"/lesson-plans/sequences/{sequence.id}/sets/{second_set.id}"
    )

    assert response.status_code == 204
    lesson_plan = unit_of_work.lesson_plans.get_lesson_plan(lesson_plan.id)
    assert lesson_plan.cool_down[0].sets == []


def test_response_not_found_when_deleting_nonexistent_set(api_client):
    response = api_client.delete("/lesson-plans/sequences/999/sets/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Set not found."}
