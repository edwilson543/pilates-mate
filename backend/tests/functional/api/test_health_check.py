def test_health_check_returns_response_ok(api_client):
    response = api_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"version": "0.0.0"}
