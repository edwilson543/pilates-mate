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


@attrs.frozen
class SequenceDoesNotExist(Exception):
    sequence_id: int


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
        variants: list[_models.ExerciseVariant],
    ) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def get_exercises(self) -> list[_models.Exercise]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_exercise(self, exercise_id: int) -> _models.Exercise:
        raise NotImplementedError

    @abc.abstractmethod
    def update_exercise(
        self,
        *,
        id: int,
        name: str,
        description: str,
        difficulty: _models.Difficulty,
        primary_muscle_group: _models.MuscleGroup,
        starting_position: _models.StartingPosition,
        variants: list[_models.ExerciseVariant],
    ) -> None:
        raise NotImplementedError

    # Lesson plans.

    @abc.abstractmethod
    def create_lesson_plan(
        self,
        *,
        name: str,
        description: str,
        date: dt.date,
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

    @abc.abstractmethod
    def add_sequence_to_section(
        self,
        *,
        lesson_plan_id: int,
        section: _models.LessonPlanSection,
        name: str,
        reps: int,
        notes: str,
    ) -> int:
        """Add sequence to section. Returns sequence_id."""
        raise NotImplementedError

    @abc.abstractmethod
    def add_set_to_sequence(
        self,
        *,
        sequence_id: int,
        exercise_id: int,
        reps: int,
        duration_seconds: int,
        variant: _models.ExerciseVariant,
    ) -> int:
        """Add set to sequence. Returns set_id."""
        raise NotImplementedError
