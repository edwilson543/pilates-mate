from testing.helpers import lesson_plans as lesson_plan_helpers


def test_update_exercise_sequence_to_new_values(api_client, repository):
    sequence = lesson_plan_helpers.ExerciseSequence(
        name="Original Name", reps=1, notes="Original notes"
    )
    lesson_plan_helpers.LessonPlan.create_in_repo(repository, main_session=[sequence])

    response = api_client.put(
        f"/lesson-plans/sequences/{sequence.id}",
        json={
            "name": "Updated Name",
            "reps": 3,
            "notes": "Updated notes",
        },
    )

    assert response.status_code == 204

    updated_sequence = repository.get_lesson_plan(1).main_session[0]
    assert updated_sequence.name == "Updated Name"
    assert updated_sequence.reps == 3
    assert updated_sequence.notes == "Updated notes"


def test_response_not_found_when_updating_nonexistent_sequence(api_client):
    response = api_client.put(
        "/lesson-plans/sequences/999",
        json={
            "name": "Test Name",
            "reps": 2,
            "notes": "Test notes",
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Sequence not found."}
