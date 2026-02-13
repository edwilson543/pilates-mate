import abc
import datetime as dt

import attrs

from . import _models


@attrs.frozen
class ExerciseDoesNotExist(Exception):
    exercise_id: int


@attrs.frozen
class LessonPlanDoesNotExist(Exception):
    lesson_plan_id: int


class Repository(abc.ABC):
    # Exercises.

    @abc.abstractmethod
    def create_exercise(
        self,
        *,
        name: str,
        description: str,
        difficulty: _models.Difficulty,
        primary_muscle_group: _models.MuscleGroup,
        starting_position: _models.StartingPosition,
    ) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def get_exercises(self) -> list[_models.Exercise]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_exercise(self, exercise_id: int) -> _models.Exercise:
        raise NotImplementedError

    # Lesson plans.

    @abc.abstractmethod
    def create_lesson_plan(
        self,
        *,
        name: str,
        description: str,
        date: dt.date,
        warm_up: list[_models.ExerciseSequence],
        main_session: list[_models.ExerciseSequence],
        cool_down: list[_models.ExerciseSequence],
    ) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def get_lesson_plans(self) -> list[_models.LessonPlan]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_lesson_plan(self, lesson_plan_id: int) -> _models.LessonPlan:
        raise NotImplementedError

    @abc.abstractmethod
    def delete_lesson_plan(self, lesson_plan_id: int) -> None:
        raise NotImplementedError
