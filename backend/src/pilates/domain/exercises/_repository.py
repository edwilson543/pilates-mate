import abc

import attrs

from . import _models


@attrs.frozen
class ExerciseDoesNotExist(Exception):
    exercise_id: int


class Repository(abc.ABC):
    @abc.abstractmethod
    def create_exercise(
        self,
        *,
        name: str,
        description: str,
        category: _models.ExerciseCategory,
        difficulty: _models.Difficulty,
        primary_muscle_group: _models.MuscleGroup,
        starting_position: _models.StartingPosition,
        movement_variants: list[_models.MovementVariant],
        equipment_variants: list[_models.Equipment],
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
        category: _models.ExerciseCategory,
        difficulty: _models.Difficulty,
        primary_muscle_group: _models.MuscleGroup,
        starting_position: _models.StartingPosition,
        movement_variants: list[_models.MovementVariant],
        equipment_variants: list[_models.Equipment],
    ) -> None:
        raise NotImplementedError
