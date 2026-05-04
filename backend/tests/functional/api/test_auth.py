import datetime as dt

import time_machine

from pilates.domain import utils
from testing.helpers import users as user_helpers


# Time is frozen so that the encoded JWTs are static.
CURRENT_TIME = dt.datetime(2026, 5, 2, tzinfo=utils.timezone())


@time_machine.travel(CURRENT_TIME)
def test_registered_user_can_login_to_obtain_token(api_client, unit_of_work):
    email = "ed@gmail.com"
    password = "qwerty123"
    user = user_helpers.User.insert(unit_of_work, email=email, password=password)

    payload = {"username": user.email, "password": password}
    # Note we use `data` not `json`, since the credentials must be form encoded.
    login_response = api_client.post("/auth/token", data=payload)

    assert login_response.status_code == 200
    assert login_response.json() == {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlZEBnbWFpbC5jb20iLCJleHAiOjE3Nzc2ODE4MDAuMH0.99fvaIPannd45cq0je9XGG7O1iUG5LQ57x9hxTSVGzE",
        "token_type": "bearer",
    }

    # TODO! this is just temporary to test an authenticated route
    auth_token = login_response.json()["access_token"]
    api_client.set_auth_token(auth_token)

    items_response = api_client.get("/auth/items")

    assert items_response.status_code == 200
    assert items_response.json() == [{"user_id": user.id, "details": "ed's item"}]


def test_not_authorized_when_registered_user_provides_invalid_password(
    api_client, unit_of_work
):
    email = "ed@gmail.com"
    password = "qwerty123"
    user = user_helpers.User.insert(unit_of_work, email=email, password=password)

    payload = {"username": user.email, "password": "the-wrong-password"}

    response = api_client.post("auth/token", data=payload)

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid username or password."}


def test_not_authorized_when_unregistered_user_attempts_login(api_client, unit_of_work):
    payload = {"username": "fake@gmail.com", "password": "the-wrong-password"}

    response = api_client.post("auth/token", data=payload)

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid username or password."}


@time_machine.travel(CURRENT_TIME)
def test_not_authorized_when_token_has_expired(api_client, unit_of_work):
    email = "ed@gmail.com"
    password = "some-password"
    user = user_helpers.User.insert(unit_of_work, email=email, password=password)

    payload = {"username": user.email, "password": password}
    login_response = api_client.post("auth/token", data=payload)

    assert login_response.status_code == 200
    assert login_response.json() == {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlZEBnbWFpbC5jb20iLCJleHAiOjE3Nzc2ODE4MDAuMH0.99fvaIPannd45cq0je9XGG7O1iUG5LQ57x9hxTSVGzE",
        "token_type": "bearer",
    }

    auth_token = login_response.json()["access_token"]
    api_client.set_auth_token(auth_token)

    token_expires_in = api_client.app_settings.auth_jwt_expiry_minutes
    after_token_expires = CURRENT_TIME + dt.timedelta(minutes=token_expires_in + 30)
    with time_machine.travel(after_token_expires):
        items_response = api_client.get("/auth/items")

    assert items_response.status_code == 401
    assert items_response.json() == {"detail": "Token expired."}
