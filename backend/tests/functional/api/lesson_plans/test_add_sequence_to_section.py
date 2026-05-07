from testing.helpers import lesson_plans as lesson_plan_helpers


def test_adds_sequence_to_section(authenticated_api_client, unit_of_work):
    lesson_plan = lesson_plan_helpers.LessonPlan.insert(
        unit_of_work, warm_up=[], main_session=[], cool_down=[]
    )

    response = authenticated_api_client.post(
        f"/lesson-plans/{lesson_plan.id}/sequences",
        json={
            "section": "WARM_UP",
            "name": "Breathing Sequence",
            "reps": 2,
            "notes": "Focus on deep breaths",
        },
    )

    assert response.status_code == 201
    lesson_plan = unit_of_work.lesson_plans.get_lesson_plan(lesson_plan.id)
    new_sequence = lesson_plan.warm_up[0]
    assert response.json()["id"] == new_sequence.id

    assert new_sequence.name == "Breathing Sequence"
    assert new_sequence.reps == 2
    assert new_sequence.notes == "Focus on deep breaths"
    assert new_sequence.sets == []


def test_response_not_found_when_adding_sequence_to_nonexistent_plan(
    authenticated_api_client,
):
    response = authenticated_api_client.post(
        "/lesson-plans/999/sequences",
        json={
            "section": "WARM_UP",
            "name": "Test Sequence",
            "reps": 1,
            "notes": "Test notes",
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Lesson plan not found."}
