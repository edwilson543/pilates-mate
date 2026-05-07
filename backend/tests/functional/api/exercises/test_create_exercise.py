def test_creates_then_gets_exercise(authenticated_api_client):
    exercise_list = authenticated_api_client.get("/exercises")

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

    create_response = authenticated_api_client.post("/exercises", json=new_exercise)

    assert create_response.status_code == 201
    exercise_id = create_response.json()["id"]

    exercise = authenticated_api_client.get(f"/exercises/{exercise_id}")

    assert exercise.status_code == 200
    expected_exercise_json = {"id": exercise_id, **new_exercise}
    assert exercise.json() == expected_exercise_json

    updated_exercise_list = authenticated_api_client.get("/exercises")

    assert updated_exercise_list.status_code == 200
    assert updated_exercise_list.json() == [expected_exercise_json]
