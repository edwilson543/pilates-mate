import pathlib

import pydantic_settings

from pilates.data import json_backend
from pilates.domain import lesson_plans, unit_of_work, users, vendors


class Settings(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )

    openai_api_key: str = ""
    model: str = "gpt-5-mini"

    # Auth.
    auth_secret_key: str = ""
    auth_jwt_algorithm: str = "HS256"
    auth_access_token_expiry_minutes: int = 30
    auth_refresh_token_expiry_minutes: int = 60 * 24 * 7  # 1 week.

    # Persistence.
    json_database_file: str = ""


def get_auth_service(settings: Settings) -> users.AuthService:
    uow = get_unit_of_work(settings)
    return users.JWTAuthService(
        repo=uow.users,
        secret_key=settings.auth_secret_key,
        algorithm=settings.auth_jwt_algorithm,
        access_token_expiry_minutes=settings.auth_access_token_expiry_minutes,
        refresh_token_expiry_minutes=settings.auth_refresh_token_expiry_minutes,
    )


def get_completion_client(settings: Settings) -> vendors.CompletionClient:
    return vendors.OpenAICompletionClient(
        api_key=settings.openai_api_key, model=settings.model
    )


def get_unit_of_work(settings: Settings) -> unit_of_work.UnitOfWork:
    database_file = pathlib.Path(settings.json_database_file)
    return json_backend.JSONUnitOfWork(database_file=database_file)


def get_evaluation_deps(settings: Settings) -> lesson_plans.EvaluationDeps:
    uow = get_unit_of_work(settings)
    return lesson_plans.EvaluationDeps(
        completions_client=get_completion_client(settings),
        lesson_plan_repo=uow.lesson_plans,
        exercises_repo=uow.exercises,
    )
