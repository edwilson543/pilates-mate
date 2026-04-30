import typing

import fastapi

from pilates import config


def get_settings(request: fastapi.Request) -> config.Settings:
    return request.app.state.settings


SettingsT = typing.Annotated[config.Settings, fastapi.Depends(get_settings)]
