import attrs

from pilates.domain import exercises


@attrs.mutable(kw_only=True)
class FakeRepository(exercises.Repository):
    _exercises: list[exercises.Exercise] = attrs.field(factory=list)

    _next_sequence_id: int = attrs.field(init=False)
    _next_set_id: int = attrs.field(init=False)

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
        next_id = len(self._exercises) + 1

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
        self._exercises.append(new_exercise)

        return next_id

    def get_exercises(self) -> list[exercises.Exercise]:
        return self._exercises.copy()

    def get_exercise(self, exercise_id: int) -> exercises.Exercise:
        for exercise in self._exercises:
            if exercise.id == exercise_id:
                return exercise
        raise exercises.ExerciseDoesNotExist(exercise_id=exercise_id)

    def update_exercise(
        self,
        *,
        id: int,
        name: str,
        category: exercises.ExerciseCategory,
        description: str,
        difficulty: exercises.Difficulty,
        primary_muscle_group: exercises.MuscleGroup,
        starting_position: exercises.StartingPosition,
        movement_variants: list[exercises.MovementVariant],
        equipment_variants: list[exercises.Equipment],
    ) -> None:
        def _update(exercise_: exercises.Exercise) -> None:
            exercise_.name = name
            exercise_.description = description
            exercise_.category = category
            exercise_.difficulty = difficulty
            exercise_.primary_muscle_group = primary_muscle_group
            exercise_.starting_position = starting_position
            exercise_.movement_variants = movement_variants
            exercise_.equipment_variants = equipment_variants

        for exercise in self._exercises:
            if exercise.id == id:
                _update(exercise)

                return None

        raise exercises.ExerciseDoesNotExist(exercise_id=id)
