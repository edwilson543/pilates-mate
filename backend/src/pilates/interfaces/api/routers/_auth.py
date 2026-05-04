import typing

import fastapi
import pydantic
from fastapi import security

from pilates.domain import users
from pilates.interfaces.api import dependencies, errors


router = fastapi.APIRouter()


class TokenResponse(pydantic.BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


@router.post("/token")
async def login(
    auth_service: dependencies.AuthServiceT,
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

    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type="bearer",
    )


@router.post("/token/refresh")
async def refresh_access_token(
    auth_service: dependencies.AuthServiceT,
    refresh_token: typing.Annotated[str, fastapi.Body(embed=True)],
) -> TokenResponse:
    try:
        access_token = auth_service.issue_access_token_from_refresh_token(
            refresh_token=refresh_token
        )
    except users.TokenExpired as exc:
        raise errors.not_authorized_error("Refresh token has expired.") from exc
    except users.InvalidToken as exc:
        raise errors.not_authorized_error("Invalid refresh token.") from exc

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


# Items.
# TODO! delete all this once other routes are authenticated...


class Item(pydantic.BaseModel):
    user_id: int
    details: str


ITEMS_DB = [
    Item(user_id=1, details="ed's item"),
    Item(user_id=2, details="libby's item"),
    Item(user_id=3, details="someone else's item"),
]


@router.get("/items")
async def read_items(user: dependencies.UserT) -> list[Item]:
    return [item for item in ITEMS_DB if item.user_id == user.id]
