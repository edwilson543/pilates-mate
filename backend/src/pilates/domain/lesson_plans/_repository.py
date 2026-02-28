import abc
import datetime as dt

import attrs

from pilates.domain import exercises

from . import _models


@attrs.frozen
class LessonPlanDoesNotExist(Exception):
    lesson_plan_id: int


@attrs.frozen
class SequenceDoesNotExist(Exception):
    sequence_id: int


@attrs.frozen
class SetDoesNotExist(Exception):
    set_id: int


class Repository(abc.ABC):
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
        movement_variant: exercises.MovementVariant,
        equipment_variant: list[exercises.Equipment],
    ) -> int:
        """Add set to sequence. Returns set_id."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_exercise_set(self, set_id: int) -> _models.ExerciseSet:
        """Get a single exercise set by ID across all lesson plans."""
        raise NotImplementedError

    @abc.abstractmethod
    def update_exercise_set(
        self,
        *,
        id: int,
        reps: int,
        duration_seconds: int,
        movement_variant: exercises.MovementVariant,
        equipment_variant: list[exercises.Equipment],
    ) -> None:
        """Update set properties. Does not change exercise reference."""
        raise NotImplementedError

    @abc.abstractmethod
    def delete_exercise_set(self, set_id: int) -> None:
        """Delete set from its sequence."""
        raise NotImplementedError

    @abc.abstractmethod
    def update_exercise_sequence(
        self,
        *,
        id: int,
        name: str,
        reps: int,
        notes: str,
    ) -> None:
        """Update sequence metadata. Does not affect sets within sequence."""
        raise NotImplementedError

    @abc.abstractmethod
    def delete_exercise_sequence(self, sequence_id: int) -> None:
        """Delete sequence and all sets within it."""
        raise NotImplementedError
