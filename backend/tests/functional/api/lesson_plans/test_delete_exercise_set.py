from testing.helpers import lesson_plans as lesson_plan_helpers


def test_deletes_existing_exercise_sets(unit_of_work, authenticated_api_client):
    lesson_plan = lesson_plan_helpers.LessonPlan.insert(
        unit_of_work,
        cool_down=[
            lesson_plan_helpers.ExerciseSequence(
                sets=[
                    lesson_plan_helpers.ExerciseSet(),
                    lesson_plan_helpers.ExerciseSet(),
                ]
            )
        ],
    )
    sequence = lesson_plan.cool_down[0]
    first_set_id = sequence.sets[0].id
    second_set_id = sequence.sets[1].id

    response = authenticated_api_client.delete(
        f"/lesson-plans/sequences/{sequence.id}/sets/{first_set_id}"
    )

    assert response.status_code == 204
    lesson_plan = unit_of_work.lesson_plans.get_lesson_plan(lesson_plan.id)
    assert len(lesson_plan.cool_down[0].sets) == 1
    assert lesson_plan.cool_down[0].sets[0].id == second_set_id

    response = authenticated_api_client.delete(
        f"/lesson-plans/sequences/{sequence.id}/sets/{second_set_id}"
    )

    assert response.status_code == 204
    lesson_plan = unit_of_work.lesson_plans.get_lesson_plan(lesson_plan.id)
    assert lesson_plan.cool_down[0].sets == []


def test_response_not_found_when_deleting_nonexistent_set(authenticated_api_client):
    response = authenticated_api_client.delete("/lesson-plans/sequences/999/sets/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Set not found."}
