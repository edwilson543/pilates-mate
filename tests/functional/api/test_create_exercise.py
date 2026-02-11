from unittest import mock


def test_creates_then_gets_exercise(api_client):
    exercise_list = api_client.get("/exercises")

    assert exercise_list.status_code == 200
    assert exercise_list == {"exercises": []}

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

    updated_exercise_list = api_client.get("/exercises")

    assert updated_exercise_list.status_code == 200
    assert updated_exercise_list == {
        "exercises": [
            {"id": create_response.json()["id"], **new_exercise},
        ]
    }
