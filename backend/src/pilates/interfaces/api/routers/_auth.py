import typing

import fastapi
import pydantic
from fastapi import security

from pilates import config
from pilates.domain import users
from pilates.interfaces.api import dependencies, errors


router = fastapi.APIRouter()


class TokenResponse(pydantic.BaseModel):
    access_token: str
    token_type: str


@router.post("/token")
async def login(
    settings: dependencies.SettingsT,
    credentials: typing.Annotated[
        security.OAuth2PasswordRequestForm, fastapi.Depends()
    ],
) -> TokenResponse:
    auth_service = config.get_auth_service(settings=settings)

    try:
        token = auth_service.get_token_if_password_valid(
            email=credentials.username, password=credentials.password
        )
    except users.InvalidCredentials as exc:
        raise errors.not_authorized_error("Invalid username or password.") from exc

    return TokenResponse(access_token=token, token_type="bearer")


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
