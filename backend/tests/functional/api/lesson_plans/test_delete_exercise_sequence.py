from testing.helpers import lesson_plans as lesson_plan_helpers


def test_deletes_existing_exercise_sequence(unit_of_work, api_client):
    sequence_1 = lesson_plan_helpers.ExerciseSequence()
    sequence_2 = lesson_plan_helpers.ExerciseSequence()
    lesson_plan = lesson_plan_helpers.LessonPlan.insert(
        unit_of_work, cool_down=[sequence_1, sequence_2]
    )

    response = api_client.delete(f"/lesson-plans/sequences/{sequence_1.id}")

    assert response.status_code == 204
    lesson_plan = unit_of_work.lesson_plans.get_lesson_plan(lesson_plan.id)
    assert len(lesson_plan.cool_down) == 1
    assert lesson_plan.cool_down[0].id == sequence_2.id


def test_response_not_found_when_deleting_nonexistent_sequence(api_client):
    response = api_client.delete("/lesson-plans/sequences/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Sequence not found."}
