from testing.helpers import exercises as exercise_helpers


def test_updates_exercise(api_client, unit_of_work):
    exercise = exercise_helpers.Exercise.insert(unit_of_work)

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
