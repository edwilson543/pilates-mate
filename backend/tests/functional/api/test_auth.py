import datetime as dt

import pytest
import time_machine

from pilates.interfaces.api.routers import _auth


# Time is frozen so that the encoded JWTs are static.
CURRENT_TIME = dt.datetime(2026, 5, 2)


@time_machine.travel(CURRENT_TIME)
def test_registered_user_can_login_to_obtain_token(api_client):
    payload = {"username": "ed@gmail.com", "password": "qwerty123"}

    # Note we use `data` not `json`, since the credentials must be form encoded.
    login_response = api_client.post("/auth/token", data=payload)

    assert login_response.status_code == 200
    assert login_response.json() == {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlZEBnbWFpbC5jb20iLCJleHAiOjE3Nzc2ODE4MDAuMH0.X50tWnjq40WJnMOVCSGVriKsa3GAkkEiWTxSqBHbbSM",
        "token_type": "bearer",
    }

    # TODO! this is just temporary to test an authenticated route
    auth_token = login_response.json()["access_token"]
    api_client.set_auth_token(auth_token)

    items_response = api_client.get("/auth/items")

    assert items_response.status_code == 200
    assert items_response.json() == [{"user_id": 1, "details": "ed's item"}]


@pytest.mark.parametrize(
    "username,password",
    [
        pytest.param("ed@gmail.com", "invalid-password", id="invalid-password"),
        pytest.param("invalid@gmail.com", "invalid", id="unregistered-email"),
    ],
)
def test_not_authorized_when_invalid_password_provided(
    api_client, username: str, password: str
):
    payload = {"username": username, "password": password}

    response = api_client.post("auth/token", data=payload)

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid username or password."}


@time_machine.travel(CURRENT_TIME)
def test_not_authorized_when_token_has_expired(api_client):
    payload = {"username": "ed@gmail.com", "password": "qwerty123"}

    # Note we use `data` not `json`, since the credentials must be form encoded.
    login_response = api_client.post("/auth/token", data=payload)

    assert login_response.status_code == 200
    assert login_response.json() == {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlZEBnbWFpbC5jb20iLCJleHAiOjE3Nzc2ODE4MDAuMH0.X50tWnjq40WJnMOVCSGVriKsa3GAkkEiWTxSqBHbbSM",
        "token_type": "bearer",
    }

    auth_token = login_response.json()["access_token"]
    api_client.set_auth_token(auth_token)

    post_expiry = CURRENT_TIME + dt.timedelta(minutes=_auth.JWT_EXPIRY_MINUTES + 30)
    with time_machine.travel(post_expiry):
        items_response = api_client.get("/auth/items")

    assert items_response.status_code == 401
    assert items_response.json() == {"detail": "Token expired."}
