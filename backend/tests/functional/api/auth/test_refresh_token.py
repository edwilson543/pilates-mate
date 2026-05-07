import datetime as dt

import time_machine

from pilates.domain import utils
from testing.helpers import users as user_helpers


# Time is frozen so that the encoded JWTs are static.
CURRENT_TIME = dt.datetime(2026, 5, 2, tzinfo=utils.timezone())


@time_machine.travel(CURRENT_TIME, tick=False)
def test_can_retrieve_new_access_token_using_refresh_token(api_client, unit_of_work):
    email = "ed@gmail.com"
    password = "qwerty123"
    user = user_helpers.User.insert(unit_of_work, email=email, password=password)

    login_payload = {"username": user.email, "password": password}
    # Note we use `data` not `json`, since the credentials must be form encoded.
    login_response = api_client.post("/auth/token", data=login_payload)

    assert login_response.status_code == 200

    # The refresh token is stored as an HttpOnly cookie; the API client's automatically includes
    # its cookies in the subsequent refresh request.
    refresh_response = api_client.post("/auth/token/refresh")

    assert refresh_response.status_code == 200
    assert refresh_response.json() == {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlZEBnbWFpbC5jb20iLCJleHAiOjE3Nzc2ODE4MDAuMCwidG9rZW5fdHlwZSI6IkFDQ0VTUyJ9.TCHPoMIFx8oYvdozZq_RK89Et7qrbrcU1gh-lj6taic",
        "token_type": "bearer",
    }


def test_not_authorized_when_no_refresh_token_cookie_provided(api_client):
    response = api_client.post("/auth/token/refresh")

    assert response.status_code == 401
    assert response.json() == {"detail": "No refresh token provided."}


def test_not_authorized_when_invalid_refresh_token_provided(api_client):
    api_client.cookies.set("refresh_token", "fake-token", path="/auth/token/refresh")
    response = api_client.post("/auth/token/refresh")

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid refresh token."}


@time_machine.travel(CURRENT_TIME, tick=False)
def test_not_authorized_when_refresh_token_has_expired(api_client, unit_of_work):
    email = "ed@gmail.com"
    password = "qwerty123"
    user = user_helpers.User.insert(unit_of_work, email=email, password=password)

    login_payload = {"username": user.email, "password": password}
    login_response = api_client.post("/auth/token", data=login_payload)

    assert login_response.status_code == 200
    refresh_token = login_response.cookies["refresh_token"]

    token_expires_in = api_client.app_settings.auth_refresh_token_expiry_minutes
    after_token_expires = CURRENT_TIME + dt.timedelta(minutes=token_expires_in + 60)
    with time_machine.travel(after_token_expires):
        # Re-set the cookie manually: the API client's cookie jar drops max_age cookies
        # when time_machine advances past their expiry, so we inject it directly.
        api_client.cookies.set(
            "refresh_token", refresh_token, path="/auth/token/refresh"
        )
        refresh_response = api_client.post("/auth/token/refresh")

    assert refresh_response.status_code == 401
    assert refresh_response.json() == {"detail": "Refresh token has expired."}
