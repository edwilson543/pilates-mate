import contextlib
import typing
from unittest import mock

from pilates.domain import lesson_plans


@contextlib.contextmanager
def inject_repository(
    repo: lesson_plans.Repository,
) -> typing.Generator[None, None, None]:
    with mock.patch("pilates.config.get_lesson_plans_repository", return_value=repo):
        yield
