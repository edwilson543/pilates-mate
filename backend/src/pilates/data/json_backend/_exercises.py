import pathlib

import attrs

from pilates.domain import exercises

from . import _mixins


@attrs.frozen
class JSONRepository(exercises.Repository, _mixins.JSONRepositoryMixin):
    database_file: pathlib.Path

    def create_exercise(
        self,
        *,
        name: str,
        description: str,
        category: exercises.ExerciseCategory,
        difficulty: exercises.Difficulty,
        primary_muscle_group: exercises.MuscleGroup,
        starting_position: exercises.StartingPosition,
        movement_variants: list[exercises.MovementVariant],
        equipment_variants: list[exercises.Equipment],
    ) -> int:
        data = self._read_database()

        next_id = max((exercise["id"] for exercise in data["exercises"]), default=0) + 1
        new_exercise = exercises.Exercise(
            id=next_id,
            name=name,
            description=description,
            category=category,
            difficulty=difficulty,
            primary_muscle_group=primary_muscle_group,
            starting_position=starting_position,
            movement_variants=movement_variants,
            equipment_variants=equipment_variants,
        )
        data["exercises"].append(new_exercise.model_dump())

        self._write_database(data)
        return next_id

    def get_exercises(self) -> list[exercises.Exercise]:
        data = self._read_database()
        return [
            exercises.Exercise.model_validate(exercise)
            for exercise in data["exercises"]
        ]

    def get_exercise(self, exercise_id: int) -> exercises.Exercise:
        for exercise in self.get_exercises():
            if exercise.id == exercise_id:
                return exercise
        raise exercises.ExerciseDoesNotExist(exercise_id=exercise_id)

    def update_exercise(
        self,
        *,
        id: int,
        name: str,
        description: str,
        category: exercises.ExerciseCategory,
        difficulty: exercises.Difficulty,
        primary_muscle_group: exercises.MuscleGroup,
        starting_position: exercises.StartingPosition,
        movement_variants: list[exercises.MovementVariant],
        equipment_variants: list[exercises.Equipment],
    ) -> None:
        data = self._read_database()

        # Find exercise index
        exercise_index = None
        for idx, exercise in enumerate(data["exercises"]):
            if exercise["id"] == id:
                exercise_index = idx
                break

        if exercise_index is None:
            raise exercises.ExerciseDoesNotExist(exercise_id=id)

        # Create updated exercise
        updated_exercise = exercises.Exercise(
            id=id,
            name=name,
            category=category,
            description=description,
            difficulty=difficulty,
            primary_muscle_group=primary_muscle_group,
            starting_position=starting_position,
            movement_variants=movement_variants,
            equipment_variants=equipment_variants,
        )

        # Update in exercises array
        data["exercises"][exercise_index] = updated_exercise.model_dump()

        self._write_database(data)
