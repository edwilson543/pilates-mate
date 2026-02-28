from pilates.data import json_backend
from pilates.domain import unit_of_work, vendors


def get_completion_client() -> vendors.CompletionClient:
    return vendors.OpenAICompletionClient(model="gpt-5-mini")


def get_unit_of_work() -> unit_of_work.UnitOfWork:
    return json_backend.JSONUnitOfWork()
