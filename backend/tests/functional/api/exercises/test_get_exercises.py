from testing.helpers import exercises as exercise_helpers


def test_retrieves_exercise_details_when_exists(authenticated_api_client, unit_of_work):
    exercise = exercise_helpers.Exercise.insert(unit_of_work)

    response = authenticated_api_client.get(f"/exercises/{exercise.id}")

    assert response.status_code == 200
    assert response.json()["id"] == exercise.id
    assert response.json()["name"] == exercise.name


def test_response_not_found_when_exercise_does_not_exist(authenticated_api_client):
    response = authenticated_api_client.get("/exercises/123")

    assert response.status_code == 404
    assert response.json() == {"detail": "Exercise not found."}
