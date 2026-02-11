import pathlib

from pilates.data.json_repositories import _lesson_planning
from pilates.domain import lesson_planning
from testing.helpers import lesson_planning as lesson_planning_helpers


class TestCreateExercise:
    def test_returns_all_exercises_after_creation(self, tmp_path: pathlib.Path):
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

        exercise_id = repository.create_exercise(
            name="Plank",
            description="Core stability exercise",
            difficulty=lesson_planning.Difficulty.INTERMEDIATE,
            primary_muscle_group=lesson_planning.MuscleGroup.CORE,
            starting_position=lesson_planning.StartingPosition.PRONE,
        )

        assert exercise_id == 3


class TestCreateLessonPlan:
    def test_creates_then_gets_lesson_plan(self, tmp_path: pathlib.Path):
        repository = _lesson_planning.JSONRepository(
            database_file=tmp_path / "test.json"
        )
        warm_up = [lesson_planning_helpers.ExerciseSequence()]

        lesson_plan_id = repository.create_lesson_plan(
            name="Beginner Flow",
            description="A gentle introduction to Pilates",
            warm_up=warm_up,
            main_session=[],
            cool_down=[],
        )

        assert lesson_plan_id == 1

        lesson_plans = repository.get_lesson_plans()

        assert len(lesson_plans) == 1
        assert lesson_plans[0].name == "Beginner Flow"
        assert lesson_plans[0].description == "A gentle introduction to Pilates"
        assert lesson_plans[0].warm_up == warm_up
