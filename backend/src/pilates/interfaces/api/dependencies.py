import typing

import fastapi
from fastapi import security

from pilates import config
from pilates.domain import unit_of_work, users
from pilates.interfaces.api import errors


def _get_settings(request: fastapi.Request) -> config.Settings:
    return request.app.state.settings


SettingsT = typing.Annotated[config.Settings, fastapi.Depends(_get_settings)]


def _get_unit_of_work(settings: SettingsT) -> unit_of_work.UnitOfWork:
    return config.get_unit_of_work(settings)


UnitOfWorkT = typing.Annotated[
    unit_of_work.UnitOfWork, fastapi.Depends(_get_unit_of_work)
]


_oauth2_scheme = security.OAuth2PasswordBearer(tokenUrl="auth/token")


async def _get_current_user(
    settings: SettingsT,
    uow: UnitOfWorkT,
    token: typing.Annotated[str, fastapi.Depends(_oauth2_scheme)],
) -> users.User:
    auth_service = config.get_auth_service(settings=settings, uow=uow)
    try:
        user = auth_service.get_user_if_access_token_is_valid(token=token)
    except users.TokenExpired as exc:
        raise errors.not_authorized_error("Token expired.") from exc
    except users.InvalidToken as exc:
        raise errors.not_authorized_error("Invalid token.") from exc

    return user


UserDep = fastapi.Depends(_get_current_user)
UserT = typing.Annotated[users.User, UserDep]


async def _get_auth_service(settings: SettingsT, uow: UnitOfWorkT) -> users.AuthService:
    return config.get_auth_service(settings=settings, uow=uow)


AuthServiceT = typing.Annotated[users.AuthService, fastapi.Depends(_get_auth_service)]
