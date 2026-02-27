import contextlib
import typing

from pilates.domain import lesson_plans


class UnitOfWork:
    lesson_plans: lesson_plans.Repository

    @contextlib.asynccontextmanager
    async def transaction(self) -> typing.AsyncIterator[None]:
        yield
