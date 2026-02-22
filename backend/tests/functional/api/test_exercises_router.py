from unittest import mock

from testing.helpers import lesson_planning as lesson_planning_helpers


def test_creates_then_gets_exercise(api_client):
    exercise_list = api_client.get("/exercises")

    assert exercise_list.status_code == 200
    assert exercise_list.json() == []

    new_exercise = {
        "name": "Squats",
        "description": "Move up and down",
        "category": "EFFORT",
        "difficulty": "INTERMEDIATE",
        "primary_muscle_group": "GLUTES",
        "starting_position": "STANDING",
        "movement_variants": ["STANDARD"],
        "equipment_variants": [],
    }

    create_response = api_client.post("/exercises", json=new_exercise)

    assert create_response.status_code == 201
    assert create_response.json() == {"id": mock.ANY}
    exercise_id = create_response.json()["id"]

    exercise = api_client.get(f"/exercises/{exercise_id}")

    assert exercise.status_code == 200
    expected_exercise_json = {"id": exercise_id, **new_exercise}
    assert exercise.json() == expected_exercise_json

    updated_exercise_list = api_client.get("/exercises")

    assert updated_exercise_list.status_code == 200
    assert updated_exercise_list.json() == [expected_exercise_json]


def test_response_not_found_when_exercise_does_not_exist(api_client):
    response = api_client.get("/exercises/123")

    assert response.status_code == 404
    assert response.json() == {"detail": "Exercise not found."}


def test_updates_exercise(api_client, repository):
    exercise = lesson_planning_helpers.Exercise.create_in_repo(repository)

    updated_exercise = {
        "name": "Jump Squats",
        "description": "Move up and down with a jump",
        "category": "EFFORT",
        "difficulty": "ADVANCED",
        "primary_muscle_group": "GLUTES",
        "starting_position": "STANDING",
        "movement_variants": ["STANDARD", "PULSE"],
        "equipment_variants": [],
    }
    update_response = api_client.put(f"/exercises/{exercise.id}", json=updated_exercise)

    assert update_response.status_code == 204
    assert update_response.content == b""

    get_response = api_client.get(f"/exercises/{exercise.id}")
    assert get_response.status_code == 200
    assert get_response.json() == {"id": exercise.id, **updated_exercise}


def test_update_response_not_found_when_exercise_does_not_exist(api_client):
    updated_exercise = {
        "name": "Jump Squats",
        "description": "Move up and down with a jump",
        "category": "EFFORT",
        "difficulty": "ADVANCED",
        "primary_muscle_group": "GLUTES",
        "starting_position": "STANDING",
        "movement_variants": ["STANDARD", "PULSE"],
        "equipment_variants": [],
    }

    response = api_client.put("/exercises/123", json=updated_exercise)

    assert response.status_code == 404
    assert response.json() == {"detail": "Exercise not found."}


def test_updating_exercise_updates_lesson_plan_references(api_client, repository):
    exercise = lesson_planning_helpers.Exercise.create_in_repo(repository)
    exercise_set = lesson_planning_helpers.ExerciseSet(exercise=exercise)
    sequence = lesson_planning_helpers.ExerciseSequence(sets=[exercise_set])
    lesson_plan = lesson_planning_helpers.LessonPlan.create_in_repo(
        repository, warm_up=[sequence]
    )

    updated_exercise = {
        "name": "Jump Squats",
        "description": "Move up and down with a jump",
        "category": "EFFORT",
        "difficulty": "ADVANCED",
        "primary_muscle_group": "GLUTES",
        "starting_position": "STANDING",
        "movement_variants": ["STANDARD", "PULSE"],
        "equipment_variants": ["ANKLE_WEIGHTS"],
    }
    update_response = api_client.put(f"/exercises/{exercise.id}", json=updated_exercise)
    assert update_response.status_code == 204

    lesson_plan_response = api_client.get(f"/lesson-plans/{lesson_plan.id}")
    assert lesson_plan_response.status_code == 200

    warm_up_exercise = lesson_plan_response.json()["warm_up"][0]["sets"][0]["exercise"]
    assert warm_up_exercise["id"] == exercise.id
    assert warm_up_exercise["name"] == "Jump Squats"
    assert warm_up_exercise["description"] == "Move up and down with a jump"
    assert warm_up_exercise["difficulty"] == "ADVANCED"
    assert warm_up_exercise["movement_variants"] == ["STANDARD", "PULSE"]
    assert warm_up_exercise["equipment_variants"] == ["ANKLE_WEIGHTS"]
