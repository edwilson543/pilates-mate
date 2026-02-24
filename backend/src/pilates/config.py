from pilates.data import json_repositories
from pilates.domain import lesson_plans, vendors


def get_completion_client() -> vendors.CompletionClient:
    return vendors.OpenAICompletionClient(model="gpt-5-mini")


def get_lesson_plans_repository() -> lesson_plans.Repository:
    return json_repositories.JSONRepository()
