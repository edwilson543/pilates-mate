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
    }

    create_response = api_client.post("/exercises", json=new_exercise)

    assert create_response.status_code == 201
    assert create_response.json() == {"id": mock.ANY}
    exercise_id = create_response.json()["id"]

    exercise = api_client.get(f"/exercises/{exercise_id}")

    assert exercise.status_code == 200
    expected_exercise_json = {"id": create_response.json()["id"], **new_exercise}
    assert exercise.json() == expected_exercise_json

    updated_exercise_list = api_client.get("/exercises")

    assert updated_exercise_list.status_code == 200
    assert updated_exercise_list.json() == [expected_exercise_json]


def test_response_not_found_when_exercise_does_not_exist(api_client):
    exercise_id = 123

    response = api_client.get(f"/exercises/{exercise_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Exercise not found."}
