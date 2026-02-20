from unittest import mock


def test_creates_then_gets_exercise(api_client):
    exercise_list = api_client.get("/exercises")

    assert exercise_list.status_code == 200
    assert exercise_list.json() == []

    new_exercise = {
        "name": "Squats",
        "description": "Move up and down",
        "difficulty": "INTERMEDIATE",
        "primary_muscle_group": "GLUTES",
        "starting_position": "STANDING",
        "variants": ["STANDARD"],
    }

    create_response = api_client.post("/exercises", json=new_exercise)

    assert create_response.status_code == 201
    assert create_response.json() == {"id": mock.ANY}
    exercise_id = create_response.json()["id"]

    exercise = api_client.get(f"/exercises/{exercise_id}")

    assert exercise.status_code == 200
    expected_exercise_json = {
        "id": create_response.json()["id"],
        **new_exercise,
    }
    assert exercise.json() == expected_exercise_json

    updated_exercise_list = api_client.get("/exercises")

    assert updated_exercise_list.status_code == 200
    assert updated_exercise_list.json() == [expected_exercise_json]


def test_response_not_found_when_exercise_does_not_exist(api_client):
    exercise_id = 123

    response = api_client.get(f"/exercises/{exercise_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Exercise not found."}


def test_updates_exercise(api_client):
    new_exercise = {
        "name": "Squats",
        "description": "Move up and down",
        "difficulty": "INTERMEDIATE",
        "primary_muscle_group": "GLUTES",
        "starting_position": "STANDING",
        "variants": ["STANDARD"],
    }
    create_response = api_client.post("/exercises", json=new_exercise)
    exercise_id = create_response.json()["id"]

    updated_exercise = {
        "name": "Jump Squats",
        "description": "Move up and down with a jump",
        "difficulty": "ADVANCED",
        "primary_muscle_group": "GLUTES",
        "starting_position": "STANDING",
        "variants": ["STANDARD", "PULSE"],
    }
    update_response = api_client.put(f"/exercises/{exercise_id}", json=updated_exercise)

    assert update_response.status_code == 204
    assert update_response.content == b""

    get_response = api_client.get(f"/exercises/{exercise_id}")
    assert get_response.status_code == 200
    expected_exercise_json = {
        "id": exercise_id,
        **updated_exercise,
    }
    assert get_response.json() == expected_exercise_json


def test_update_response_not_found_when_exercise_does_not_exist(api_client):
    exercise_id = 123
    updated_exercise = {
        "name": "Jump Squats",
        "description": "Move up and down with a jump",
        "difficulty": "ADVANCED",
        "primary_muscle_group": "GLUTES",
        "starting_position": "STANDING",
        "variants": ["STANDARD", "PULSE"],
    }

    response = api_client.put(f"/exercises/{exercise_id}", json=updated_exercise)

    assert response.status_code == 404
    assert response.json() == {"detail": "Exercise not found."}


def test_updating_exercise_updates_lesson_plan_references(api_client):
    import datetime as dt

    from pilates import config
    from pilates.domain import lesson_planning

    # Create an exercise
    new_exercise = {
        "name": "Squats",
        "description": "Move up and down",
        "difficulty": "INTERMEDIATE",
        "primary_muscle_group": "GLUTES",
        "starting_position": "STANDING",
        "variants": ["STANDARD"],
    }
    create_response = api_client.post("/exercises", json=new_exercise)
    exercise_id = create_response.json()["id"]

    # Create a lesson plan that uses this exercise
    repository = config.get_lesson_planning_repository()

    lesson_plan_id = repository.create_lesson_plan(
        name="Morning Flow",
        description="A refreshing morning Pilates session",
        date=dt.date(2026, 1, 15),
    )
    sequence_id = repository.add_sequence_to_section(
        lesson_plan_id=lesson_plan_id,
        section=lesson_planning.LessonPlanSection.WARM_UP,
        name="Squat Sequence",
        reps=1,
        notes="Focus on form",
    )
    repository.add_set_to_sequence(
        sequence_id=sequence_id,
        exercise_id=exercise_id,
        reps=10,
        duration_seconds=30,
        variant=lesson_planning.ExerciseVariant.STANDARD,
    )

    # Update the exercise
    updated_exercise = {
        "name": "Jump Squats",
        "description": "Move up and down with a jump",
        "difficulty": "ADVANCED",
        "primary_muscle_group": "GLUTES",
        "starting_position": "STANDING",
        "variants": ["STANDARD", "PULSE"],
    }
    update_response = api_client.put(f"/exercises/{exercise_id}", json=updated_exercise)
    assert update_response.status_code == 204

    # Verify the lesson plan has the updated exercise data
    lesson_plan_response = api_client.get(f"/lesson-plans/{lesson_plan_id}")
    assert lesson_plan_response.status_code == 200

    lesson_plan_json = lesson_plan_response.json()
    warm_up_exercise = lesson_plan_json["warm_up"][0]["sets"][0]["exercise"]

    assert warm_up_exercise["id"] == exercise_id
    assert warm_up_exercise["name"] == "Jump Squats"
    assert warm_up_exercise["description"] == "Move up and down with a jump"
    assert warm_up_exercise["difficulty"] == "ADVANCED"
    assert warm_up_exercise["variants"] == ["STANDARD", "PULSE"]
