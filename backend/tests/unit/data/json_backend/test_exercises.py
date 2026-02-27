import pytest

from pilates.data.json_backend import _unit_of_work
from pilates.domain import exercises
from testing.helpers import exercises as exercise_helpers


class TestCreateExercise:
    def test_creates_exercise_with_given_parameters(
        self, uow: _unit_of_work.JSONUnitOfWork
    ):
        lesson_plan_id = uow.exercises.create_exercise(
            name="Hundred",
            description="Classic Pilates breathing exercise",
            category=exercises.ExerciseCategory.BREATH_WORK,
            difficulty=exercises.Difficulty.BEGINNER,
            primary_muscle_group=exercises.MuscleGroup.CORE,
            starting_position=exercises.StartingPosition.SUPINE,
            movement_variants=[exercises.MovementVariant.STANDARD],
            equipment_variants=[],
        )

        assert lesson_plan_id == 1


class TestGetExercises:
    def test_returns_all_created_exercises(self, uow: _unit_of_work.JSONUnitOfWork):
        exercise_helpers.Exercise.insert(uow, name="Hundred")
        exercise_helpers.Exercise.insert(uow, name="Roll Up")

        exercises = uow.exercises.get_exercises()

        assert len(exercises) == 2
        assert exercises[0].name == "Hundred"
        assert exercises[1].name == "Roll Up"


class TestGetExercise:
    def test_returns_exercise_with_matching_id(self, uow: _unit_of_work.JSONUnitOfWork):
        exercise = exercise_helpers.Exercise.insert(
            uow, name="Plank", description="Core stability exercise"
        )

        result = uow.exercises.get_exercise(exercise.id)

        assert result.id == exercise.id
        assert result.name == "Plank"
        assert result.description == "Core stability exercise"

    def test_raises_exception_when_exercise_does_not_exist(
        self, uow: _unit_of_work.JSONUnitOfWork
    ):
        with pytest.raises(exercises.ExerciseDoesNotExist) as exc_info:
            uow.exercises.get_exercise(999)

        assert exc_info.value.exercise_id == 999
