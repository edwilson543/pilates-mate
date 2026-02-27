import contextlib
import typing

from pilates.domain import exercises, lesson_plans


class UnitOfWork:
    exercises: exercises.Repository
    lesson_plans: lesson_plans.Repository

    @contextlib.asynccontextmanager
    async def transaction(self) -> typing.AsyncIterator[None]:
        yield
