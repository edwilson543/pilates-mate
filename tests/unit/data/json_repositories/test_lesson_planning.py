import pathlib

import pytest

from pilates.data.json_repositories import _lesson_planning
from pilates.domain import lesson_planning
from testing.helpers import lesson_planning as lesson_planning_helpers


class TestCreateExercise:
    def test_creates_exercise_with_given_parameters(self, tmp_path: pathlib.Path):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )

        lesson_plan_id = repository.create_exercise(
            name="Hundred",
            description="Classic Pilates breathing exercise",
            difficulty=lesson_planning.Difficulty.BEGINNER,
            primary_muscle_group=lesson_planning.MuscleGroup.CORE,
            starting_position=lesson_planning.StartingPosition.SUPINE,
        )

        assert lesson_plan_id == 1


class TestGetExercises:
    def test_returns_all_created_exercises(self, tmp_path: pathlib.Path):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )
        repository.create_exercise(
            name="Hundred",
            description="Classic Pilates breathing exercise",
            difficulty=lesson_planning.Difficulty.BEGINNER,
            primary_muscle_group=lesson_planning.MuscleGroup.CORE,
            starting_position=lesson_planning.StartingPosition.SUPINE,
        )
        repository.create_exercise(
            name="Roll Up",
            description="Spinal articulation exercise",
            difficulty=lesson_planning.Difficulty.INTERMEDIATE,
            primary_muscle_group=lesson_planning.MuscleGroup.CORE,
            starting_position=lesson_planning.StartingPosition.SUPINE,
        )

        exercises = repository.get_exercises()

        assert len(exercises) == 2
        assert exercises[0].name == "Hundred"
        assert exercises[1].name == "Roll Up"


class TestGetExercise:
    def test_returns_exercise_with_matching_id(self, tmp_path: pathlib.Path):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )
        exercise_id = repository.create_exercise(
            name="Plank",
            description="Core stability exercise",
            difficulty=lesson_planning.Difficulty.INTERMEDIATE,
            primary_muscle_group=lesson_planning.MuscleGroup.CORE,
            starting_position=lesson_planning.StartingPosition.PRONE,
        )

        exercise = repository.get_exercise(exercise_id)

        assert exercise.id == exercise_id
        assert exercise.name == "Plank"
        assert exercise.description == "Core stability exercise"

    def test_raises_exception_when_exercise_does_not_exist(
        self, tmp_path: pathlib.Path
    ):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )

        with pytest.raises(lesson_planning.ExerciseDoesNotExist) as exc_info:
            repository.get_exercise(999)

        assert exc_info.value.exercise_id == 999


class TestCreateLessonPlan:
    def test_returns_lesson_plan_id(self, tmp_path: pathlib.Path):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )

        lesson_plan_id = repository.create_lesson_plan(
            name="Beginner Flow",
            description="A gentle introduction to Pilates",
            warm_up=[lesson_planning_helpers.ExerciseSequence()],  # type: ignore[list-item]
            main_session=[],
            cool_down=[],
        )

        assert lesson_plan_id == 1


class TestGetLessonPlans:
    def test_returns_all_created_lesson_plans(self, tmp_path: pathlib.Path):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )
        repository.create_lesson_plan(
            name="Beginner Flow",
            description="A gentle introduction to Pilates",
            warm_up=[lesson_planning_helpers.ExerciseSequence()],  # type: ignore[list-item]
            main_session=[],
            cool_down=[],
        )
        repository.create_lesson_plan(
            name="Advanced Flow",
            description="An intense Pilates session",
            warm_up=[],
            main_session=[lesson_planning_helpers.ExerciseSequence()],  # type: ignore[list-item]
            cool_down=[],
        )

        lesson_plans = repository.get_lesson_plans()

        assert len(lesson_plans) == 2
        assert lesson_plans[0].name == "Beginner Flow"
        assert lesson_plans[1].name == "Advanced Flow"


class TestGetLessonPlan:
    def test_returns_lesson_plan_with_matching_id(self, tmp_path: pathlib.Path):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )

        lesson_plan_id = repository.create_lesson_plan(
            name="Beginner Flow",
            description="A gentle introduction to Pilates",
            warm_up=[lesson_planning_helpers.ExerciseSequence()],  # type: ignore[list-item]
            main_session=[],
            cool_down=[],
        )

        lesson_plan = repository.get_lesson_plan(lesson_plan_id)

        assert lesson_plan.id == lesson_plan_id
        assert lesson_plan.name == "Beginner Flow"
        assert lesson_plan.description == "A gentle introduction to Pilates"
        assert len(lesson_plan.warm_up) == 1

    def test_raises_exception_when_lesson_plan_does_not_exist(
        self, tmp_path: pathlib.Path
    ):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )

        with pytest.raises(lesson_planning.LessonPlanDoesNotExist) as exc_info:
            repository.get_lesson_plan(999)

        assert exc_info.value.lesson_plan_id == 999
