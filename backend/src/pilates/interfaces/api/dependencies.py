import typing

import fastapi
from fastapi import security

from pilates import config
from pilates.domain import unit_of_work, users
from pilates.interfaces.api import errors


def get_settings(request: fastapi.Request) -> config.Settings:
    return request.app.state.settings


SettingsT = typing.Annotated[config.Settings, fastapi.Depends(get_settings)]


def get_unit_of_work(settings: SettingsT) -> unit_of_work.UnitOfWork:
    return config.get_unit_of_work(settings)


UnitOfWorkT = typing.Annotated[
    unit_of_work.UnitOfWork, fastapi.Depends(get_unit_of_work)
]


oauth2_scheme = security.OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_current_user(
    settings: SettingsT,
    token: typing.Annotated[str, fastapi.Depends(oauth2_scheme)],
) -> users.User:
    auth_service = config.get_auth_service(settings=settings)
    try:
        user = auth_service.get_user_if_token_valid(token=token)
    except users.TokenExpired as exc:
        raise errors.not_authorized_error("Token expired.") from exc
    except users.InvalidToken as exc:
        raise errors.not_authorized_error("Invalid token.") from exc

    return user


UserT = typing.Annotated[users.User, fastapi.Depends(get_current_user)]
