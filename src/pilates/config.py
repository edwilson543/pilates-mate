from pilates.data import json_repositories
from pilates.domain import lesson_planning, vendors


def get_completion_client() -> vendors.CompletionClient:
    return vendors.OpenAICompletionClient(model="gpt-5-mini")


def get_lesson_planning_repository() -> lesson_planning.Repository:
    return json_repositories.JSONRepository()
