from pilates.data import json_backend
from pilates.domain import lesson_plans, unit_of_work, vendors


def get_completion_client() -> vendors.CompletionClient:
    return vendors.OpenAICompletionClient(model="gpt-5-mini")


def get_unit_of_work() -> unit_of_work.UnitOfWork:
    return json_backend.JSONUnitOfWork()


def get_evaluation_deps() -> lesson_plans.EvaluationDeps:
    uow = get_unit_of_work()
    return lesson_plans.EvaluationDeps(
        lesson_plan_repo=uow.lesson_plans, exercises_repo=uow.exercises
    )
