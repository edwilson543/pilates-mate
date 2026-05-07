import typing

import fastapi
import pydantic
from fastapi import security

from pilates.domain import users
from pilates.interfaces.api import dependencies, errors


router = fastapi.APIRouter()


class TokenResponse(pydantic.BaseModel):
    access_token: str
    token_type: str


@router.post("/token")
async def login(
    auth_service: dependencies.AuthServiceT,
    settings: dependencies.SettingsT,
    response: fastapi.Response,
    credentials: typing.Annotated[
        security.OAuth2PasswordRequestForm, fastapi.Depends()
    ],
) -> TokenResponse:
    try:
        tokens = auth_service.issue_access_and_refresh_token_from_credentials(
            email=credentials.username, password=credentials.password
        )
    except users.InvalidCredentials as exc:
        raise errors.not_authorized_error("Invalid username or password.") from exc

    _set_refresh_token_cookie(
        response,
        tokens.refresh_token,
        secure=settings.auth_cookie_secure,
        max_age_seconds=settings.auth_refresh_token_expiry_minutes * 60,
    )
    return TokenResponse(access_token=tokens.access_token, token_type="bearer")


@router.post("/token/refresh")
async def refresh_access_token(
    auth_service: dependencies.AuthServiceT,
    settings: dependencies.SettingsT,
    response: fastapi.Response,
    refresh_token: typing.Annotated[str | None, fastapi.Cookie()] = None,
) -> TokenResponse:
    if refresh_token is None:
        raise errors.not_authorized_error("No refresh token provided.")

    try:
        access_token = auth_service.issue_access_token_from_refresh_token(
            refresh_token=refresh_token
        )
    except users.TokenExpired as exc:
        raise errors.not_authorized_error("Refresh token has expired.") from exc
    except users.InvalidToken as exc:
        raise errors.not_authorized_error("Invalid refresh token.") from exc

    _set_refresh_token_cookie(
        response,
        refresh_token,
        secure=settings.auth_cookie_secure,
        max_age_seconds=settings.auth_refresh_token_expiry_minutes * 60,
    )
    return TokenResponse(access_token=access_token, token_type="bearer")


class UserResponse(pydantic.BaseModel):
    full_name: str
    email: str


@router.get("/user")
async def get_authenticated_user_details(
    user: dependencies.UserT,
) -> UserResponse:
    return UserResponse(full_name=user.full_name, email=user.email)


def _set_refresh_token_cookie(
    response: fastapi.Response,
    refresh_token: str,
    *,
    secure: bool,
    max_age_seconds: int,
) -> None:
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=secure,
        max_age=max_age_seconds,
        path="/auth/token/refresh",
    )
