def test_response_not_found_when_exercise_does_not_exist(api_client):
    response = api_client.get("/exercises/123")

    assert response.status_code == 404
    assert response.json() == {"detail": "Exercise not found."}
