import contextlib
import typing
from unittest import mock

from pilates.domain import lesson_planning


@contextlib.contextmanager
def inject_repository(
    repo: lesson_planning.Repository,
) -> typing.Generator[None, None, None]:
    with mock.patch("pilates.config.get_lesson_planning_repository", return_value=repo):
        yield
