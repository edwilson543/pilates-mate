import contextlib
import typing
from unittest import mock

from pilates.domain import unit_of_work


@contextlib.contextmanager
def inject_uow(
    uow: unit_of_work.UnitOfWork,
) -> typing.Generator[None, None, None]:
    with mock.patch("pilates.config.get_unit_of_work", return_value=uow):
        yield
